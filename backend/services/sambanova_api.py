"""
SambaNova API Service
Handles LLM API calls and prompt management for RAG chatbot and question generation
"""
import time
import json
from sambanova import SambaNova
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Lazy import to avoid circular imports
_local_llm = None

def get_local_llm():
    """Get LocalLLM instance (lazy import)"""
    global _local_llm
    if _local_llm is None:
        try:
            from services.local_llm import LocalLLM
            _local_llm = LocalLLM()
        except Exception as e:
            logger.error(f"Could not import LocalLLM: {e}")
            _local_llm = False
    return _local_llm if _local_llm else None


class SambanovaLLM:
    def __init__(self, api_key: str, api_url: str):
        """
        Initialize SambaNova LLM service
        api_key: SambaNova API key
        api_url: SambaNova API base URL
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.client = SambaNova(
            api_key=api_key,
            base_url=self.api_url
        )
        self.system_prompt = self._load_system_prompt()
        self.question_generation_prompt = self._load_question_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load medical system prompt - requesting CONCISE answers"""
        try:
            with open("prompts/medical_prompt.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            # Fallback prompt - MINIMAL to avoid tokenization issues
            return "You are a medical assistant. Answer using context provided. Keep answers short."
    
    def _load_question_prompt(self) -> str:
        """Load question generation system prompt"""
        return """You are an expert medical educator specializing in creating comprehensive study questions.
Your role is to generate high-quality practice questions that:
- Test deep understanding of medical concepts
- Are clinically relevant and practical
- Have clear, unambiguous answers
- Include appropriate difficulty levels
- Promote critical thinking

Format your response as valid JSON ONLY."""

    def _make_api_call(self, messages, max_tokens, temperature, retry_count=0, max_retries=5):
        """
        Make API call with exponential backoff retry for rate limits
        """
        try:
            response = self.client.chat.completions.create(
                model="Llama-4-Maverick-17B-128E-Instruct",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95
            )
            return response
        
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    print(f"⏳ Rate limited. Retrying in {wait_time}s (attempt {retry_count + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    return self._make_api_call(messages, max_tokens, temperature, retry_count + 1, max_retries)
                else:
                    raise Exception(f"Rate limit exceeded after {max_retries} retries")
            else:
                raise
    
    def _local_fallback_response(self, relevant_chunks: List[str], question: str) -> str:
        """
        Generate concise response from chunks directly without API call
        Used as fallback when API is rate limited
        """
        # Extract key sentences instead of full chunks
        key_points = []
        for chunk in relevant_chunks[:2]:  # Just use first 2 chunks
            # Get first sentence or first 100 chars
            text = chunk[:150].split('.')[0] + '.'
            if text and text not in key_points:
                key_points.append(text)
        
        context = " ".join(key_points)
        
        fallback_response = f"Based on the documents: {context}"
        
        return fallback_response
    
    def generate_response(
        self,
        question: str,
        relevant_chunks: List[str],
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response using SambaNova LLM
        
        Args:
            question: User's question
            relevant_chunks: List of relevant PDF chunks (context)
            max_tokens: Maximum response length
            temperature: Response creativity (0-1)
        
        Returns: Generated response text
        """
        # Validate and clean chunks - be very aggressive
        clean_chunks = []
        for chunk in relevant_chunks:
            if isinstance(chunk, str) and chunk.strip():
                # Remove problematic characters
                clean_text = chunk.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                # Remove multiple spaces
                clean_text = ' '.join(clean_text.split())
                if clean_text.strip():
                    clean_chunks.append(clean_text[:800])  # Limit chunk more
        
        if not clean_chunks:
            # If no chunks, use fallback
            return self._local_fallback_response(relevant_chunks, question)
        
        # Build context from chunks with strict limit
        context = " ".join(clean_chunks[:3])[:1500]  # Only 3 chunks, max 1500 chars
        
        # Validate question - clean it too
        clean_question = question.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        clean_question = ' '.join(clean_question.split()).strip()
        if not clean_question:
            raise Exception("Invalid question")
        
        try:
            # Call SambaNova API with very simple message format
            # Use single combined message to avoid format issues
            combined_content = f"Context: {context}\n\nQuestion: {clean_question}\n\nAnswer:"
            
            response = self._make_api_call(
                messages=[
                    {"role": "user", "content": combined_content}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response text
            if response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content.strip()
                return response_text
            else:
                raise Exception("Invalid response format from SambaNova API")
        
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() or "429" in error_str:
                print(f"[WARN] API rate limited, trying local fallback...")
                local_llm = get_local_llm()
                if local_llm:
                    try:
                        return local_llm.generate_response(
                            question=question,
                            relevant_chunks=relevant_chunks[:3],
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                    except Exception as local_e:
                        print(f"[ERROR] Local fallback also failed: {local_e}")
                        return self._local_fallback_response(relevant_chunks, question)
                else:
                    return self._local_fallback_response(relevant_chunks, question)
            elif "tokenize" in error_str.lower() or "400" in error_str:
                # Tokenization error - try local fallback
                print(f"[WARN] SambaNova tokenization error, trying local fallback...")
                local_llm = get_local_llm()
                if local_llm:
                    try:
                        return local_llm.generate_response(
                            question=question,
                            relevant_chunks=relevant_chunks[:3],
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                    except Exception as local_e:
                        print(f"[ERROR] Local fallback also failed: {local_e}")
                        return self._local_fallback_response(relevant_chunks, question)
                else:
                    return self._local_fallback_response(relevant_chunks, question)
            else:
                print(f"[ERROR] SambaNova API error: {str(e)}")
                raise
    
    def summarize_context(
        self,
        relevant_chunks: List[str],
        question: str
    ) -> str:
        """
        Generate a concise summary of the retrieved chunks
        Used when full context would exceed token limits
        
        Args:
            relevant_chunks: List of relevant PDF chunks
            question: User's question to guide summary focus
        
        Returns: Summarized context
        """
        context = "\n\n---\n\n".join(relevant_chunks)
        
        summary_prompt = f"""Please provide a brief, relevant summary of this medical content that addresses the question:

QUESTION: {question}

CONTENT TO SUMMARIZE:
{context}

SUMMARY (concise, key points only):"""
        
        try:
            response = self._make_api_call(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise medical summarizer. Extract only the key information relevant to the user's question."
                    },
                    {
                        "role": "user",
                        "content": summary_prompt
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                return "\n\n---\n\n".join(relevant_chunks)
        
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() or "429" in error_str:
                print(f"[WARN] Summary API rate limited, returning original chunks...")
                return "\n\n---\n\n".join(relevant_chunks)
            else:
                print(f"[WARN] Summary generation failed: {str(e)}, using original context")
                return "\n\n---\n\n".join(relevant_chunks)
    
    def format_context(self, chunks: List[Dict]) -> List[str]:
        """
        Format chunks for inclusion in prompt
        
        Args:
            chunks: List of chunk dicts with 'text', 'source', 'distance'
        
        Returns: List of formatted context strings
        """
        formatted = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("source", "unknown")
            distance = chunk.get("distance", 0)
            text = chunk.get("text", "")
            
            formatted_chunk = f"[Source: {source} | Relevance: {100 - distance:.1f}%]\n{text}"
            formatted.append(formatted_chunk)
        
        return formatted    
    def generate_questions(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "mixed",
        question_type: str = "mixed",
        book_content: Optional[str] = None,
        max_tokens: int = 2048
    ) -> List[Dict]:
        """
        Generate study questions using SambaNova AI
        
        Args:
            topic: Topic to generate questions about
            num_questions: Number of questions to generate
            difficulty: easy, medium, hard, or mixed
            question_type: multiple_choice, true_false, short_answer, essay, or mixed
            book_content: Optional book content to base questions on
            max_tokens: Maximum response tokens
        
        Returns: List of question dictionaries
        """
        try:
            # Build the prompt
            content_context = ""
            if book_content:
                # Limit content to avoid token overload
                content_context = f"\nBased on the following medical content:\n---\n{book_content[:3000]}\n---\n"
            
            prompt = f"""{content_context}
Generate exactly {num_questions} MEDICAL study questions about "{topic}".

Requirements:
- Difficulty levels: {difficulty}
- Question types: {question_type}
- Each question must have clear, unambiguous answers
- Include clinical relevance where applicable
- Provide explanation for each answer

Format your response as valid JSON array with this structure:
[
  {{
    "question": "question text",
    "type": "multiple_choice|true_false|short_answer|essay",
    "difficulty": "easy|medium|hard",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],  // for multiple_choice only
    "correct_answer": "text answer or 'A'",
    "explanation": "why this answer is correct"
  }}
]

IMPORTANT: Return ONLY valid JSON, no markdown, no extra text."""
            
            logger.info(f"Generating {num_questions} {difficulty} {question_type} questions about '{topic}'")
            
            response = self._make_api_call(
                messages=[
                    {
                        "role": "system",
                        "content": self.question_generation_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.5  # Moderate temp for structured questions
            )
            
            if response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content.strip()
                
                # Parse JSON response
                try:
                    # Try to extract JSON if wrapped in markdown
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                    questions = json.loads(response_text)
                    logger.info(f"✓ Generated {len(questions)} questions using SambaNova")
                    return questions
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse question JSON: {str(e)}")
                    logger.error(f"Response was: {response_text[:500]}")
                    raise ValueError(f"Invalid JSON response from SambaNova API: {str(e)}")
            else:
                raise ValueError("No response from SambaNova API")
        
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() or "429" in error_str:
                logger.warning(f"Rate limited during question generation: {str(e)}")
                raise Exception("API rate limit exceeded. Please try again in a moment.")
            else:
                logger.error(f"Question generation error: {str(e)}")
                raise
    
    def extract_json_from_response(self, response_text: str) -> Dict:
        """
        Extract JSON from API response, handling markdown and formatting variations
        
        Args:
            response_text: Raw response text from API
        
        Returns: Parsed JSON dictionary
        """
        try:
            # Try direct parse first
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try removing markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # Try to find JSON array or object
            import re
            json_match = re.search(r'\{.*\}|\[.*\]', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            raise ValueError(f"Could not extract JSON from response: {str(e)}")