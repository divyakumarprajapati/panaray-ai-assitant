"""LLM service using LangChain for response generation."""
import logging
from typing import List, Dict
from langchain_community.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from ..config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating responses using LangChain LLM wrappers.
    
    Follows Single Responsibility Principle - only handles LLM inference.
    Now using LangChain's HuggingFaceHub integration for better composability.
    """
    
    def __init__(self):
        """Initialize the LLM service with LangChain."""
        self._settings = get_settings()
        logger.info(f"Initializing LLM service via LangChain: {self._settings.llm_model}")
        
        # Validate API key
        if not self._settings.huggingface_api_key:
            error_msg = (
                "HuggingFace API key is not configured. "
                "Please set HUGGINGFACE_API_KEY in your .env file or environment variables. "
                "Get your API key from https://huggingface.co/settings/tokens"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Initialize LangChain HuggingFace LLM
        self._llm = HuggingFaceHub(
            repo_id=self._settings.llm_model,
            huggingfacehub_api_token=self._settings.huggingface_api_key,
            model_kwargs={
                "temperature": 0.7,
                "max_new_tokens": 300,
                "top_p": 0.9,
                "return_full_text": False
            }
        )
        
        # Create prompt template
        self._prompt_template = self._create_prompt_template()
        
        # Create LLM chain
        self._chain = LLMChain(
            llm=self._llm,
            prompt=self._prompt_template,
            verbose=False
        )
        
        logger.info("LLM service initialized successfully with LangChain")
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create the prompt template for RAG.
        
        Returns:
            LangChain PromptTemplate instance
        """
        template = """You are a helpful assistant specialized in William O'Neil + Co. PANARAY Datagraph™.

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
        
        return PromptTemplate(
            input_variables=["context", "tone", "query"],
            template=template
        )
    
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
        
        # Generate response using LangChain
        try:
            # Use the chain with await for async support
            response = await self._chain.arun(
                context=context_str,
                tone=tone,
                query=query
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating response via LangChain: {e}")
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
    
    @property
    def llm(self):
        """Get the underlying LangChain LLM object.
        
        Returns:
            LangChain LLM instance
        """
        return self._llm
    
    @property
    def chain(self):
        """Get the LangChain chain object.
        
        Returns:
            LangChain LLMChain instance
        """
        return self._chain
