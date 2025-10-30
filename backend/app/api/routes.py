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
from ..config import get_settings

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
    """Index data from JSONL file into vector store.
    
    Args:
        index_request: Index request with options
        request: FastAPI request object
        
    Returns:
        IndexDataResponse with indexing results
    """
    services = request.app.state.services
    try:
        settings = get_settings()
        data_file = "backend/data/features.jsonl"
        
        # Load data
        logger.info("Loading data from file")
        raw_data = DataLoader.load_jsonl(data_file)
        documents = DataLoader.prepare_documents(raw_data)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No valid documents found in data file")
        
        # Check if already indexed
        stats = services["vector"].get_stats()
        if stats["total_vectors"] > 0 and not index_request.force_reindex:
            logger.info("Data already indexed, skipping")
            return IndexDataResponse(
                indexed_count=stats["total_vectors"],
                status="already_indexed"
            )
        
        # Clear existing data if force reindex
        if index_request.force_reindex and stats["total_vectors"] > 0:
            logger.info("Force reindex requested, clearing existing data")
            services["vector"].delete_all()
        
        # Generate embeddings
        logger.info("Generating embeddings for documents")
        contents = [doc["content"] for doc in documents]
        embeddings = services["embedding"].generate_embeddings_batch(contents)
        
        # Prepare metadata
        metadatas = [
            {
                "content": doc["content"],
                "question": doc["question"],
                "answer": doc["answer"]
            }
            for doc in documents
        ]
        
        # Index vectors
        logger.info("Indexing vectors in Pinecone")
        ids = [doc["id"] for doc in documents]
        indexed_count = services["vector"].upsert_vectors(
            vectors=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return IndexDataResponse(
            indexed_count=indexed_count,
            status="success"
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
