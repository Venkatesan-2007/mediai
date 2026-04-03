"""
Simple TF-IDF Embeddings Service
Uses sklearn for embeddings - more lightweight than sentence-transformers
No heavy dependencies needed
"""
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

class SimpleEmbeddingsService:
    """
    Simple TF-IDF based embeddings using sklearn
    Lightweight alternative to sentence-transformers
    """
    
    def __init__(self, vocab_path="database/tfidf_vectorizer.pkl"):
        """Initialize TF-IDF vectorizer"""
        self.vocab_path = vocab_path
        self.vectorizer = None
        self.all_embeddings = []
        
        # Load existing vectorizer if available
        if os.path.exists(vocab_path):
            try:
                with open(vocab_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                print("[OK] Loaded existing TF-IDF vectorizer")
            except Exception as e:
                print(f"Warning: Could not load vectorizer: {e}")
                self.vectorizer = None
        
        if self.vectorizer is None:
            # Create new vectorizer with common medical terms
            # Use 384 dimensions to match MiniLM embeddings (for compatibility)
            self.vectorizer = TfidfVectorizer(
                max_features=384,
                stop_words='english',
                lowercase=True,
                ngram_range=(1, 2),
                min_df=1
            )
            print("[OK] Initialized new TF-IDF vectorizer")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Convert text to embedding vector using TF-IDF
        Returns: List of floats representing the embedding
        """
        try:
            if self.vectorizer is None:
                raise Exception("Vectorizer not initialized")
            
            # Transform text to TF-IDF vector
            embedding = self.vectorizer.transform([text]).toarray()[0]
            return embedding.tolist()
        except Exception as e:
            print(f"[ERROR] Error creating embedding: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[dict]) -> List[dict]:
        """
        Embed all chunks using TF-IDF
        Adds 'embedding' field to each chunk
        """
        embedded_chunks = []
        
        # Fit vectorizer on all chunk texts if not already fitted
        if hasattr(self.vectorizer, 'vocabulary_') and len(self.vectorizer.vocabulary_) == 0:
            texts = [chunk["text"] for chunk in chunks]
            self.vectorizer.fit(texts)
            # Save vectorizer
            try:
                os.makedirs("database", exist_ok=True)
                with open(self.vocab_path, 'wb') as f:
                    pickle.dump(self.vectorizer, f)
                print("[OK] Saved TF-IDF vectorizer")
            except Exception as e:
                print(f"Warning: Could not save vectorizer: {e}")
        
        for i, chunk in enumerate(chunks):
            try:
                embedding = self.embed_text(chunk["text"])
                chunk["embedding"] = embedding
                embedded_chunks.append(chunk)
                
                if (i + 1) % 10 == 0:
                    print(f"[OK] Embedded {i + 1}/{len(chunks)} chunks")
            
            except Exception as e:
                print(f"[ERROR] Error embedding chunk {chunk.get('chunk_id', i)}: {str(e)}")
                continue
        
        print(f"[OK] Successfully embedded {len(embedded_chunks)}/{len(chunks)} chunks")
        return embedded_chunks
