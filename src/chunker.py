"""
Chunker module for splitting documents by separator patterns.
ONLY uses asterisk-based separators (****+) - NO FALLBACK to word-based chunking.
"""

import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class Chunker:
    """
    Handles document chunking using ONLY separator-based strategy.
    Documents MUST contain separator patterns (****+).
    """
    
    # Pattern for separator: 4 or more asterisks with optional whitespace
    # This matches: \n****\n, \n*****\n, \n******\n, etc.
    SEPARATOR_PATTERN = re.compile(r'\n\s*\*{4,}\s*\n')
    
    @staticmethod
    def chunk_by_separator(text: str) -> List[str]:
        """
        Split text by asterisk separators (4+ asterisks).
        Each chunk is a standalone section from the document.
        
        Args:
            text: Input text with separator patterns (****+)
            
        Returns:
            List of text chunks separated by the pattern
            Empty list if no separators found
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to chunk_by_separator")
            return []
        
        # Split by the separator pattern
        chunks = Chunker.SEPARATOR_PATTERN.split(text)
        
        # Filter out empty chunks and strip whitespace
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        if not chunks:
            logger.warning("No chunks created after splitting by separator")
            return []
        
        logger.info(f"Separator-based chunking created {len(chunks)} chunks")
        return chunks
    
    @classmethod
    def chunk_text(cls, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Chunk text using separator-based strategy with fallback to word-based chunking.

        First tries separator chunking, then falls back to word-based if no separators found.

        Args:
            text: Input text to chunk
            chunk_size: Chunk size for word-based fallback (default 400)
            overlap: Overlap for word-based fallback (default 50)

        Returns:
            List of chunks
            Empty list if text is empty
        """
        if not text or not text.strip():
            logger.error("Empty or None text provided to chunk_text")
            return []

        # Try separator-based chunking first
        chunks = cls.chunk_by_separator(text)

        if chunks:
            logger.info(f"✅ Successfully chunked text into {len(chunks)} chunks using separators")
            return chunks

        # Fallback to word-based chunking
        logger.warning("No separator patterns found, falling back to word-based chunking")
        return cls.chunk_by_words(text, chunk_size or 400, overlap or 50)

    @staticmethod
    def chunk_by_words(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """
        Chunk text by words with overlap.

        Args:
            text: Input text
            chunk_size: Maximum words per chunk
            overlap: Words to overlap between chunks

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        words = text.split()
        if len(words) <= chunk_size:
            return [text.strip()]

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = ' '.join(words[start:end])
            chunks.append(chunk.strip())
            start += chunk_size - overlap
            if start >= len(words):
                break

        logger.info(f"✅ Word-based chunking created {len(chunks)} chunks")
        return chunks
    
    @staticmethod
    def extract_metadata_from_chunk(chunk: str, document_name: str, section_title: str, chunk_index: int) -> Dict:
        """
        Extract meaningful metadata from a chunk.
        For separator-based chunks, extracts first line as summary.
        
        Args:
            chunk: The text chunk
            document_name: Name of the source document
            section_title: Section/category this came from
            chunk_index: Index of this chunk in the sequence
            
        Returns:
            Dictionary with metadata
        """
        # Get first line or first 50 chars as preview
        lines = chunk.split('\n')
        first_line = lines[0].strip() if lines else chunk[:50]
        
        # Extract some keywords from the chunk (first 20 words)
        words = chunk.split()
        keywords = ' '.join(words[:20]) if len(words) >= 20 else ' '.join(words)
        
        return {
            "document": document_name,
            "section": section_title,
            "chunk_index": chunk_index,
            "chunk_preview": first_line[:100] + "..." if len(first_line) > 100 else first_line,
            "chunk_length": len(chunk),
            "word_count": len(words),
            "keywords": keywords,
            "source_file": document_name
        }
    
    @staticmethod
    def validate_document_format(text: str) -> Dict[str, any]:
        """
        Validate that a document contains proper separator patterns.
        
        Args:
            text: Document text to validate
            
        Returns:
            Dictionary with validation results:
            - valid: bool
            - separator_count: int
            - expected_chunks: int
            - message: str
        """
        if not text or not text.strip():
            return {
                "valid": False,
                "separator_count": 0,
                "expected_chunks": 0,
                "message": "Empty document"
            }
        
        separators = Chunker.SEPARATOR_PATTERN.findall(text)
        separator_count = len(separators)
        expected_chunks = separator_count + 1  # n separators = n+1 chunks
        
        if separator_count == 0:
            return {
                "valid": False,
                "separator_count": 0,
                "expected_chunks": 0,
                "message": "No separator patterns (****+) found in document"
            }
        
        return {
            "valid": True,
            "separator_count": separator_count,
            "expected_chunks": expected_chunks,
            "message": f"Document valid: {separator_count} separators, {expected_chunks} expected chunks"
        }