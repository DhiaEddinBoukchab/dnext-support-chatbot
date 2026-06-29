"""Chunk documents using asterisk-based separators."""

import logging
import re
from typing import Dict, List


logger = logging.getLogger(__name__)


class Chunker:
    """Handle document chunking using separator-based strategy only."""

    SEPARATOR_PATTERN = re.compile(r"\n\s*\*{4,}\s*\n")

    @staticmethod
    def chunk_by_separator(text: str) -> List[str]:
        """Split text by separator lines containing at least four asterisks."""
        if not text or not text.strip():
            logger.warning("Empty text provided to chunk_by_separator")
            return []

        chunks = Chunker.SEPARATOR_PATTERN.split(text)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        if not chunks:
            logger.warning("No chunks created after splitting by separator")
            return []

        logger.info(f"Separator-based chunking created {len(chunks)} chunks")
        return chunks

    @classmethod
    def chunk_text(cls, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Chunk text using separator-based strategy only."""
        if not text or not text.strip():
            logger.error("Empty or None text provided to chunk_text")
            return []

        chunks = cls.chunk_by_separator(text)
        if not chunks:
            logger.error(
                "Chunking failed because no separator patterns (****+) were found in the document."
            )
            return []

        logger.info(f"Successfully chunked text into {len(chunks)} chunks")
        return chunks

    @staticmethod
    def extract_metadata_from_chunk(
        chunk: str,
        document_name: str,
        section_title: str,
        chunk_index: int,
    ) -> Dict:
        """Extract metadata from a chunk."""
        lines = chunk.split("\n")
        first_line = lines[0].strip() if lines else chunk[:50]
        words = chunk.split()
        keywords = " ".join(words[:20]) if len(words) >= 20 else " ".join(words)

        return {
            "document": document_name,
            "section": section_title,
            "chunk_index": chunk_index,
            "chunk_preview": first_line[:100] + "..." if len(first_line) > 100 else first_line,
            "chunk_length": len(chunk),
            "word_count": len(words),
            "keywords": keywords,
            "source_file": document_name,
        }

    @staticmethod
    def validate_document_format(text: str) -> Dict[str, object]:
        """Validate that a document contains the required separator pattern."""
        if not text or not text.strip():
            return {
                "valid": False,
                "separator_count": 0,
                "expected_chunks": 0,
                "message": "Empty document",
            }

        separators = Chunker.SEPARATOR_PATTERN.findall(text)
        separator_count = len(separators)
        expected_chunks = separator_count + 1

        if separator_count == 0:
            return {
                "valid": False,
                "separator_count": 0,
                "expected_chunks": 0,
                "message": "No separator patterns (****+) found in document",
            }

        return {
            "valid": True,
            "separator_count": separator_count,
            "expected_chunks": expected_chunks,
            "message": f"Document valid: {separator_count} separators, {expected_chunks} expected chunks",
        }
