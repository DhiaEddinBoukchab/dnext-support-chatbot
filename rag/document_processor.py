"""Document processing utilities for section extraction and chunking."""

from typing import Dict, List

from rag.chunker import Chunker


class DocumentProcessor:
    """Process markdown documents into sections and chunks."""

    def __init__(self):
        self.chunker = Chunker()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text using separator-based chunking."""
        return Chunker.chunk_text(text, chunk_size, overlap)

    @staticmethod
    def extract_sections(text: str) -> List[Dict[str, str]]:
        """Extract sections based on markdown headers."""
        sections = []
        current_section = {"title": "Introduction", "content": ""}

        for line in text.split("\n"):
            if line.strip().startswith("#"):
                if current_section["content"].strip():
                    sections.append(current_section)
                title = line.strip().lstrip("#").strip()
                current_section = {"title": title, "content": ""}
            else:
                current_section["content"] += line + "\n"

        if current_section["content"].strip():
            sections.append(current_section)

        return sections
