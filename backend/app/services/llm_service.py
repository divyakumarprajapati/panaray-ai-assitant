"""LLM service for generating responses using Hugging Face Inference API."""
import logging
import httpx
from typing import List, Dict

from ..config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating responses using LLM.
    
    Follows Single Responsibility Principle - only handles LLM inference.
    """
    
    def __init__(self):
        """Initialize the LLM service."""
        self._settings = get_settings()
        self._api_url = f"https://api-inference.huggingface.co/models/{self._settings.llm_model}"
        self._headers = {"Authorization": f"Bearer {self._settings.huggingface_api_key}"}
        logger.info(f"LLM service initialized with model: {self._settings.llm_model}")
    
    async def generate_response(
        self,
        query: str,
        context: List[Dict[str, str]],
        tone: str
    ) -> str:
        """Generate a response using retrieved context and emotion-adapted tone.
        
        Args:
            query: User's question
            context: List of relevant context documents
            tone: Tone description based on detected emotion
            
        Returns:
            Generated response string
        """
        # Build context string from retrieved documents
        context_str = self._build_context(context)
        
        # Build prompt with tone adaptation
        prompt = self._build_prompt(query, context_str, tone)
        
        # Call Hugging Face Inference API
        try:
            response = await self._call_api(prompt)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def _build_context(self, context: List[Dict[str, str]]) -> str:
        """Build context string from retrieved documents.
        
        Args:
            context: List of context documents with 'content' field
            
        Returns:
            Formatted context string
        """
        if not context:
            return "No specific information available."
        
        context_parts = []
        for i, doc in enumerate(context, 1):
            content = doc.get("content", "")
            context_parts.append(f"[{i}] {content}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str, tone: str) -> str:
        """Build the prompt for the LLM.
        
        Args:
            query: User's question
            context: Retrieved context
            tone: Tone adaptation instruction
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful assistant specialized in William O'Neil + Co. PANARAY Datagraph™.

CONTEXT:
{context}

INSTRUCTIONS:
1. Answer the question ONLY using the information provided in the CONTEXT above
2. If the context doesn't contain the answer, say "I don't have information about that in my knowledge base"
3. Be {tone} in your response
4. Keep the answer concise and accurate
5. Do not make up information or use external knowledge

QUESTION: {query}

ANSWER:"""
        
        return prompt
    
    async def _call_api(self, prompt: str) -> str:
        """Call Hugging Face Inference API.
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            Generated text
        """
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self._api_url,
                headers=self._headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
            
            return "Unable to generate response."
