"""
Vector Store Service
Manages FAISS index for semantic search
"""
import faiss
import numpy as np
import pickle
from typing import List, Dict, Tuple
from pathlib import Path


class VectorStore:
    def __init__(self, index_path: str = "database/faiss_index.pkl"):
        """
        Initialize vector store
        index_path: where to save/load FAISS index
        """
        self.index_path = index_path
        self.index = None
        self.chunks = []  # Store original chunks with embeddings
        self.embedding_dim = None
    
    def create_index(self, embedded_chunks: List[dict]) -> None:
        """
        Create FAISS index from embedded chunks
        """
        if not embedded_chunks:
            raise ValueError("No chunks provided")
        
        # Extract embeddings
        embeddings = [chunk["embedding"] for chunk in embedded_chunks]
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        self.embedding_dim = embeddings_array.shape[1]
        
        # Create FAISS index (L2 distance)
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings_array)
        
        # Store chunks for later retrieval
        self.chunks = embedded_chunks
        
        print(f"✓ Created FAISS index with {len(embedded_chunks)} vectors (dim={self.embedding_dim})")
    
    def save_index(self) -> None:
        """Save index and chunks to disk"""
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "index": self.index,
            "chunks": self.chunks,
            "embedding_dim": self.embedding_dim
        }
        
        with open(self.index_path, "wb") as f:
            pickle.dump(data, f)
        
        print(f"✓ Saved index to {self.index_path}")
    
    def load_index(self) -> bool:
        """Load index and chunks from disk"""
        if not Path(self.index_path).exists():
            return False
        
        try:
            with open(self.index_path, "rb") as f:
                data = pickle.load(f)
            
            self.index = data["index"]
            self.chunks = data["chunks"]
            self.embedding_dim = data["embedding_dim"]
            
            print(f"✓ Loaded index from {self.index_path} ({len(self.chunks)} chunks)")
            return True
        except Exception as e:
            print(f"✗ Error loading index: {str(e)}")
            return False
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """
        Search for similar chunks
        Returns: List of top-k chunks with distances
        """
        if self.index is None:
            raise RuntimeError("Index not initialized")
        
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["distance"] = float(distances[0][i])
                results.append(chunk)
        
        return results
    
    def search_in_chunks(self, query_embedding: List[float], filtered_chunks: List[Dict], k: int = 5) -> List[Dict]:
        """
        Search for similar chunks within a pre-filtered list (e.g., user-specific chunks).
        This is used for user isolation in multi-user scenarios.
        Returns: List of top-k chunks with distances from the filtered set
        """
        if not filtered_chunks:
            return []
        
        # Filter to only chunks that have embeddings
        chunks_with_embeddings = [chunk for chunk in filtered_chunks if "embedding" in chunk]
        
        if not chunks_with_embeddings:
            # No chunks have embeddings, return empty list
            print(f"[WARNING] search_in_chunks() received {len(filtered_chunks)} chunks, but none have embeddings")
            return []
        
        # Extract embeddings from chunks with embeddings
        embeddings = np.array([chunk["embedding"] for chunk in chunks_with_embeddings], dtype=np.float32)
        
        # Create a temporary FAISS index for the filtered chunks
        if embeddings.shape[0] == 0:
            return []
        
        temp_index = faiss.IndexFlatL2(embeddings.shape[1])
        temp_index.add(embeddings)
        
        # Search in the temporary index
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = temp_index.search(query_array, min(k, len(chunks_with_embeddings)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(chunks_with_embeddings):
                chunk = chunks_with_embeddings[idx].copy()
                chunk["distance"] = float(distances[0][i])
                results.append(chunk)
        
        return results
    
    def get_all_chunks(self) -> List[Dict]:
        """Get all chunks"""
        return self.chunks
    
    def add_chunks(self, new_chunks: List[Dict]) -> None:
        """
        Add new chunks to the existing index.
        If no index exists, create one with the new chunks.
        """
        if not new_chunks:
            return
        
        # If no index exists, create one
        if self.index is None:
            self.create_index(new_chunks)
            self.save_index()
            return
        
        # Extract embeddings from new chunks
        new_embeddings = np.array([chunk["embedding"] for chunk in new_chunks], dtype=np.float32)
        
        # Get current embeddings
        existing_embeddings = np.array([chunk["embedding"] for chunk in self.chunks], dtype=np.float32)
        
        # Combine all embeddings
        all_embeddings = np.vstack([existing_embeddings, new_embeddings])
        
        # Create new index with combined embeddings
        self.embedding_dim = all_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(all_embeddings)
        
        # Combine chunks
        self.chunks.extend(new_chunks)
        
        print(f"✓ Added {len(new_chunks)} chunks to index. Total chunks: {len(self.chunks)}")
        
        # Save the updated index
        self.save_index()
    
    def count_chunks(self) -> int:
        """Count the number of chunks in the index"""
        return len(self.chunks) if self.chunks else 0
    
    def clear(self) -> None:
        """Clear the index"""
        self.index = None
        self.chunks = []
        self.embedding_dim = None
