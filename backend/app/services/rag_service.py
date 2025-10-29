"""RAG orchestration service combining all components."""
import logging
from typing import Dict

from .embedding_service import EmbeddingService
from .emotion_service import EmotionService
from .llm_service import LLMService
from .vector_service import VectorService
from ..models.schemas import QueryResponse, EmotionResult
from ..config import get_settings

logger = logging.getLogger(__name__)


class RAGService:
    """Orchestrates RAG pipeline with emotion adaptation.
    
    Follows Dependency Inversion Principle - depends on abstractions (services).
    Follows Open/Closed Principle - extensible without modification.
    """
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        emotion_service: EmotionService,
        llm_service: LLMService,
        vector_service: VectorService
    ):
        """Initialize RAG service with dependencies.
        
        Args:
            embedding_service: Service for generating embeddings
            emotion_service: Service for detecting emotions
            llm_service: Service for generating responses
            vector_service: Service for vector operations
        """
        self._embedding_service = embedding_service
        self._emotion_service = emotion_service
        self._llm_service = llm_service
        self._vector_service = vector_service
        self._settings = get_settings()
        logger.info("RAG service initialized")
    
    async def process_query(self, query: str) -> QueryResponse:
        """Process a user query through the RAG pipeline.
        
        Args:
            query: User's question
            
        Returns:
            QueryResponse with answer and metadata
        """
        logger.info(f"Processing query: {query[:50]}...")
        
        # Step 1: Detect emotion
        emotion_result = self._emotion_service.detect_emotion(query)
        tone = self._emotion_service.get_tone_for_emotion(emotion_result.emotion)
        logger.info(f"Detected emotion: {emotion_result.emotion} (tone: {tone})")
        
        # Step 2: Generate query embedding
        query_embedding = self._embedding_service.generate_embedding(query)
        
        # Step 3: Retrieve relevant context
        similar_docs = self._vector_service.query_similar(
            query_vector=query_embedding,
            top_k=self._settings.top_k_results
        )
        
        # Filter by similarity threshold
        filtered_docs = [
            doc for doc in similar_docs
            if doc["score"] >= self._settings.similarity_threshold
        ]
        
        logger.info(f"Retrieved {len(filtered_docs)} relevant documents")
        
        # Step 4: Prepare context
        context = [
            {"content": doc["metadata"].get("content", "")}
            for doc in filtered_docs
        ]
        
        # Step 5: Generate response with emotion-adapted tone
        answer = await self._llm_service.generate_response(
            query=query,
            context=context,
            tone=tone
        )
        
        # Calculate confidence based on retrieval scores
        confidence = self._calculate_confidence(filtered_docs)
        
        logger.info("Query processed successfully")
        
        return QueryResponse(
            answer=answer,
            emotion=emotion_result,
            sources_used=len(filtered_docs),
            confidence=confidence
        )
    
    def _calculate_confidence(self, docs: list) -> float:
        """Calculate confidence score based on retrieved documents.
        
        Args:
            docs: List of retrieved documents with scores
            
        Returns:
            Confidence score between 0 and 1
        """
        if not docs:
            return 0.0
        
        # Average similarity score of top results
        avg_score = sum(doc["score"] for doc in docs) / len(docs)
        return round(avg_score, 2)
