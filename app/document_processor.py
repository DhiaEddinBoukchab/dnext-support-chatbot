"""
Document processing: chunking and section extraction.
"""

from typing import List, Dict
from src.chunker import Chunker


class DocumentProcessor:
    """Handles document processing and chunking using smart chunker."""

    def __init__(self):
        self.chunker = Chunker()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text using separator-based chunking. chunk_size/overlap are ignored (kept for compatibility)."""
        return Chunker.chunk_text(text, chunk_size, overlap)

    @staticmethod
    def extract_sections(text: str) -> List[Dict[str, str]]:
        """Extract sections based on markdown headers."""
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