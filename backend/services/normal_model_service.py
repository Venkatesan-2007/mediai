"""
Normal Model Service
Handles pure general knowledge responses without any document context
Dedicated service to ensure clean separation from RAG mode
"""
import requests
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class NormalModelService:
    """
    Dedicated service for Normal Mode (General Knowledge)
    Generates responses using only model knowledge, NO documents
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 60,
    ):
        """
        Initialize Normal Model Service

        Args:
            base_url: Ollama API base URL
            model: Model name (mistral, neural-chat, etc.)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._verify_connection()

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

    def generate_response(
        self,
        question: str,
        max_tokens: int = 256,
        temperature: float = 0.5,
    ) -> str:
        """
        Generate response using ONLY general knowledge (NO documents)

        Args:
            question: User's question
            max_tokens: Maximum tokens in response (256 for speed)
            temperature: Sampling temperature (0.0-1.0), lower for focused answers

        Returns:
            Generated response string (cleaned, no document references)
        """
        try:
            # Build prompt explicitly telling model NOT to mention documents
            prompt = f"""Answer this question using general knowledge. Be concise and direct.

IMPORTANT: Do NOT mention documents, PDFs, provided context, or any references to files.
Do NOT say "Based on the documents" or similar phrases.
Just provide a clear, direct answer.

QUESTION: {question}

ANSWER:"""

            logger.info(f"[NORMAL MODE] Generating response | Model: {self.model} | Tokens: {max_tokens}")
            logger.debug(f"[NORMAL MODE] Prompt: {prompt[:100]}...")

            # Call Ollama API
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
                original_length = len(generated_text)

                logger.debug(f"[NORMAL MODE] Raw response ({original_length} chars): {generated_text[:100]}...")

                # AGGRESSIVE CLEANING - Multiple passes to remove ANY document references
                generated_text = self._clean_response(generated_text)

                final_length = len(generated_text)
                logger.info(
                    f"[NORMAL MODE] ✓ Response cleaned ({original_length} → {final_length} chars)"
                )

                if not generated_text:
                    logger.warning("[NORMAL MODE] Empty response after cleaning")
                    return "Unable to generate response. Please try again."

                return generated_text
            else:
                logger.error(f"[NORMAL MODE] Ollama error: {response.status_code} - {response.text}")
                return "Error generating response from Ollama service."

        except requests.exceptions.Timeout:
            logger.error("[NORMAL MODE] Request timed out")
            return "Response generation timed out. Please try again."
        except Exception as e:
            logger.error(f"[NORMAL MODE] Generation error: {str(e)}", exc_info=True)
            return f"Error: Unable to generate response - {str(e)}"

    def _clean_response(self, text: str) -> str:
        """
        Aggressively clean response to remove ALL document references
        
        Args:
            text: Raw response from Ollama
            
        Returns:
            Cleaned response
        """
        if not text:
            return text

        original_text = text

        # ============================================
        # PASS 1: Remove leading unwanted prefixes
        # ============================================
        leading_prefixes = [
            "based on the document",
            "based on the documents",
            "according to the document",
            "according to the documents",
            "from the document",
            "from the documents",
            "the document states",
            "the documents state",
            "this document",
            "these documents",
            "answer:",
            "response:",
            "a:",
        ]

        for prefix in leading_prefixes:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
                logger.debug(f"[NORMAL MODE] Removed leading prefix: '{prefix}'")
                break

        # ============================================
        # PASS 2: Remove ALL embedded document phrases
        # ============================================
        embedded_phrases = [
            r"based on the document[s]?",
            r"according to the document[s]?",
            r"based on\s+(?:the\s+)?document[s]?",
            r"according to\s+(?:the\s+)?document[s]?",
            r"in the document[s]?",
            r"from the document[s]?",
            r"the provided document[s]?",
            r"provided pdf",
            r"(?:the\s+)?pdf",
            r"the\s+(?:uploaded\s+)?document[s]?",
            r"document reference",
            r"source document",
        ]

        for pattern in embedded_phrases:
            if re.search(pattern, text, re.IGNORECASE):
                old_length = len(text)
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)
                new_length = len(text)
                if new_length < old_length:
                    logger.debug(f"[NORMAL MODE] Removed phrase pattern: '{pattern}' ({old_length} → {new_length})")

        # ============================================
        # PASS 3: Remove phrases starting sentences
        # ============================================
        sentence_patterns = [
            r"^\s*(?:Based|According|From|In|The)\s+(?:on\s+)?(?:the\s+)?document[s]?\s*:?\s*",
            r"^\s*(?:This|These)\s+document[s]?\s+(?:state|show|indicate|suggest)[s]?\s*:?\s*",
        ]

        for pattern in sentence_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
                logger.debug(f"[NORMAL MODE] Removed sentence pattern: '{pattern}'")

        # ============================================
        # PASS 4: Normalize whitespace
        # ============================================
        text = " ".join(text.split())
        text = re.sub(r"\s+", " ", text)

        # ============================================
        # PASS 5: Remove leading punctuation and markers
        # ============================================
        text = text.lstrip("?:;-•*\n ").strip()

        # ============================================
        # PASS 6: Final validation
        # ============================================
        if len(text) < 10:
            logger.warning(f"[NORMAL MODE] Response too short after cleaning: {len(text)} chars")
            return ""

        # Check if any document reference remains
        forbidden_keywords = [
            "based on",
            "according to",
            "document",
            "provided",
            "pdf",
            "uploaded",
        ]

        text_lower = text.lower()
        found_keywords = [kw for kw in forbidden_keywords if f" {kw} " in f" {text_lower} "]

        if found_keywords:
            logger.warning(f"[NORMAL MODE] Found forbidden keywords after cleaning: {found_keywords}")
            logger.warning(f"[NORMAL MODE] Response: {text[:100]}...")

        logger.info(
            f"[NORMAL MODE] Final cleaned response ({len(original_text)} → {len(text)} chars)"
        )
        return text
