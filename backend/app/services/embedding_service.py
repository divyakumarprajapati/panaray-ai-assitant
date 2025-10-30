"""Embedding generation service using LangChain HuggingFaceEmbeddings."""
import logging
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings

from ..config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using LangChain.
    
    Follows Single Responsibility Principle - only handles embedding generation.
    Now using LangChain's HuggingFaceEmbeddings for better integration.
    """
    
    def __init__(self):
        """Initialize the embedding model using LangChain."""
        settings = get_settings()
        logger.info(f"Loading embedding model via LangChain: {settings.embedding_model}")
        
        # Initialize LangChain HuggingFace Embeddings
        self._embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        logger.info("Embedding model loaded successfully via LangChain")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        # LangChain's embed_query method for single text
        embedding = self._embeddings.embed_query(text)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # LangChain's embed_documents method for batch processing
        embeddings = self._embeddings.embed_documents(texts)
        return embeddings
    
    @property
    def embeddings(self):
        """Get the underlying LangChain embeddings object.
        
        Returns:
            LangChain HuggingFaceEmbeddings instance
        """
        return self._embeddings
