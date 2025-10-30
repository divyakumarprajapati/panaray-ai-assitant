"""Emotion detection service using HuggingFace Inference API."""
import logging
from typing import Dict
import httpx

from ..config import get_settings
from ..models.schemas import EmotionResult

logger = logging.getLogger(__name__)


class EmotionService:
    """Service for detecting emotions in text using HuggingFace Inference API.
    
    Follows Single Responsibility Principle - only handles emotion detection.
    Now uses HuggingFace Inference API instead of local transformers/torch.
    This eliminates the need for heavy ML dependencies.
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
        """Initialize the emotion classification service."""
        self._settings = get_settings()
        self._api_url = f"https://api-inference.huggingface.co/models/{self._settings.emotion_model}"
        self._headers = {"Authorization": f"Bearer {self._settings.huggingface_api_key}"}
        logger.info(f"Emotion service initialized with model: {self._settings.emotion_model}")
    
    def detect_emotion(self, text: str) -> EmotionResult:
        """Detect the primary emotion in text using HuggingFace Inference API.
        
        Args:
            text: Input text to analyze
            
        Returns:
            EmotionResult with detected emotion and confidence
        """
        try:
            # Limit text length to avoid API issues
            text_to_analyze = text[:512]
            
            # Call HuggingFace Inference API synchronously
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self._api_url,
                    headers=self._headers,
                    json={"inputs": text_to_analyze}
                )
                response.raise_for_status()
                
                results = response.json()
                
                # Parse response
                if results and isinstance(results, list) and len(results) > 0:
                    # Get top result (highest score)
                    top_result = results[0][0] if isinstance(results[0], list) else results[0]
                    emotion = top_result.get("label", "neutral").lower()
                    confidence = top_result.get("score", 1.0)
                    
                    logger.debug(f"Detected emotion: {emotion} (confidence: {confidence:.2f})")
                    return EmotionResult(emotion=emotion, confidence=confidence)
        
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error calling emotion API: {e}. Falling back to neutral.")
        except httpx.TimeoutException:
            logger.warning("Timeout calling emotion API. Falling back to neutral.")
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}. Falling back to neutral.")
        
        # Fallback to neutral on any error
        return EmotionResult(emotion="neutral", confidence=1.0)
    
    async def detect_emotion_async(self, text: str) -> EmotionResult:
        """Detect the primary emotion in text (async version).
        
        Args:
            text: Input text to analyze
            
        Returns:
            EmotionResult with detected emotion and confidence
        """
        try:
            # Limit text length to avoid API issues
            text_to_analyze = text[:512]
            
            # Call HuggingFace Inference API asynchronously
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self._api_url,
                    headers=self._headers,
                    json={"inputs": text_to_analyze}
                )
                response.raise_for_status()
                
                results = response.json()
                
                # Parse response
                if results and isinstance(results, list) and len(results) > 0:
                    # Get top result (highest score)
                    top_result = results[0][0] if isinstance(results[0], list) else results[0]
                    emotion = top_result.get("label", "neutral").lower()
                    confidence = top_result.get("score", 1.0)
                    
                    logger.debug(f"Detected emotion: {emotion} (confidence: {confidence:.2f})")
                    return EmotionResult(emotion=emotion, confidence=confidence)
        
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error calling emotion API: {e}. Falling back to neutral.")
        except httpx.TimeoutException:
            logger.warning("Timeout calling emotion API. Falling back to neutral.")
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}. Falling back to neutral.")
        
        # Fallback to neutral on any error
        return EmotionResult(emotion="neutral", confidence=1.0)
    
    def get_tone_for_emotion(self, emotion: str) -> str:
        """Get the appropriate response tone for an emotion.
        
        Args:
            emotion: Detected emotion label
            
        Returns:
            Description of tone to use in response
        """
        return self.EMOTION_TO_TONE.get(emotion, self.EMOTION_TO_TONE["neutral"])
