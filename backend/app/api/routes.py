"""API route definitions."""
import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Annotated

from ..models.schemas import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    IndexDataRequest,
    IndexDataResponse
)
from ..utils import DataLoader

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
                "emotion": "operational",
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


@router.post("/index", response_model=IndexDataResponse)
async def index_data(
    index_request: IndexDataRequest,
    request: Request
) -> IndexDataResponse:
    """Manually trigger data indexing (mainly for reindexing).
    
    Data is automatically loaded on application startup. This endpoint is provided
    for manual reindexing operations (e.g., after data file updates).
    
    Args:
        index_request: Index request with force_reindex option
        request: FastAPI request object
        
    Returns:
        IndexDataResponse with indexing results
    """
    services = request.app.state.services
    
    try:
        logger.info(f"Manual index triggered (force_reindex={index_request.force_reindex})")
        
        # Use the shared data loading function
        result = DataLoader.load_and_index_data(
            vector_service=services["vector"],
            embedding_service=services["embedding"],
            force_reindex=index_request.force_reindex
        )
        
        return IndexDataResponse(
            indexed_count=result["indexed_count"],
            status=result["status"]
        )
        
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error indexing data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error indexing data: {str(e)}"
        )
