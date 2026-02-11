import gradio as gr
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Tuple, Optional
import time
from langsmith import traceable
from PIL import Image
import io
import base64
import uuid

# Make sure this is imported
from config import Config
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore
from src.llm_handler import LLMHandler
from src.vlm_handler import VLMHandler
from src.chunker import Chunker
from database import DatabaseRepository
from auth_service import AuthenticationService
from models import Conversation, UserStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing and chunking using smart chunker"""
    
    def __init__(self):
        """Initialize with Chunker instance"""
        self.chunker = Chunker()  # AJOUTER CETTE LIGNE si elle n'existe pas
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text using separator-based chunking ONLY.
        chunk_size and overlap are IGNORED (kept for compatibility).
        """
        return Chunker.chunk_text(text, chunk_size, overlap)
    
    @staticmethod
    def extract_sections(text: str) -> List[Dict[str, str]]:
        """Extract sections based on headers"""
        sections = []
        current_section = {"title": "Introduction", "content": ""}
        
        for line in text.split('\n'):
            if line.strip().startswith('#'):
                if current_section["content"].strip():
                    sections.append(current_section)
                title = line.strip().lstrip('#').strip()
                current_section = {"title": title, "content": ""}
            else:
                current_section["content"] += line + "\n"
        
        if current_section["content"].strip():
            sections.append(current_section)
        
        return sections

