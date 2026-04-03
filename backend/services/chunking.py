"""
Text Chunking Service
Splits text into overlapping chunks of 300-500 words
"""
from typing import List, Dict


class TextChunker:
    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        """
        Initialize chunker
        chunk_size: target words per chunk
        overlap: words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, source: str = "document") -> List[Dict[str, str]]:
        """
        Split text into chunks with overlap
        Returns: List of dicts with 'text', 'source', and 'chunk_id' keys
        """
        # Split by sentences/paragraphs for cleaner chunks
        sentences = text.replace("\n\n", ". ").split(". ")
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_word_count = len(sentence.split())
            current_word_count += sentence_word_count
            current_chunk.append(sentence)
            
            # Check if we've reached target size
            if current_word_count >= self.chunk_size:
                chunk_text = ". ".join(current_chunk)
                
                if chunk_text.strip():
                    chunks.append({
                        "text": chunk_text,
                        "source": source,
                        "chunk_id": chunk_id
                    })
                    chunk_id += 1
                
                # Keep last N sentences for overlap
                overlap_count = self.overlap // 10  # rough estimate (10 words per sentence)
                current_chunk = current_chunk[-overlap_count:] if overlap_count > 0 else []
                current_word_count = sum(len(s.split()) for s in current_chunk)
        
        # Add remaining text
        if current_chunk:
            chunk_text = ". ".join(current_chunk)
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "source": source,
                    "chunk_id": chunk_id
                })
        
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Chunk all documents
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_text(doc["text"], source=doc["filename"])
            all_chunks.extend(chunks)
        
        print(f"✓ Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
