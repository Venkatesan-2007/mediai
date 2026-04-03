"""ChromaDB service for vector storage and semantic search"""
import chromadb
from typing import List, Dict, Optional
import os
from pathlib import Path

class ChromaDBService:
    def __init__(self, persist_dir: str = "database/chroma_db"):
        """Initialize ChromaDB client with persistence"""
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Create persistent Chroma client
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="medical_documents",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
    
    def add_chunks(self, chunks: List[Dict]) -> None:
        """Add chunks to ChromaDB collection"""
        if not chunks:
            return
        
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for chunk in chunks:
            chunk_id = f"{chunk.get('source', 'unknown')}_{chunk.get('chunk_id', 0)}"
            ids.append(chunk_id)
            documents.append(chunk['text'])
            
            metadata = {
                'source': chunk.get('source', 'unknown'),
                'chunk_id': str(chunk.get('chunk_id', 0)),
                'user_id': str(chunk.get('user_id', 0)),
                'chunk_index': str(chunk.get('chunk_id', 0))
            }
            metadatas.append(metadata)
            
            # If chunk has embedding, include it
            if 'embedding' in chunk:
                embeddings.append(chunk['embedding'])
        
        # Add to collection
        if embeddings:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
        else:
            # Let ChromaDB compute embeddings (uses default)
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
    
    def search(self, query_text: str, k: int = 5, user_id: int = None) -> List[Dict]:
        """Search for similar chunks
        
        Args:
            query_text: Text to search for
            k: Number of results to return
            user_id: User ID for filtering (REQUIRED for user isolation)
        
        Returns:
            List of relevant chunks filtered by user_id
            
        Raises:
            ValueError: If user_id is None (security requirement)
        """
        # SECURITY: Enforce user_id to prevent reading other users' documents
        if user_id is None:
            raise ValueError("user_id is required for security - cannot search without user isolation")
        
        # Build where filter for user isolation
        where_filter = {"user_id": str(user_id)}
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=k,
            where=where_filter,
            include=["documents", "metadatas", "distances", "embeddings"]
        )
        
        if not results['documents'] or not results['documents'][0]:
            return []
        
        # Format results
        chunks = []
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            chunk = {
                'id': results['ids'][0][i],
                'text': doc,
                'source': meta.get('source', 'unknown'),
                'chunk_id': int(meta.get('chunk_id', 0)),
                'user_id': int(meta.get('user_id', 0)),
                'distance': float(dist)  # Distance metric
            }
            chunks.append(chunk)
        
        return chunks
    
    def get_all_chunks(self, user_id: int = None) -> List[Dict]:
        """Get all chunks (optionally filtered by user)"""
        where_filter = None
        if user_id is not None:
            where_filter = {"user_id": str(user_id)}
        
        results = self.collection.get(
            where=where_filter if where_filter else None,
            include=["documents", "metadatas"]
        )
        
        chunks = []
        for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
            chunk = {
                'id': results['ids'][i],
                'text': doc,
                'source': meta.get('source', 'unknown'),
                'chunk_id': int(meta.get('chunk_id', 0)),
                'user_id': int(meta.get('user_id', 0))
            }
            chunks.append(chunk)
        
        return chunks
    
    def delete_chunks(self, ids: List[str]) -> None:
        """Delete chunks by ID"""
        self.collection.delete(ids=ids)
    
    def count(self) -> int:
        """Get total number of chunks"""
        return self.collection.count()
    
    def count_chunks(self) -> int:
        """Get total number of chunks (alias for count)"""
        return self.count()
    
    def chunks(self) -> List[Dict]:
        """Get all chunks (property-like access)"""
        return self.get_all_chunks()