class ConversationSession:
    """Represents a single conversation session"""
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages = []
        self.created_at = datetime.now()
        self.title = "New Chat"
        self.last_updated = datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add a message to the session"""
        self.messages.append({"role": role, "content": content})
        self.last_updated = datetime.now()
        
        # Auto-generate title from first user message
        if role == "user" and self.title == "New Chat" and content.strip():
            self.title = content[:50] + "..." if len(content) > 50 else content
    
    def get_chat_history(self) -> List[Dict]:
        """Get messages in Gradio format"""
        return self.messages
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "message_count": len(self.messages)
        }

class ChatbotApp:
    """Main chatbot application with user authentication"""
    
    def __init__(self, db_repository: DatabaseRepository, auth_service: AuthenticationService):
        """Initialize chatbot components"""
        Config.validate()
        
        # Services
        self.db = db_repository
        self.auth = auth_service
        
        # Core components
        self.embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL)
        self.vector_store = VectorStore(Config.CHROMA_DB_PATH)
        self.llm_handler = LLMHandler(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
        self.vlm_handler = VLMHandler(Config.GROQ_API_KEY, Config.GROQ_VISION_MODEL) if Config.GROQ_API_KEY else None
        self.doc_processor = DocumentProcessor()
        
        # Session management
        self.active_sessions: Dict[int, Dict[str, ConversationSession]] = {}  # user_id -> {session_id -> session}
        
        if not self.vlm_handler:
            logger.warning("⚠️ Groq API key not configured. Image analysis feature will be disabled.")
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize or load vector database"""
        logger.info("Initializing vector database...")
        try:
            self.collection = self.vector_store.get_collection()
            logger.info("✅ Loaded existing database")
        except:
            logger.info("No existing database found. Creating new one...")
            self.load_documents()
    
    @traceable(name="load_and_index_documents")
    def load_documents(self) -> Tuple[bool, str]:
        """Load and index all documents with separator-based chunking."""
        try:
            logger.info(f"Loading documents from {Config.DOCS_FOLDER}...")
            self.collection = self.vector_store.create_collection(reset=True)
            
            docs_path = Path(Config.DOCS_FOLDER)
            md_files = list(docs_path.glob("*.md")) + list(docs_path.glob("*.txt"))
            
            if not md_files:
                return False, f"❌ No documents found in {Config.DOCS_FOLDER}"
            
            logger.info(f"Found {len(md_files)} document(s)")
            total_chunks = 0
            all_chunks = []
            all_metadatas = []
            skipped_docs = []
            
            for doc_file in md_files:
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing: {doc_file.name}")
                logger.info(f"{'='*60}")
                
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                logger.info(f"Content length: {len(content)} characters")
                
                # Validate document format
                validation = self.doc_processor.chunker.validate_document_format(content)
                logger.info(f"Validation: {validation['message']}")
                
                if not validation['valid']:
                    logger.error(
                        f"❌ Skipping {doc_file.name}: {validation['message']}\n"
                        f"Please ensure your document contains separator patterns (****)"
                    )
                    skipped_docs.append(doc_file.name)
                    continue
                
                # Extract sections
                sections = self.doc_processor.extract_sections(content)
                logger.info(f"Found {len(sections)} section(s)")
                
                for section in sections:
                    section_title = section["title"]
                    section_content = section["content"]
                    
                    if not section_content.strip():
                        logger.warning(f"Section '{section_title}' is empty, skipping")
                        continue
                    
                    # Chunk using separator-based chunking
                    chunks = self.doc_processor.chunk_text(section_content)
                    
                    if not chunks:
                        logger.error(f"❌ No chunks created for section '{section_title}'")
                        continue
                    
                    logger.info(f"Section '{section_title}': {len(chunks)} chunks created")
                    
                    for i, chunk in enumerate(chunks):
                        if not chunk.strip():
                            continue
                        
                        all_chunks.append(chunk)
                        metadata = Chunker.extract_metadata_from_chunk(
                            chunk, doc_file.stem, section_title, i
                        )
                        all_metadatas.append(metadata)
                        total_chunks += 1
            
            if not all_chunks:
                error_msg = (
                    f"❌ No chunks created!\n"
                    f"Processed {len(md_files)} files, skipped {len(skipped_docs)}.\n"
                    f"Please ensure documents contain separator patterns (****)."
                )
                logger.error(error_msg)
                return False, error_msg
            
            logger.info(f"✅ Created {total_chunks} total chunks")
            logger.info("Generating embeddings...")
            embeddings = self.embedding_manager.encode_batch(all_chunks)
            
            logger.info("Adding to vector store...")
            self.vector_store.add_documents(all_chunks, all_metadatas, embeddings)
            
            final_count = self.collection.count()
            message = f"✅ Successfully indexed {final_count} chunks from {len(md_files)} documents!"
            logger.info(message)
            
            return True, message
            
        except Exception as e:
            error_msg = f"❌ Error loading documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    @traceable(name="retrieve_relevant_chunks", run_type="retriever")
    def retrieve_relevant_chunks(self, message: str, top_k: int = None) -> Dict:
        """Retrieve relevant chunks with full tracing"""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        query_embedding = self.embedding_manager.encode(message)
        results = self.vector_store.query(query_embedding, top_k)
        
        if results['documents'] and results['documents'][0]:
            chunks_info = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0] if 'distances' in results else [None] * len(results['documents'][0])
            )):
                chunk_info = {
                    "rank": i + 1,
                    "document": metadata.get('document', 'Unknown'),
                    "section": metadata.get('section', 'Unknown'),
                    "chunk_index": metadata.get('chunk_index', -1),
                    "source_file": metadata.get('source_file', 'Unknown'),
                    "distance": float(distance) if distance is not None else None,
                    "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
                    "content_length": len(doc)
                }
                chunks_info.append(chunk_info)
            
            logger.info(f"Retrieved {len(results['documents'][0])} chunks:")
            for chunk in chunks_info:
                logger.info(f"  - Rank {chunk['rank']}: {chunk['document']} / {chunk['section']} (distance: {chunk['distance']})")
        
        return results
    
    def _format_context(self, results: Dict) -> str:
        """Format retrieved chunks into context"""
        if not results['documents'] or not results['documents'][0]:
            return ""
        
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0]
        )):
            section = metadata.get('section', 'Unknown')
            document = metadata.get('document', 'Unknown')
            context_parts.append(
                f"[Source {i+1} - Document: {document}, Section: {section}]\n{doc}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_or_create_session(self, user_id: int, session_id: str = None) -> ConversationSession:
        """Get existing session or create new one"""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = {}
        
        if session_id and session_id in self.active_sessions[user_id]:
            return self.active_sessions[user_id][session_id]
        
        # Create new session
        new_session = ConversationSession(session_id)
        self.active_sessions[user_id][new_session.session_id] = new_session
        logger.info(f"Created new session {new_session.session_id} for user {user_id}")
        return new_session
    
    def get_user_sessions(self, user_id: int) -> List[Dict]:
        """Get all sessions for a user, sorted by last updated"""
        if user_id not in self.active_sessions:
            return []
        
        sessions = list(self.active_sessions[user_id].values())
        sessions.sort(key=lambda x: x.last_updated, reverse=True)
        return [s.to_dict() for s in sessions]
    
    def load_session_history(self, user_id: int, session_id: str) -> List[Dict]:
        """Load conversation history for a specific session"""
        if user_id in self.active_sessions and session_id in self.active_sessions[user_id]:
            return self.active_sessions[user_id][session_id].get_chat_history()
        return []
    
    def save_session_to_db(self, user_id: int, session_id: str):
        """Save all messages from a session to database"""
        if user_id not in self.active_sessions or session_id not in self.active_sessions[user_id]:
            return
        
        session = self.active_sessions[user_id][session_id]
        
        # Save each message pair (user + assistant) as a conversation
        messages = session.messages
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages) and messages[i]["role"] == "user" and messages[i+1]["role"] == "assistant":
                conversation = Conversation(
                    user_id=user_id,
                    message=messages[i]["content"],
                    response=messages[i+1]["content"],
                    timestamp=session.last_updated,
                    conversation_type="CHAT",
                    response_time_ms=0
                )
                self.db.save_conversation(conversation)
        
        logger.info(f"Saved session {session_id} to database")
    
    @traceable(name="process_multimodal_message", run_type="chain")
    def process_message_stream(self, message: str, files: List, session: ConversationSession, user_id: int):
        """
        Process message with streaming response
        Handles 3 scenarios:
        1. Text only: Standard RAG pipeline
        2. Text + Image: Extract image info → combine with text → RAG with combined query
        3. Image only: Extract image info → use as query for RAG
        """
        start_time = time.time()
        
        try:
            if not self.auth.verify_user_access(user_id):
                yield "❌ Your account has been suspended. Please contact support."
                return
            
            has_images = files and len(files) > 0
            has_text = message and message.strip()
            
            if not has_text and not has_images:
                yield "Please provide a question or upload an image."
                return
            
            # ========== SCENARIO 1: Text only (standard RAG) ==========
            if not has_images:
                logger.info("📝 SCENARIO 1: Text-only query")
                conversation_type = self.llm_handler.classify_conversation(message)
                
                if conversation_type == "CASUAL":
                    logger.info("Handling as casual conversation")
                    full_response = ""
                    for chunk in self.llm_handler.generate_response_stream("", message):
                        full_response += chunk
                        yield full_response
                    chunks_retrieved = 0
                else:
                    logger.info("Handling as technical question")
                    results = self.retrieve_relevant_chunks(message)
                    context = self._format_context(results)
                    chunks_retrieved = len(results['documents'][0]) if results['documents'] else 0
                    
                    if not context:
                        response = "I couldn't find relevant information about this. For specific assistance, please contact our support team at support@dnext.io 📧"
                        yield response
                        full_response = response
                    else:
                        full_response = ""
                        for chunk in self.llm_handler.generate_response_stream(context, message):
                            full_response += chunk
                            yield full_response
                
                # Add to session
                session.add_message("user", message)
                session.add_message("assistant", full_response)
                
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.info(f"Query processed in {response_time_ms}ms | Type: {conversation_type} | Chunks: {chunks_retrieved}")
            
            # ========== SCENARIO 2 & 3: Image handling ==========
            else:
                if not self.vlm_handler:
                    yield "❌ Image analysis feature is not configured. Please ensure GROQ_API_KEY is set."
                    return
                
                file_path = files[0] if isinstance(files[0], str) else files[0].name
                logger.info(f"Processing file: {file_path}")
                file_ext = Path(file_path).suffix.lower()
                
                # Handle PDF conversion to image
                if file_ext == '.pdf':
                    try:
                        import fitz  # PyMuPDF
                        doc = fitz.open(file_path)
                        page = doc[0]
                        pix = page.get_pixmap()
                        img_bytes = pix.tobytes("png")
                        doc.close()
                        
                        # Extract image information using STAGE 1 only
                        extraction_result = self.vlm_handler.extract_image_info(
                            image_bytes=img_bytes,
                            user_prompt=f"Extract all visible information from this image{' related to: ' + message if has_text else ''}."
                        )
                    except ImportError:
                        yield "❌ PDF support requires PyMuPDF. Install with: `pip install PyMuPDF`"
                        return
                    except Exception as e:
                        yield f"❌ Error processing PDF: {str(e)}"
                        return
                        
                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                    # Extract image information using STAGE 1 only
                    extraction_result = self.vlm_handler.extract_image_info(
                        image_path=file_path,
                        user_prompt=f"Extract all visible information from this image{' related to: ' + message if has_text else ''}."
                    )
                else:
                    yield f"❌ Unsupported file type: {file_ext}. Supported: images (jpg, png, gif, webp) and PDF."
                    return
                
                if not extraction_result["success"]:
                    yield f"❌ Error analyzing image: {extraction_result['error']}"
                    return
                
                image_description = extraction_result["extracted_info"]
                logger.info(f"Extracted image info: {image_description[:200]}...")
                
                # SCENARIO 3: Image only (no text)
                if not has_text:
                    logger.info("📸 SCENARIO 3: Image-only query")
                    # Use extracted image info as the main query
                    retrieval_query = f"Analyze this information and help me understand it: {image_description}"
                    user_display_msg = "[IMAGE] (No text provided)"
                    
                # SCENARIO 2: Text + Image
                else:
                    logger.info("📸📝 SCENARIO 2: Text + Image query")
                    # Combine user text with image description for better retrieval
                    retrieval_query = f"{message}\n\nImage content: {image_description}"
                    user_display_msg = f"[IMAGE + TEXT] {message}"
                
                logger.info(f"Retrieval query: {retrieval_query[:200]}...")
                
                # Retrieve relevant chunks using the enhanced query
                results = self.retrieve_relevant_chunks(retrieval_query, top_k=5)
                context = self._format_context(results)
                chunks_retrieved = len(results['documents'][0]) if results['documents'] else 0
                
                logger.info(f"Retrieved {chunks_retrieved} chunks based on {'combined' if has_text else 'image'} context")
                
                if not context:
                    response = "I couldn't find relevant information about this. For specific assistance, please contact our support team at support@dnext.io 📧"
                    yield response
                    full_response = response
                else:
                    # Generate response with streaming
                    full_response = ""
                    for chunk in self.llm_handler.generate_response_stream(context, retrieval_query):
                        full_response += chunk
                        yield full_response
                
                # Add to session
                session.add_message("user", user_display_msg)
                session.add_message("assistant", full_response)
                
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.info(f"Multimodal query processed in {response_time_ms}ms | Chunks: {chunks_retrieved}")
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            yield f"❌ Error: {str(e)}"
    
    def get_logo_base64(self):
        """Encode logo as base64"""
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                return f"data:image/png;base64,{encoded}"
        return ""
    
    def _render_conversations_html(self, user_id: int, active_session_id: str = None) -> str:
        """Render conversations as clickable HTML items"""
        sessions = self.get_user_sessions(user_id)
        
        if not sessions:
            return '''
            <div class="no-conversations">
                No conversations yet<br>
                Start a new chat!
            </div>
            '''
        
        # Group by date
        sessions_by_date = {}
        for session in sessions:
            session_date = datetime.fromisoformat(session['last_updated']).date()
            today = datetime.now().date()
            yesterday = today.replace(day=today.day-1) if today.day > 1 else today
            
            if session_date == today:
                date_label = "Today"
            elif session_date == yesterday:
                date_label = "Yesterday"
            else:
                date_label = session_date.strftime("%B %d, %Y")
            
            if date_label not in sessions_by_date:
                sessions_by_date[date_label] = []
            sessions_by_date[date_label].append(session)
        
        html_parts = []
        
        for date_label, date_sessions in sessions_by_date.items():
            html_parts.append(f'<div class="session-date-header">{date_label}</div>')
            
            for session in date_sessions:
                is_active = session['session_id'] == active_session_id
                active_class = "active" if is_active else ""
                
                # Format time
                last_updated = datetime.fromisoformat(session['last_updated'])
                time_str = last_updated.strftime("%I:%M %p").lstrip('0')
                
                # Truncate title if too long
                title = session['title']
                if len(title) > 35:
                    title = title[:32] + "..."
                
                html_parts.append(f'''
                <div class="conversation-item {active_class}" 
                     data-session-id="{session['session_id']}"
                     onclick="selectConversation('{session['session_id']}'); 
                              document.getElementById('conversation-selector').value = '{session['session_id']}';
                              document.getElementById('conversation-selector').dispatchEvent(new Event('input', {{ bubbles: true }}));">
                    <svg class="conversation-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="currentColor"/>
                    </svg>
                    <div style="flex: 1; overflow: hidden;">
                        <div style="font-weight: 500; overflow: hidden; text-overflow: ellipsis;">{title}</div>
                        <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem;">{time_str}</div>
                    </div>
                </div>
                ''')
        
        return ''.join(html_parts)
    
    def create_interface(self):
        """Create compact ChatGPT-style interface that fits in one screen"""
        
        custom_css = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        body, .gradio-container {
            background-color: #ffffff !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        
        /* Login section - compact */
        .login-container {
            max-width: 380px !important;
            margin: auto !important;
            padding: 1.5rem !important;
            background: white !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
        }
        
        .login-container h1 {
            text-align: center !important;
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            color: #1f2937 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Main layout - all in one screen */
        .main-container {
            display: flex !important;
            height: 100vh !important;
            max-height: 100vh !important;
            overflow: hidden !important;
        }
        
        /* Sidebar - compact */
        .sidebar {
            width: 240px !important;
            background: #f7f7f8 !important;
            border-right: 1px solid #e5e7eb !important;
            overflow-y: auto !important;
            padding: 0.75rem !important;
            height: 100vh !important;
            flex-shrink: 0 !important;
        }
        
        .sidebar-header {
            padding: 0.5rem 0 !important;
            margin-bottom: 0.75rem !important;
        }
        
        .new-chat-btn {
            width: 100% !important;
            padding: 0.5rem !important;
            background: white !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            font-size: 0.875rem !important;
            margin-bottom: 1rem !important;
        }
        
        .user-badge {
            background: #f0fdf4 !important;
            border: 1px solid #bbf7d0 !important;
            color: #166534 !important;
            padding: 0.375rem 0.75rem !important;
            border-radius: 16px !important;
            font-size: 0.75rem !important;
            margin: 0.5rem 0 !important;
            text-align: center !important;
        }
        
        .session-date-header {
            font-size: 0.6875rem !important;
            font-weight: 600 !important;
            color: #6b7280 !important;
            margin-top: 0.75rem !important;
            margin-bottom: 0.25rem !important;
            text-transform: uppercase !important;
        }
        
        .conversation-list {
            display: flex !important;
            flex-direction: column !important;
            gap: 0.25rem !important;
        }
        
        /* Chat area - compact */
        .chat-container {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
            max-width: 900px !important;
            margin: 0 auto !important;
            padding: 0 0.75rem !important;
            width: 100% !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        
        .app-header {
            text-align: center !important;
            padding: 0.75rem 0 !important;
            border-bottom: 1px solid #e5e7eb !important;
            flex-shrink: 0 !important;
        }
        
        .app-header h1 {
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #1f2937 !important;
            margin: 0 !important;
        }
        
        .logo-container {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .logo-img {
            width: 32px !important;
            height: 32px !important;
            object-fit: contain !important;
        }
        
        /* Chatbot styling - compact */
        .chatbot {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            flex: 1 !important;
            overflow-y: auto !important;
            padding: 1rem 0 !important;
            max-width: 750px !important;
            margin: 0 auto !important;
            width: 100% !important;
            height: calc(100vh - 180px) !important;
            max-height: calc(100vh - 180px) !important;
        }
        
        /* Message bubbles - compact */
        .message {
            padding: 0.75rem 1rem !important;
            margin: 0.375rem 0 !important;
            border-radius: 8px !important;
            width: 100% !important;
            max-width: 100% !important;
            font-size: 0.875rem !important;
            line-height: 1.4 !important;
        }
        
        .message.user {
            background: #f7f7f8 !important;
            border: none !important;
        }
        
        .message.bot {
            background: white !important;
            border: none !important;
        }
        
        /* Input container - compact */
        .input-container-welcome {
            background: white !important;
            border: 1px solid #d1d5db !important;
            border-radius: 20px !important;
            padding: 0.5rem 0.75rem !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
            transition: all 0.2s !important;
            margin: 0.5rem auto 0 !important;
            max-width: 750px !important;
            width: 100% !important;
            flex-shrink: 0 !important;
        }
        
        .input-container-bottom {
            background: white !important;
            border: 1px solid #d1d5db !important;
            border-radius: 20px !important;
            padding: 0.5rem 0.75rem !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
            transition: all 0.2s !important;
            margin: 0.5rem auto !important;
            max-width: 750px !important;
            width: 100% !important;
            flex-shrink: 0 !important;
            position: sticky !important;
            bottom: 0.5rem !important;
        }
        
        /* Welcome screen - compact */
        .welcome-screen {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            height: calc(100vh - 200px) !important;
            text-align: center !important;
            padding: 0 !important;
            flex-shrink: 0 !important;
        }
        
        .welcome-screen h2 {
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            color: #1f2937 !important;
            margin-bottom: 0.25rem !important;
        }
        
        .welcome-screen p {
            font-size: 0.875rem !important;
            color: #6b7280 !important;
            margin-bottom: 1rem !important;
        }
        
        /* Logout button */
        .logout-btn {
            margin-top: 0.5rem !important;
            padding: 0.375rem !important;
            font-size: 0.75rem !important;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 6px !important;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1 !important;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c1c1c1 !important;
            border-radius: 3px !important;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8 !important;
        }
        
        /* Adjust for very small screens */
        @media (max-height: 700px) {
            .chatbot {
                height: calc(100vh - 150px) !important;
                max-height: calc(100vh - 150px) !important;
            }
            
            .welcome-screen {
                height: calc(100vh - 170px) !important;
            }
            
            .message {
                padding: 0.5rem 0.75rem !important;
                font-size: 0.8125rem !important;
            }
        }
        
        @media (max-width: 1200px) {
            .sidebar {
                width: 200px !important;
            }
            
            .chat-container {
                padding: 0 0.5rem !important;
            }
        }
        """
        
        logo_data = self.get_logo_base64()
        
        with gr.Blocks(title="Customer AI Assistant", css=custom_css) as demo:
            user_state = gr.State(None)
            current_session_id = gr.State(None)
            
            # ========== LOGIN SECTION ==========
            # ========== LOGIN SECTION ==========
            with gr.Column(visible=True, elem_classes="login-container") as login_section:
                if logo_data:
                    gr.HTML(f"""
                        <div style="text-align: center; margin-bottom: 1.5rem;">
                            <img src="{logo_data}" style="width: 80px; height: 80px; margin: 0 auto 1rem auto; display: block; object-fit: contain; image-rendering: -webkit-optimize-contrast; image-rendering: crisp-edges;">
                            <h1 style="margin: 0; font-size: 1.5rem; font-weight: 600; color: #1f2937;">Customer AI Assistant</h1>
                        </div>
                    """)
                else:
                    gr.Markdown("# 🤖 Customer AI Assistant")
                
                gr.Markdown("**Sign in to start chatting**")
                email_input = gr.Textbox(
                    label="Email", 
                    placeholder="your.email@example.com",
                    scale=1
                )
                name_input = gr.Textbox(
                    label="Full Name", 
                    placeholder="John Doe",
                    scale=1
                )
                signup_btn = gr.Button(
                    "Sign In / Sign Up", 
                    variant="primary", 
                    size="sm"
                )
                signup_status = gr.Markdown("")
            
            # ========== CHAT SECTION ==========
            with gr.Row(visible=False, elem_classes="main-container") as chat_section:
                # Sidebar (preserved from original)
                with gr.Column(scale=1, elem_classes="sidebar", min_width=240):
                    with gr.Column(elem_classes="sidebar-header"):
                        new_chat_btn = gr.Button("➕ New Chat", elem_classes="new-chat-btn")
                        user_info_display = gr.HTML("")
                    
                    # Conversation history
                    gr.HTML('<div class="session-date-header">Recent Conversations</div>')
                    conversation_selector = gr.Radio(
                        label="",
                        choices=[],
                        interactive=True,
                        show_label=False,
                        elem_classes="conversation-list"
                    )
                    
                    with gr.Row():
                        logout_btn = gr.Button("🚪 Logout", size="sm", elem_classes="logout-btn", scale=1)
                
                # Main chat area (preserved from original)
                with gr.Column(scale=3, elem_classes="chat-container"):
                    # Header
                    gr.HTML(f"""
                        <div class="app-header">
                            <div class="logo-container">
                                <img src="{logo_data}" class="logo-img" alt="Dnext Logo">
                                <h1> Customer AI Assistant</h1>
                            </div>
                        </div>
                    """)
                    
                    # Welcome screen (shown when chat is empty)
                    with gr.Column(visible=True, elem_classes="welcome-screen") as welcome_screen:
                        gr.HTML("""
                            <div style="margin-bottom: 1.5rem;">
                                <h2>How can I help you today?</h2>
                                <p>Ask me anything about Dnext services, or upload an image for assistance</p>
                            </div>
                        """)
                        
                        # Input in welcome screen
                        with gr.Column(elem_classes="input-container-welcome"):
                            msg_welcome = gr.MultimodalTextbox(
                                placeholder="Message Dnext Support...",
                                file_types=["image", ".pdf"],
                                show_label=False,
                                submit_btn=True,
                                interactive=True
                            )
                    
                    # Chatbot
                    chatbot = gr.Chatbot(
                        value=[],
                        show_label=False,
                        visible=False,
                        elem_id="chatbot-container"
                    )
                    
                    # Input at bottom (when chat is active)
                    with gr.Column(elem_classes="input-container-bottom", visible=False) as input_bottom:
                        msg = gr.MultimodalTextbox(
                            placeholder="Message Dnext Support...",
                            file_types=["image", ".pdf"],
                            show_label=False,
                            submit_btn=True,
                            interactive=True
                        )
            
            # ========== EVENT HANDLERS (PRESERVED FROM ORIGINAL) ==========
            
            def signup_handler(email, name):
                """Handle user signup/login"""
                success, message, user = self.auth.register_user(email, name)
                if success and user:
                    welcome_html = f'<div class="user-badge">✓ {user.full_name}</div>'
                    
                    # Create initial session
                    session = self.get_or_create_session(user.user_id)
                    
                    # Get session list
                    sessions = self.get_user_sessions(user.user_id)
                    session_choices = [(s['title'], s['session_id']) for s in sessions]
                    
                    return {
                        login_section: gr.update(visible=False),
                        chat_section: gr.update(visible=True),
                        signup_status: "",
                        user_state: user,
                        current_session_id: session.session_id,
                        user_info_display: welcome_html,
                        conversation_selector: gr.update(choices=session_choices, value=None),
                        welcome_screen: gr.update(visible=True),
                        chatbot: gr.update(visible=False, value=[]),
                        input_bottom: gr.update(visible=False),
                        msg_welcome: gr.update(visible=True)
                    }
                return {
                    signup_status: f"❌ {message}",
                    user_state: None
                }
            
            def new_chat_handler(user, current_session):
                """Create a new chat session"""
                if not user:
                    return {}, None, gr.update(visible=True), gr.update(visible=False, value=[]), gr.update(choices=[]), gr.update(visible=False), gr.update(visible=True)
                
                # Save current session to database if it has messages
                if current_session:
                    self.save_session_to_db(user.user_id, current_session)
                
                # Create new session
                new_session = self.get_or_create_session(user.user_id)
                
                # Update session list
                sessions = self.get_user_sessions(user.user_id)
                session_choices = [(s['title'], s['session_id']) for s in sessions]
                
                logger.info(f"Created new chat session: {new_session.session_id}")
                
                return {
                    current_session_id: new_session.session_id,
                    chatbot: gr.update(visible=False, value=[]),
                    welcome_screen: gr.update(visible=True),
                    conversation_selector: gr.update(choices=session_choices, value=None),
                    input_bottom: gr.update(visible=False),
                    msg_welcome: gr.update(visible=True)
                }
            
            def respond(multimodal_input, chat_history, user, session_id):
                """Handle user message with streaming"""
                if not user or not session_id:
                    yield chat_history, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=True)
                    return
                
                text_message = multimodal_input.get("text", "") if isinstance(multimodal_input, dict) else ""
                files = multimodal_input.get("files", []) if isinstance(multimodal_input, dict) else []
                
                if not text_message.strip() and not files:
                    yield chat_history, gr.update(visible=True if chat_history else False), gr.update(visible=False if chat_history else True), gr.update(visible=True if chat_history else False), gr.update(visible=False if chat_history else True)
                    return
                
                # Get or create session
                session = self.get_or_create_session(user.user_id, session_id)
                
                user_content = text_message if text_message else "[Image uploaded]"
                if files:
                    user_content += f" 📎 {len(files)} file(s)"
                
                # Add user message
                chat_history.append({"role": "user", "content": user_content})
                chat_history.append({"role": "assistant", "content": ""})
                
                # Show chatbot and bottom input, hide welcome
                yield chat_history, gr.update(visible=True), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
                
                # Stream the response
                for response_chunk in self.process_message_stream(text_message, files, session, user.user_id):
                    chat_history[-1]["content"] = response_chunk
                    yield chat_history, gr.update(visible=True), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
            
            def load_session_handler(session_id, user):
                """Load a conversation session"""
                if not user or not session_id:
                    return [], gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
                
                # Save current active session first
                if user.user_id in self.active_sessions:
                    for sid in self.active_sessions[user.user_id].keys():
                        if sid != session_id:
                            self.save_session_to_db(user.user_id, sid)
                
                # Load selected session
                history = self.load_session_history(user.user_id, session_id)
                
                if history:
                    return history, gr.update(visible=True), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
                else:
                    return [], gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=True)
            
            def refresh_session_list(user):
                """Refresh the conversation list"""
                if not user:
                    return gr.update(choices=[])
                
                sessions = self.get_user_sessions(user.user_id)
                session_choices = [(s['title'], s['session_id']) for s in sessions]
                return gr.update(choices=session_choices)
            
            def logout_handler(user, current_session):
                """Handle logout and save all sessions"""
                if user and current_session:
                    # Save all active sessions to database
                    if user.user_id in self.active_sessions:
                        for session_id in list(self.active_sessions[user.user_id].keys()):
                            self.save_session_to_db(user.user_id, session_id)
                        # Clear active sessions for this user
                        del self.active_sessions[user.user_id]
                
                return {
                    login_section: gr.update(visible=True),
                    chat_section: gr.update(visible=False),
                    user_state: None,
                    current_session_id: None,
                    chatbot: gr.update(value=[], visible=False),
                    welcome_screen: gr.update(visible=True),
                    msg: None,
                    msg_welcome: None,
                    email_input: "",
                    name_input: "",
                    conversation_selector: gr.update(choices=[], value=None)
                }
            
            # ========== CONNECT EVENTS (PRESERVED FROM ORIGINAL) ==========
            
            # Signup
            signup_btn.click(
                signup_handler,
                inputs=[email_input, name_input],
                outputs=[login_section, chat_section, signup_status, user_state, current_session_id, 
                        user_info_display, conversation_selector, welcome_screen, chatbot, input_bottom, msg_welcome]
            )
            
            # New chat
            new_chat_btn.click(
                new_chat_handler,
                inputs=[user_state, current_session_id],
                outputs=[current_session_id, chatbot, welcome_screen, conversation_selector, input_bottom, msg_welcome]
            )
            
            # Message submission from welcome screen
            msg_welcome.submit(
                respond,
                inputs=[msg_welcome, chatbot, user_state, current_session_id],
                outputs=[chatbot, chatbot, welcome_screen, input_bottom, msg_welcome]
            ).then(
                lambda: None,
                None,
                [msg_welcome]
            ).then(
                refresh_session_list,
                inputs=[user_state],
                outputs=[conversation_selector]
            )
            
            # Message submission from bottom input
            msg.submit(
                respond,
                inputs=[msg, chatbot, user_state, current_session_id],
                outputs=[chatbot, chatbot, welcome_screen, input_bottom, msg_welcome]
            ).then(
                lambda: None,
                None,
                [msg]
            ).then(
                refresh_session_list,
                inputs=[user_state],
                outputs=[conversation_selector]
            )
            
            # Load conversation from sidebar
            conversation_selector.change(
                load_session_handler,
                inputs=[conversation_selector, user_state],
                outputs=[chatbot, chatbot, welcome_screen, input_bottom, msg_welcome]
            ).then(
                lambda x: x,
                inputs=[conversation_selector],
                outputs=[current_session_id]
            )
            
            # Logout
            logout_btn.click(
                logout_handler,
                inputs=[user_state, current_session_id],
                outputs=[login_section, chat_section, user_state, current_session_id, 
                        chatbot, welcome_screen, msg, msg_welcome, email_input, name_input, conversation_selector]
            )
        
        return demo

def main():
    """Main entry point"""
    print("=" * 60)
    print("🚀 Starting Customer AI Assistant")
    print("=" * 60)
    
    try:
        db_repository = DatabaseRepository("data/chatbot.db")
        auth_service = AuthenticationService(db_repository)
        
        db_repository.create_admin("admin", "admin123")
        logger.info("✅ Default admin created (username: admin, password: admin123)")
        logger.info("⚠️ IMPORTANT: Change the admin password in production!")
        
        app = ChatbotApp(db_repository, auth_service)
        demo = app.create_interface()
        
        print("\n" + "=" * 60)
        print("✅ Chatbot is ready!")
        print("📊 Admin dashboard: Run admin_launcher.py")
        print("🔍 LangSmith tracing enabled")
        print("🎨 Modern ChatGPT-style interface")
        print("⚡ Dynamic session management")
        print("💾 Auto-save conversations")
        print("📸 Enhanced multimodal support:")
        print("   1️⃣ Text only → Standard RAG")
        print("   2️⃣ Text + Image → Extract image → Combine → RAG")
        print("   3️⃣ Image only → Extract image → RAG")
        print("=" * 60)
        
        # Get custom CSS from the create_interface method
        demo.launch(
            share=True,
            server_name=Config.SERVER_NAME,
            server_port=Config.SERVER_PORT,
            show_error=True,
            css="""
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            }
            
            body, .gradio-container {
                background-color: #ffffff !important;
            }
            
            .gradio-container {
                max-width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            """
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == "__main__":
    main()