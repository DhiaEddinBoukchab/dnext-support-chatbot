"""
Message handler: processes user messages (text, images, PDFs) and streams LLM responses.
Scenario 1 — text only    → standard RAG pipeline
Scenario 2 — text + files → extract file info → combine → RAG
Scenario 3 — files only   → extract file info → RAG
"""

import json
import logging
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List, Optional

from langsmith import traceable

from models import Conversation
from app.session import ConversationSession
from app.rag_engine import RAGEngine

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
NO_CONTEXT_REPLY = (
    "I couldn't find relevant information about this. "
    "For specific assistance, please contact our support team at support@dnext.io 📧"
)


class MessageHandler:
    """Streams LLM responses for all message scenarios."""

    def __init__(self, rag_engine: RAGEngine, llm_handler, vlm_handler, db, auth):
        self.rag = rag_engine
        self.llm = llm_handler
        self.vlm = vlm_handler
        self.db = db
        self.auth = auth

    @staticmethod
    def _record_response_metadata(
        session: ConversationSession,
        conversation_type: str,
        chunks_retrieved: int,
        start_time: float,
    ):
        """Store response metadata so API wrappers can emit accurate stats."""
        session.set_response_metadata(
            conversation_type=conversation_type,
            chunks_retrieved=chunks_retrieved,
            response_time_ms=int((time.time() - start_time) * 1000),
        )

    @traceable(name="process_multimodal_message", run_type="chain")
    async def process_stream(
        self,
        message: str,
        files: List,
        session: ConversationSession,
        user_id: int,
    ) -> Generator[str, None, None]:
        """Main entry point — yields partial response strings for streaming."""
        start_time = time.time()

        try:
            if not self.auth.verify_user_access(user_id):
                yield "❌ Your account has been suspended. Please contact support."
                return

            has_images = bool(files)
            has_text = bool(message and message.strip())

            # ── Strip .txt files → append their content to message ───────────
            if has_images:
                remaining_files = []
                for f in files:
                    file_path = f if isinstance(f, str) else f.name
                    if Path(file_path).suffix.lower() == '.txt':
                        try:
                            with open(file_path, 'r', encoding='utf-8') as fh:
                                text_content = fh.read()
                            message = (message + "\n\n" + text_content).strip() if has_text else text_content
                            has_text = True
                        except Exception as e:
                            yield f"❌ Error reading text file: {str(e)}"
                            return
                    else:
                        remaining_files.append(f)
                files = remaining_files
                has_images = bool(files)

            if not has_text and not has_images:
                yield "Please provide a question or upload an image."
                return

            # ── SCENARIO 1: Text only ─────────────────────────────────────────
            if not has_images:
                async for chunk in self._handle_text(message, session, user_id, start_time):
                    yield chunk

            # ── SCENARIO 2 & 3: Files (images / PDFs) ───────────────────────
            else:
                async for chunk in self._handle_files(message, files, session, user_id, start_time, has_text):
                    yield chunk

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            yield f"❌ Error: {str(e)}"

    # ─────────────────────────────────────────────────────────────────────────
    # SCENARIO 1
    # ─────────────────────────────────────────────────────────────────────────

    async def _handle_text(self, message: str, session: ConversationSession, user_id: int, start_time: float):
        if not self.rag:
            yield "❌ RAG is not configured. Please ensure vector database is set up."
            return

        results = self.rag.retrieve(message, top_k=5)
        context = self.rag.format_context(results)
        chunks_retrieved = len(results['documents'][0]) if results['documents'] else 0

        if not context:
            yield NO_CONTEXT_REPLY
            full_response = NO_CONTEXT_REPLY
        else:
            full_response = ""
            async for chunk in self.llm.generate_response_stream(context, message, conversation_history=session.messages):
                full_response += chunk
                yield full_response

        session.add_message("user", message)
        session.add_message("assistant", full_response)

        self.db.save_conversation(Conversation(
            user_id=user_id,
            session_id=session.session_id,
            message=message,
            response=full_response,
            timestamp=datetime.now(),
            conversation_type="TECHNICAL",
            response_time_ms=int((time.time() - start_time) * 1000),
            attachments=None,
        ))
        self._record_response_metadata(
            session=session,
            conversation_type="TECHNICAL",
            chunks_retrieved=chunks_retrieved,
            start_time=start_time,
        )
        logger.info(f"Text query done in {int((time.time()-start_time)*1000)}ms | TECHNICAL | {chunks_retrieved} chunks")

    # ─────────────────────────────────────────────────────────────────────────
    # SCENARIO 2 & 3
    # ─────────────────────────────────────────────────────────────────────────

    async def _handle_files(
        self,
        message: str,
        files: List,
        session: ConversationSession,
        user_id: int,
        start_time: float,
        has_text: bool,
    ):
        if not self.vlm:
            yield "❌ Image analysis is not configured. Please ensure GROQ_API_KEY is set."
            return

        # Extract info from every file
        all_descriptions: List[str] = []
        for file_item in files:
            file_path = file_item if isinstance(file_item, str) else file_item.name
            file_ext = Path(file_path).suffix.lower()

            if file_ext == '.pdf':
                try:
                    import fitz
                    doc = fitz.open(file_path)
                    img_bytes = doc[0].get_pixmap().tobytes("png")
                    doc.close()
                    result = await self.vlm.extract_image_info(
                        image_bytes=img_bytes,
                        user_prompt=f"Extract all visible information from this image"
                                    f"{' related to: ' + message if has_text else ''}."
                    )
                except ImportError:
                    yield "❌ PDF support requires PyMuPDF: `pip install PyMuPDF`"
                    return
                except Exception as e:
                    yield f"❌ Error processing PDF: {str(e)}"
                    return

            elif file_ext in SUPPORTED_IMAGE_EXTS:
                result = await self.vlm.extract_image_info(
                    image_path=file_path,
                    user_prompt=f"Extract all visible information from this image"
                                f"{' related to: ' + message if has_text else ''}."
                )
            else:
                yield f"❌ Unsupported file type: {file_ext}. Supported: images (jpg, png, gif, webp) and PDF."
                return

            if not result["success"]:
                yield f"❌ Error analyzing {Path(file_path).name}: {result['error']}"
                return

            all_descriptions.append(
                f"[File {len(all_descriptions)+1}: {Path(file_path).name}]\n{result['extracted_info']}"
            )
            logger.info(f"Extracted from {Path(file_path).name}: {result['extracted_info'][:100]}...")

        combined = "\n\n".join(all_descriptions)
        num_files = len(files)

        if not has_text:
            retrieval_query = f"Analyze this information and help me understand it: {combined}"
            user_display_msg = f"[{num_files} FILE(S)] (No text provided)"
        else:
            retrieval_query = f"{message}\n\nFile content(s):\n{combined}"
            user_display_msg = f"[{num_files} FILE(S) + TEXT] {message}"

        results = self.rag.retrieve(retrieval_query, top_k=5)
        context = self.rag.format_context(results)
        chunks_retrieved = len(results['documents'][0]) if results['documents'] else 0

        if not context:
            yield NO_CONTEXT_REPLY
            full_response = NO_CONTEXT_REPLY
        else:
            full_response = ""
            async for chunk in self.llm.generate_response_stream(context, retrieval_query, conversation_history=session.messages):
                full_response += chunk
                yield full_response

        session.add_message("user", user_display_msg)
        session.add_message("assistant", full_response)

        # Save attachments to uploads/
        attachments_meta = self._save_attachments(files)

        self.db.save_conversation(Conversation(
            user_id=user_id,
            session_id=session.session_id,
            message=user_display_msg,
            response=full_response,
            timestamp=datetime.now(),
            conversation_type="TECHNICAL",
            response_time_ms=int((time.time() - start_time) * 1000),
            attachments=json.dumps(attachments_meta) if attachments_meta else None,
        ))
        self._record_response_metadata(
            session=session,
            conversation_type="TECHNICAL",
            chunks_retrieved=chunks_retrieved,
            start_time=start_time,
        )
        logger.info(f"File query done in {int((time.time()-start_time)*1000)}ms | {chunks_retrieved} chunks")

    def _save_attachments(self, files: List) -> List[Dict[str, str]]:
        """Copy uploaded files to the persistent uploads/ directory."""
        uploads_dir = Path("data/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        meta = []
        for f in files:
            src = Path(f) if isinstance(f, str) else Path(f.name)
            if not src.exists():
                continue
            ext = src.suffix.lower()
            dest = uploads_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}{ext}"
            try:
                shutil.copy2(src, dest)
            except Exception as e:
                logger.warning(f"Failed to copy attachment {src}: {e}")
                continue
            meta.append({
                "type": "image" if ext in SUPPORTED_IMAGE_EXTS else "file",
                "path": str(dest),
                "original_name": src.name,
            })
        return meta
