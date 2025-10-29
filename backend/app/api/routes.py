"""API route definitions."""
import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from ..models.schemas import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    IndexDataRequest,
    IndexDataResponse
)
from ..services import (
    EmbeddingService,
    EmotionService,
    LLMService,
    VectorService,
    RAGService
)
from ..utils import DataLoader
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Service instances (singleton pattern)
_services = {}


def get_services() -> dict:
    """Get or create service instances.
    
    Returns:
        Dictionary of service instances
    """
    if not _services:
        logger.info("Initializing services")
        _services["embedding"] = EmbeddingService()
        _services["emotion"] = EmotionService()
        _services["llm"] = LLMService()
        _services["vector"] = VectorService()
        _services["rag"] = RAGService(
            embedding_service=_services["embedding"],
            emotion_service=_services["emotion"],
            llm_service=_services["llm"],
            vector_service=_services["vector"]
        )
    return _services


@router.get("/health", response_model=HealthResponse)
async def health_check(services: Annotated[dict, Depends(get_services)]) -> HealthResponse:
    """Health check endpoint.
    
    Returns:
        Health status of all services
    """
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
    request: QueryRequest,
    services: Annotated[dict, Depends(get_services)]
) -> QueryResponse:
    """Query the feature assistant.
    
    Args:
        request: Query request with user question
        services: Injected services
        
    Returns:
        QueryResponse with answer and metadata
    """
    try:
        rag_service: RAGService = services["rag"]
        response = await rag_service.process_query(request.query)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/index", response_model=IndexDataResponse)
async def index_data(
    request: IndexDataRequest,
    services: Annotated[dict, Depends(get_services)]
) -> IndexDataResponse:
    """Index data from JSONL file into vector store.
    
    Args:
        request: Index request with options
        services: Injected services
        
    Returns:
        IndexDataResponse with indexing results
    """
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
        if stats["total_vectors"] > 0 and not request.force_reindex:
            logger.info("Data already indexed, skipping")
            return IndexDataResponse(
                indexed_count=stats["total_vectors"],
                status="already_indexed"
            )
        
        # Clear existing data if force reindex
        if request.force_reindex and stats["total_vectors"] > 0:
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
