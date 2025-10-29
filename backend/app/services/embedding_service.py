"""Embedding generation service using Sentence Transformers."""
import logging
from typing import List
from sentence_transformers import SentenceTransformer

from ..config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings.
    
    Follows Single Responsibility Principle - only handles embedding generation.
    """
    
    def __init__(self):
        """Initialize the embedding model."""
        settings = get_settings()
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self._model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        embedding = self._model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self._model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
        return [emb.tolist() for emb in embeddings]
