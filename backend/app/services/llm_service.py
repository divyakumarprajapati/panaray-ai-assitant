"""LLM service using direct Hugging Face API calls for response generation."""
import logging
from typing import List, Dict
import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating responses using direct Hugging Face API calls.
    
    Follows Single Responsibility Principle - only handles LLM inference.
    Uses httpx for async HTTP calls to Hugging Face Inference API.
    """
    
    def __init__(self):
        """Initialize the LLM service with direct API access."""
        self._settings = get_settings()
        logger.info(f"Initializing LLM service with direct API: {self._settings.llm_model}")
        
        # Hugging Face API endpoint
        self._api_url = f"https://api-inference.huggingface.co/models/{self._settings.llm_model}"
        self._headers = {
            "Authorization": f"Bearer {self._settings.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        # LLM parameters
        self._temperature = 0.7
        self._max_new_tokens = 300
        self._top_p = 0.9
        
        logger.info("LLM service initialized successfully with direct API")
    
    def _create_prompt(self, context: str, tone: str, query: str) -> str:
        """Create the prompt for RAG.
        
        Args:
            context: Formatted context string
            tone: Tone description based on detected emotion
            query: User's question
            
        Returns:
            Formatted prompt string
        """
        template = f"""You are a helpful assistant specialized in William O'Neil + Co. PANARAY Datagraph™.

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
        return template
    
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
        
        # Create prompt
        prompt = self._create_prompt(context_str, tone, query)
        
        # Call Hugging Face API directly
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "temperature": self._temperature,
                        "max_new_tokens": self._max_new_tokens,
                        "top_p": self._top_p,
                        "return_full_text": False
                    }
                }
                
                response = await client.post(
                    self._api_url,
                    headers=self._headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract generated text from response
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "")
                else:
                    generated_text = str(result)
                
                return generated_text.strip()
                
        except httpx.TimeoutException:
            logger.error("Timeout calling Hugging Face API")
            return "I apologize, but the request timed out. Please try again."
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Hugging Face API: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
        except Exception as e:
            logger.error(f"Error generating response via direct API: {e}")
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
