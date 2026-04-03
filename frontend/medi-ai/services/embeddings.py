"""
Embeddings Service
Calls SambaNova API to convert text to vectors
"""
import requests
from typing import List
import os


class EmbeddingsService:
    def __init__(self, api_key: str, api_url: str):
        """
        Initialize embeddings service
        api_key: SambaNova API key
        api_url: SambaNova API base URL
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def embed_text(self, text: str) -> List[float]:
        """
        Convert text to embedding vector via SambaNova API
        Returns: List of floats representing the embedding
        """
        try:
            # SambaNova embeddings endpoint
            endpoint = f"{self.api_url}/embeddings"
            
            payload = {
                "model": "embeddings",
                "input": text
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"SambaNova API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Extract embedding from response
            if "data" in data and len(data["data"]) > 0:
                embedding = data["data"][0]["embedding"]
                return embedding
            else:
                raise Exception("Invalid response format from SambaNova API")
        
        except requests.RequestException as e:
            print(f"✗ Request error: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[dict]) -> List[dict]:
        """
        Embed all chunks
        Adds 'embedding' field to each chunk
        """
        embedded_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                embedding = self.embed_text(chunk["text"])
                chunk["embedding"] = embedding
                embedded_chunks.append(chunk)
                
                if (i + 1) % 10 == 0:
                    print(f"✓ Embedded {i + 1}/{len(chunks)} chunks")
            
            except Exception as e:
                print(f"✗ Error embedding chunk {chunk['chunk_id']}: {str(e)}")
                continue
        
        print(f"✓ Successfully embedded {len(embedded_chunks)}/{len(chunks)} chunks")
        return embedded_chunks
