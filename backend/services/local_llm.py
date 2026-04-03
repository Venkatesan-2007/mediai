"""
Local LLM Service
Uses transformers to generate responses locally (no API needed)
This is a lightweight solution for medical QA contexts
"""
from typing import List, Dict
import os

class LocalLLM:
    def __init__(self):
        """
        Initialize local LLM service
        Uses text-summarization or simple context-based generation
        """
        self.system_prompt = self._load_system_prompt()
    
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
    
    def generate_response(
        self,
        question: str,
        relevant_chunks: List[str],
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response based on relevant chunks
        Uses heuristic-based summarization
        
        Args:
            question: User's question
            relevant_chunks: List of relevant PDF chunks (context)
            max_tokens: Maximum response length
            temperature: (ignored for local generation)
        
        Returns: Generated response text
        """
        try:
            # Build context from chunks
            context = "\n\n---\n\n".join(relevant_chunks)
            
            # Generate response using pattern matching on chunks
            response = self._generate_from_context(question, relevant_chunks)
            
            return response
        
        except Exception as e:
            print(f"✗ Error in local LLM: {str(e)}")
            raise
    
    def _generate_from_context(self, question: str, chunks: List[str]) -> str:
        """
        Generate response by analyzing chunks
        Uses extractive summarization approach
        """
        # Extract key sentences from chunks that relate to the question
        question_words = set(question.lower().split())
        
        # Score sentences based on keyword relevance
        scored_sentences = []
        for chunk in chunks:
            sentences = chunk.split('.')
            for sentence in sentences:
                if sentence.strip():
                    # Score based on question keyword matches
                    words_in_sentence = set(sentence.lower().split())
                    overlap = len(question_words & words_in_sentence)
                    if overlap > 0:
                        scored_sentences.append((sentence.strip(), overlap))
        
        # Sort by score and take top ones
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in scored_sentences[:5]]
        
        if top_sentences:
            # Build response from top sentences
            response = "Based on the provided documents:\n\n"
            response += " ".join(top_sentences)
            
            if len(response) > 200:
                response = response[:200] + "..."
            
            return response
        else:
            return "The provided documents do not contain specific information about this question. Please provide more context or related documents."
    
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
    
    def summarize_context(self, chunks: List[str], question: str) -> str:
        """
        Summarize context for token-limited scenarios
        
        Args:
            chunks: List of context strings
            question: User's question
        
        Returns: Summarized context
        """
        # Combine and summarize chunks
        context = "\n\n".join(chunks)
        
        # Simple extractive summarization
        sentences = context.split('.')
        important_sentences = []
        
        question_words = set(question.lower().split())
        for sentence in sentences:
            if sentence.strip():
                sentence_words = set(sentence.lower().split())
                overlap = len(question_words & sentence_words)
                if overlap > 0:
                    important_sentences.append(sentence.strip())
        
        if important_sentences:
            return ". ".join(important_sentences[:3]) + "."
        else:
            # Return first 200 chars of context as fallback
            return context[:200] + "..." if len(context) > 200 else context
    
    def _local_fallback_response(self, chunks: List[str], question: str) -> str:
        """
        Local fallback response when API calls fail
        
        Args:
            chunks: List of context strings
            question: User's question
        
        Returns: Generated response
        """
        if not chunks:
            return f"I don't have enough information to answer: {question[:100]}"
        
        # Build response from available chunks
        context = "\n\n".join(chunks)
        
        # Extract most relevant sentences
        sentences = context.split('.')
        relevant_sentences = []
        
        question_words = set(question.lower().split())
        for sentence in sentences:
            if sentence.strip() and len(sentence.strip()) > 10:
                sentence_words = set(sentence.lower().split())
                overlap = len(question_words & sentence_words)
                if overlap >= 2:  # At least 2 matching words
                    relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            response = "Based on the available documents:\n\n"
            response += ". ".join(relevant_sentences[:5]) + "."
            return response
        else:
            return f"The documents provided do not directly address: {question[:100]}. Please refine your question or provide additional documents."
