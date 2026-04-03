"""
Local Embeddings Service (Free Alternative)
Uses SentenceTransformers - no API costs, works offline
"""
from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMER = True
except ImportError:
    HAS_TRANSFORMER = False


class LocalEmbeddingsService:
    def __init__(self):
        """
        Initialize local embeddings using SentenceTransformers
        Downloads model on first use (cached locally)
        """
        if not HAS_TRANSFORMER:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")
        
        print("🔄 Loading embedding model (first run may take a minute)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model ready!")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Convert text to embedding vector locally
        Returns: List of floats representing the embedding
        """
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"❌ Error creating embedding: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[dict]) -> List[dict]:
        """
        Embed all chunks locally
        Adds 'embedding' field to each chunk
        """
        embedded_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                embedding = self.embed_text(chunk["text"])
                chunk["embedding"] = embedding
                embedded_chunks.append(chunk)
                
                if (i + 1) % 10 == 0:
                    print(f"✅ Embedded {i + 1}/{len(chunks)} chunks")
            
            except Exception as e:
                print(f"❌ Error embedding chunk {chunk['chunk_id']}: {str(e)}")
                continue
        
        print(f"✅ Successfully embedded {len(embedded_chunks)}/{len(chunks)} chunks")
        return embedded_chunks
