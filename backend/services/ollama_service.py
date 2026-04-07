"""
Ollama LLM Service
Handles local LLM requests via Ollama API (secondary backend for RAG)
Provides fallback when primary LLM services are unavailable
"""
import requests
import logging
import re
from typing import List, Optional
import time

logger = logging.getLogger(__name__)


class OllamaLLM:
    """
    Ollama-based LLM service for local RAG chatbot
    Supports various models: mistral, neural-chat, llama2, etc.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 60,
    ):
        """
        Initialize Ollama LLM service

        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
            model: Model name to use (default: mistral)
            timeout: Request timeout in seconds (default: 60s for fast responses)
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.system_prompt = self._load_system_prompt()
        self._verify_connection()

    def _load_system_prompt(self) -> str:
        """Load medical system prompt"""
        try:
            with open("prompts/medical_prompt.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return """You are a medical document assistant AI.

CRITICAL RULES:
1. Answer ONLY using the provided PDF context below
2. Be educational and informative
3. Never diagnose or prescribe treatment
4. If information is missing from the PDF, clearly state: "This information is not available in the provided document"
5. Cite which document sections you're referencing

Stay factual, helpful, and honest."""

    def _verify_connection(self) -> bool:
        """Verify Ollama service is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ Ollama service verified at {self.base_url}")
                return True
        except Exception as e:
            logger.warning(
                f"⚠ Ollama service not accessible at {self.base_url}: {str(e)}"
            )
        return False

    def check_model_available(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                if self.model in model_names:
                    logger.info(f"✓ Model '{self.model}' is available")
                    return True
                else:
                    available = ", ".join(set(model_names))
                    logger.warning(
                        f"✗ Model '{self.model}' not found. Available: {available}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error checking available models: {str(e)}")
        return False

    def pull_model(self) -> bool:
        """Pull the model from Ollama registry if not present"""
        try:
            logger.info(f"Pulling model '{self.model}' from Ollama registry...")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                timeout=self.timeout,
            )

            if response.status_code == 200:
                logger.info(f"✓ Model '{self.model}' pulled successfully")
                return True
            else:
                logger.error(f"Failed to pull model: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            return False

    def generate_response(
        self,
        question: str,
        relevant_chunks: List[str],
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate response using Ollama - OPTIMIZED FOR SPEED

        Args:
            question: User's question
            relevant_chunks: List of relevant PDF chunks (context), empty for normal mode
            max_tokens: Maximum tokens in response (256 for speed)
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Generated response string
        """
        try:
            # Determine mode
            is_rag_mode = relevant_chunks and len(relevant_chunks) > 0
            
            # Build context from chunks - limit to 3 chunks for speed
            if is_rag_mode:
                context = "\n".join([f"- {chunk[:200]}" for chunk in relevant_chunks[:3]])
                # RAG Mode - with documents
                prompt = f"""You are a medical document assistant. Use ONLY the documents below to answer.

QUESTION: {question}

DOCUMENTS:
{context}

ANSWER:"""
            else:
                # Normal Mode - general knowledge, NO document references
                prompt = f"""Answer this question using general knowledge. Do NOT mention documents or context. Be concise.

QUESTION: {question}

ANSWER:"""

            mode_str = "RAG" if is_rag_mode else "NORMAL"
            logger.info(f"[Ollama] Mode: {mode_str} | Model: {self.model} | Tokens: {max_tokens}")

            # Make request to Ollama with OPTIMIZED settings for speed
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_k": 40,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                },
                timeout=self.timeout,
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                original_text = generated_text  # For logging

                # AGGRESSIVE response cleaning - multiple passes
                # Pass 1: Remove leading common prefixes
                unwanted_prefixes = [
                    "based on the documents:",
                    "based on the document:",
                    "according to the document:",
                    "according to the documents:",
                    "from the documents:",
                    "from the document:",
                    "answer:",
                    "response:",
                    "question:",
                    "a:",
                ]
                
                for prefix in unwanted_prefixes:
                    if generated_text.lower().startswith(prefix):
                        old_len = len(generated_text)
                        generated_text = generated_text[len(prefix):].strip()
                        logger.debug(f"[Ollama] Removed leading prefix '{prefix}' ({old_len} → {len(generated_text)} chars)")
                        break
                
                # Pass 2: Remove all embedded occurrences of document-related phrases (case-insensitive)
                # Only if NOT in RAG mode - in normal mode, no mention of documents should exist
                if not is_rag_mode:
                    embedded_phrases = [
                        "based on the documents",
                        "based on the document",
                        "according to the documents",
                        "according to the document",
                        "in the documents",
                        "in the document",
                        "the document states",
                        "the documents state",
                        "the pdf",
                        "provided document",
                    ]
                    
                    for phrase in embedded_phrases:
                        if phrase.lower() in generated_text.lower():
                            # Remove all occurrences of this phrase (case-insensitive)
                            import re
                            old_len = len(generated_text)
                            generated_text = re.sub(
                                re.escape(phrase),
                                "",
                                generated_text,
                                flags=re.IGNORECASE
                            ).strip()
                            if len(generated_text) < old_len:
                                logger.debug(f"[Ollama] Removed embedded phrase '{phrase}' ({old_len} → {len(generated_text)} chars)")
                
                # Pass 3: Clean up any double spaces created by removal
                generated_text = " ".join(generated_text.split())
                
                # Pass 4: Remove leading punctuation and whitespace
                generated_text = generated_text.lstrip("?:;-\n ").strip()

                # Validate response
                if not generated_text:
                    logger.warning("[Ollama] Empty response received after cleaning")
                    return "Unable to generate response. Please try again."

                if len(generated_text) > len(original_text) * 0.1:  # Check if useful content remains
                    logger.info(
                        f"[Ollama] ✓ {mode_str} Response generated "
                        f"({len(original_text)} → {len(generated_text)} chars after cleaning)"
                    )
                    return generated_text
                else:
                    logger.warning(f"[Ollama] Response cleaned to insignificant length: {len(generated_text)} chars")
                    return "Unable to generate meaningful response. Please try again."
            else:
                # Log the full error response for debugging
                error_detail = response.text if response.text else f"HTTP {response.status_code}"
                logger.error(f"[Ollama] API Error: {response.status_code}")
                logger.error(f"[Ollama] Response: {error_detail}")
                
                # Check for specific error conditions
                if "memory" in error_detail.lower() or "ram" in error_detail.lower():
                    logger.error("[Ollama] Memory error - insufficient system RAM for model execution")
                    return "Ollama model requires more memory than available. Free up system memory and try again, or restart Ollama."
                elif response.status_code == 0 or "Connection" in response.text:
                    return "Ollama service is not running. Please start Ollama first."
                elif "not found" in response.text.lower() or response.status_code == 404:
                    return f"Model '{self.model}' not found in Ollama. Please pull it first."
                else:
                    return f"Error generating response from Ollama service: {response.status_code}"

        except requests.exceptions.ConnectionError:
            logger.error(f"[Ollama] Connection error - Ollama service at {self.base_url} is not accessible")
            return "Cannot connect to Ollama service. Is it running?"
        except requests.exceptions.Timeout:
            logger.error("[Ollama] Request timed out")
            return "Response generation timed out. Please try again."
        except Exception as e:
            logger.error(f"[Ollama] Unexpected error: {str(e)}", exc_info=True)
            return f"Error generating response: {str(e)}"

    def generate_response_stream(
        self,
        question: str,
        relevant_chunks: List[str],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ):
        """
        Generate streaming response using Ollama (for real-time responses)

        Args:
            question: User's question
            relevant_chunks: List of relevant PDF chunks
            max_tokens: Maximum tokens
            temperature: Sampling temperature

        Yields:
            Chunks of generated text
        """
        try:
            context = "\n".join([f"- {chunk}" for chunk in relevant_chunks])

            prompt = f"""{self.system_prompt}

QUESTION: {question}

CONTEXT FROM DOCUMENTS:
{context}

ANSWER:"""

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
                timeout=self.timeout,
                stream=True,
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = eval(line)  # Parse JSON line
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                        except Exception as e:
                            logger.debug(f"Error parsing stream chunk: {e}")
            else:
                logger.error(f"Ollama streaming error: {response.status_code}")
                yield "Error generating streaming response."

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"Error: {str(e)}"

    def get_model_info(self) -> dict:
        """Get information about the current model"""
        try:
            response = requests.get(f"{self.base_url}/api/show", 
                                   json={"name": self.model},
                                   timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
        
        return {"model": self.model, "status": "unknown"}
