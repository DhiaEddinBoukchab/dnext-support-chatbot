import gradio as gr
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Tuple
import time

from config import Config
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore
from src.llm_handler import LLMHandler
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
    """Handles document processing and chunking"""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:
                chunks.append(chunk)
        
        return chunks
    
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


class ChatbotApp:
    """Main chatbot application with user authentication"""
    
    def __init__(self, db_repository: DatabaseRepository, auth_service: AuthenticationService):
        """Initialize chatbot components"""
        Config.validate()
        
        # Services - Following DIP: Depend on abstractions
        self.db = db_repository
        self.auth = auth_service
        
        # Core components
        self.embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL)
        self.vector_store = VectorStore(Config.CHROMA_DB_PATH)
        self.llm_handler = LLMHandler(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
        self.doc_processor = DocumentProcessor()
        
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
    
    def load_documents(self) -> Tuple[bool, str]:
        """Load and index all documents"""
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
            
            for doc_file in md_files:
                logger.info(f"Processing: {doc_file.name}")
                
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                sections = self.doc_processor.extract_sections(content)
                
                for section in sections:
                    chunks = self.doc_processor.chunk_text(
                        section["content"],
                        Config.CHUNK_SIZE,
                        Config.CHUNK_OVERLAP
                    )
                    
                    for i, chunk in enumerate(chunks):
                        all_chunks.append(chunk)
                        all_metadatas.append({
                            "document": doc_file.stem,
                            "section": section["title"],
                            "chunk_index": i,
                            "source_file": doc_file.name
                        })
                        total_chunks += 1
            
            logger.info("Generating embeddings...")
            embeddings = self.embedding_manager.encode_batch(all_chunks)
            
            logger.info("Adding to vector store...")
            self.vector_store.add_documents(all_chunks, all_metadatas, embeddings)
            
            message = f"✅ Successfully indexed {total_chunks} chunks from {len(md_files)} documents!"
            logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"❌ Error loading documents: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def answer_query(self, message: str, history: List, user_id: int) -> str:
        """Process query and generate answer - tracks conversation"""
        start_time = time.time()
        
        try:
            # Verify user access
            if not self.auth.verify_user_access(user_id):
                return "❌ Your account has been suspended. Please contact support."
            
            # Classify conversation type
            conversation_type = self.llm_handler.classify_conversation(message)
            
            # For casual conversations
            if conversation_type == "CASUAL":
                logger.info("Handling as casual conversation")
                answer = self.llm_handler.generate_response("", message)
            else:
                # For technical questions
                logger.info("Handling as technical question")
                
                query_embedding = self.embedding_manager.encode(message)
                results = self.vector_store.query(query_embedding, Config.TOP_K_RESULTS)
                context = self._format_context(results)
                
                if not context:
                    answer = "I couldn't find relevant information in our documentation about this. For specific assistance, please contact our support team at support@dnext.io 📧"
                else:
                    answer = self.llm_handler.generate_response(context, message)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Save conversation to database
            conversation = Conversation(
                user_id=user_id,
                message=message,
                response=answer,
                timestamp=datetime.now(),
                conversation_type=conversation_type,
                response_time_ms=response_time_ms
            )
            self.db.save_conversation(conversation)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return f"❌ Error: {str(e)}"
    
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
            context_parts.append(f"[Source {i+1} - {section}]\n{doc}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def create_interface(self):
        """Create Gradio interface with authentication"""
        with gr.Blocks(theme=gr.themes.Soft(), title="Dnext Support Assistant") as demo:
            
            # User state
            user_state = gr.State(None)  # Stores user object
            
            # Login section
            with gr.Column(visible=True) as login_section:
                gr.Markdown("""
                # 🤖 Dnext Customer Support Assistant
                ### Please sign up or login to continue
                """)
                
                with gr.Row():
                    email_input = gr.Textbox(
                        label="Email",
                        placeholder="your.email@example.com"
                    )
                    name_input = gr.Textbox(
                        label="Full Name",
                        placeholder="John Doe"
                    )
                
                signup_btn = gr.Button("Sign Up / Login", variant="primary")
                signup_status = gr.Markdown("")
            
            # Chat section (hidden initially)
            with gr.Column(visible=False) as chat_section:
                gr.Markdown("""
                # 🤖 Dnext Customer Support Assistant
                ### Get instant help with the Dnext platform
                """)
                
                user_info_display = gr.Markdown("")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(height=500)
                        
                        with gr.Row():
                            msg = gr.Textbox(
                                placeholder="Type your question here...",
                                label="Your Question",
                                scale=4
                            )
                            submit = gr.Button("Send", variant="primary", scale=1)
                        
                        with gr.Row():
                            clear = gr.Button("Clear Chat")
                            logout_btn = gr.Button("Logout", variant="stop")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 💡 Example Questions")
                        gr.Examples(
                            examples=[
                                "How do I download a dataset?",
                                "I'm having login issues",
                                "Show me Python API code",
                                "How can I find a dataset code?",
                                "Password reset steps?",
                            ],
                            inputs=msg
                        )
                        
                        gr.Markdown("""
                        ### ℹ️ Tips
                        - Be specific with your questions
                        - Mention exact features
                        - Request code examples when needed
                        """)
            
            # Event handlers
            def signup_handler(email, name):
                """Handle user signup/login"""
                success, message, user = self.auth.register_user(email, name)
                
                if success and user:
                    welcome_msg = f"Welcome, **{user.full_name}**! ({user.email})"
                    return {
                        login_section: gr.update(visible=False),
                        chat_section: gr.update(visible=True),
                        signup_status: "",
                        user_state: user,
                        user_info_display: welcome_msg
                    }
                
                return {
                    signup_status: message,
                    user_state: None
                }
            
            signup_btn.click(
                signup_handler,
                inputs=[email_input, name_input],
                outputs=[login_section, chat_section, signup_status, user_state, user_info_display]
            )
            
            def respond(message, chat_history, user):
                """Handle chat response"""
                if not message.strip() or not user:
                    return chat_history, ""
                
                bot_message = self.answer_query(message, chat_history, user.user_id)
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": bot_message})
                return chat_history, ""
            
            def clear_chat():
                return [], ""
            
            def logout_handler():
                """Handle logout"""
                return {
                    login_section: gr.update(visible=True),
                    chat_section: gr.update(visible=False),
                    user_state: None,
                    chatbot: [],
                    msg: "",
                    email_input: "",
                    name_input: ""
                }
            
            msg.submit(respond, [msg, chatbot, user_state], [chatbot, msg])
            submit.click(respond, [msg, chatbot, user_state], [chatbot, msg])
            clear.click(clear_chat, None, [chatbot, msg])
            logout_btn.click(
                logout_handler,
                None,
                [login_section, chat_section, user_state, chatbot, msg, email_input, name_input]
            )
        
        return demo


def main():
    """Main entry point"""
    print("=" * 60)
    print("🚀 Starting Dnext Customer Support Chatbot")
    print("=" * 60)
    
    try:
        # Initialize services
        db_repository = DatabaseRepository("data/chatbot.db")
        auth_service = AuthenticationService(db_repository)
        
        # Create default admin if not exists
        db_repository.create_admin("admin", "admin123")  # Change this password!
        logger.info("✅ Default admin created (username: admin, password: admin123)")
        logger.info("⚠️ IMPORTANT: Change the admin password in production!")
        
        # Initialize app
        app = ChatbotApp(db_repository, auth_service)
        demo = app.create_interface()
        
        print("\n" + "=" * 60)
        print("✅ Chatbot is ready!")
        print("📊 Admin dashboard: Run admin_launcher.py")
        print("=" * 60)
        
        demo.launch(
            share=True,
            server_name=Config.SERVER_NAME,
            server_port=Config.SERVER_PORT,
            show_error=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main()