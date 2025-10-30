"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field


class EmotionResult(BaseModel):
    """Detected emotion with confidence score."""
    emotion: str = Field(..., description="Detected emotion label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class QueryRequest(BaseModel):
    """Request model for querying the assistant."""
    query: str = Field(..., min_length=1, max_length=1000, description="User query")


class QueryResponse(BaseModel):
    """Response model with answer and metadata."""
    answer: str = Field(..., description="Generated answer")
    emotion: EmotionResult = Field(..., description="Detected user emotion")
    sources_used: int = Field(..., ge=0, description="Number of sources retrieved")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Answer confidence")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy")
    services: dict[str, str] = Field(default_factory=dict)
