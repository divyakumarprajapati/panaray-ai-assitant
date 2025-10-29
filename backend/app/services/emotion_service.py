"""Emotion detection service using Hugging Face transformers."""
import logging
from typing import Dict
from transformers import pipeline

from ..config import get_settings
from ..models.schemas import EmotionResult

logger = logging.getLogger(__name__)


class EmotionService:
    """Service for detecting emotions in text.
    
    Follows Single Responsibility Principle - only handles emotion detection.
    """
    
    # Emotion to tone mapping for response adaptation
    EMOTION_TO_TONE = {
        "joy": "enthusiastic and positive",
        "sadness": "empathetic and supportive",
        "anger": "calm and understanding",
        "fear": "reassuring and gentle",
        "surprise": "informative and clear",
        "love": "warm and friendly",
        "neutral": "professional and straightforward"
    }
    
    def __init__(self):
        """Initialize the emotion classification model."""
        settings = get_settings()
        logger.info(f"Loading emotion model: {settings.emotion_model}")
        self._classifier = pipeline(
            "text-classification",
            model=settings.emotion_model,
            top_k=1
        )
        logger.info("Emotion model loaded successfully")
    
    def detect_emotion(self, text: str) -> EmotionResult:
        """Detect the primary emotion in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            EmotionResult with detected emotion and confidence
        """
        results = self._classifier(text[:512])  # Limit text length
        
        if results and len(results[0]) > 0:
            top_result = results[0][0]
            emotion = top_result["label"].lower()
            confidence = top_result["score"]
            
            logger.debug(f"Detected emotion: {emotion} (confidence: {confidence:.2f})")
            return EmotionResult(emotion=emotion, confidence=confidence)
        
        # Fallback to neutral
        return EmotionResult(emotion="neutral", confidence=1.0)
    
    def get_tone_for_emotion(self, emotion: str) -> str:
        """Get the appropriate response tone for an emotion.
        
        Args:
            emotion: Detected emotion label
            
        Returns:
            Description of tone to use in response
        """
        return self.EMOTION_TO_TONE.get(emotion, self.EMOTION_TO_TONE["neutral"])
