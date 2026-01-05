
import gradio as gr
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Tuple

from config import Config
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore
from src.llm_handler import LLMHandler

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
    """Main chatbot application"""
    
    def __init__(self):
        """Initialize chatbot components"""
        Config.validate()
        
        self.embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL)
        self.vector_store = VectorStore(Config.CHROMA_DB_PATH)
        self.llm_handler = LLMHandler(Config.GROQ_API_KEY, Config.GROQ_MODEL)
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
            
            # Generate embeddings in batch
            logger.info("Generating embeddings...")
            embeddings = self.embedding_manager.encode_batch(all_chunks)
            
            # Add to vector store
            logger.info("Adding to vector store...")
            self.vector_store.add_documents(all_chunks, all_metadatas, embeddings)
            
            message = f"✅ Successfully indexed {total_chunks} chunks from {len(md_files)} documents!"
            logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"❌ Error loading documents: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def answer_query(self, message: str, history: List) -> str:
        """Process query and generate answer with intelligent classification"""
        try:
            # Classify conversation type first
            conversation_type = self.llm_handler.classify_conversation(message)
            
            # For casual conversations, respond directly without context retrieval
            if conversation_type == "CASUAL":
                logger.info("Handling as casual conversation")
                answer = self.llm_handler.generate_response("", message)
                return answer
            
            # For technical questions, retrieve context and respond
            logger.info("Handling as technical question")
            
            # Get embedding for query
            query_embedding = self.embedding_manager.encode(message)
            
            # Retrieve relevant context
            results = self.vector_store.query(query_embedding, Config.TOP_K_RESULTS)
            
            # Format context
            context = self._format_context(results)
            
            if not context:
                return "I couldn't find relevant information in our documentation about this. For specific assistance, please contact our support team at support@dnext.io 📧"
            
            # Generate technical response
            answer = self.llm_handler.generate_response(context, message)
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
        """Create Gradio interface"""
        with gr.Blocks(theme=gr.themes.Soft(), title="Dnext Support Assistant") as demo:
            
            gr.Markdown("""
            # 🤖 Dnext Customer Support Assistant
            ### Get instant help with the Dnext platform
            
            Ask any question about datasets, TradeMatrix, API usage, authentication, or troubleshooting!
            """)
            
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
                        reindex = gr.Button("Reindex Documents")
                
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
            
            def respond(message, chat_history):
                if not message.strip():
                    return chat_history, ""
                
                bot_message = self.answer_query(message, chat_history)
                # Gradio 5.0 format: list of dicts with 'role' and 'content'
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": bot_message})
                return chat_history, ""
            
            def clear_chat():
                return [], ""
            
            def reindex_docs():
                success, message = self.load_documents()
                return [], message
            
            msg.submit(respond, [msg, chatbot], [chatbot, msg])
            submit.click(respond, [msg, chatbot], [chatbot, msg])
            clear.click(clear_chat, None, [chatbot, msg])
            reindex.click(reindex_docs, None, [chatbot, msg])
        
        return demo

def main():
    """Main entry point"""
    print("=" * 60)
    print("🚀 Starting Dnext Customer Support Chatbot")
    print("=" * 60)
    
    try:
        app = ChatbotApp()
        demo = app.create_interface()
        
        print("\n" + "=" * 60)
        print("✅ Chatbot is ready!")
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