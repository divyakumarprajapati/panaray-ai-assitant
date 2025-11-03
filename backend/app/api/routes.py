"""API route definitions."""
import logging
from fastapi import APIRouter, HTTPException, Request

from ..models.schemas import (
    QueryRequest,
    QueryResponse,
    HealthResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


def get_services(request: Request) -> dict:
    """Get service instances from app state.
    
    Services are initialized during application startup and stored in app.state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary of service instances
    """
    return request.app.state.services


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """Health check endpoint.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Health status of all services
    """
    services = request.app.state.services
    try:
        # Check vector store
        stats = services["vector"].get_stats()
        
        return HealthResponse(
            status="healthy",
            services={
                "embedding": "operational",
                "llm": "operational",
                "vector_store": "operational",
                "indexed_documents": str(stats.get("total_vectors", 0))
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.post("/query", response_model=QueryResponse)
async def query_assistant(
    query_request: QueryRequest,
    request: Request
) -> QueryResponse:
    """Query the feature assistant.
    
    Args:
        query_request: Query request with user question
        request: FastAPI request object
        
    Returns:
        QueryResponse with answer and metadata
    """
    services = request.app.state.services
    try:
        rag_service = services["rag"]
        response = await rag_service.process_query(query_request.query)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
