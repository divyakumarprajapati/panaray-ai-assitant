"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .api import router
from .services import (
    EmbeddingService,
    EmotionService,
    LLMService,
    VectorService,
    RAGService
)
from .utils import DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Application starting up")
    
    # Initialize all services on startup
    logger.info("Initializing services...")
    try:
        embedding_service = EmbeddingService()
        emotion_service = EmotionService()
        llm_service = LLMService()
        vector_service = VectorService()
        rag_service = RAGService(
            embedding_service=embedding_service,
            emotion_service=emotion_service,
            llm_service=llm_service,
            vector_service=vector_service
        )
        
        # Store services in app state
        app.state.services = {
            "embedding": embedding_service,
            "emotion": emotion_service,
            "llm": llm_service,
            "vector": vector_service,
            "rag": rag_service
        }
        
        logger.info("Services initialized successfully")
        
        # Load data into Pinecone if not already loaded
        logger.info("Checking if data needs to be loaded...")
        try:
            stats = vector_service.get_stats()
            if stats["total_vectors"] == 0:
                logger.info("Index is empty, loading initial data...")
                
                # Load data from file
                settings = get_settings()
                data_file = "backend/data/features.jsonl"
                raw_data = DataLoader.load_jsonl(data_file)
                documents = DataLoader.prepare_documents(raw_data)
                
                if documents:
                    # Generate embeddings
                    logger.info(f"Generating embeddings for {len(documents)} documents...")
                    contents = [doc["content"] for doc in documents]
                    embeddings = embedding_service.generate_embeddings_batch(contents)
                    
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
                    logger.info("Indexing vectors in Pinecone...")
                    ids = [doc["id"] for doc in documents]
                    indexed_count = vector_service.upsert_vectors(
                        vectors=embeddings,
                        metadatas=metadatas,
                        ids=ids
                    )
                    
                    logger.info(f"Successfully indexed {indexed_count} documents")
                else:
                    logger.warning("No valid documents found in data file")
            else:
                logger.info(f"Index already contains {stats['total_vectors']} vectors, skipping data load")
        except FileNotFoundError as e:
            logger.warning(f"Data file not found during startup: {e}")
        except Exception as e:
            logger.error(f"Error loading data during startup: {e}", exc_info=True)
            # Don't fail startup if data loading fails
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        raise
    
    yield
    
    logger.info("Application shutting down")


def create_application() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router, prefix="/api")
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": settings.api_title,
            "version": settings.api_version,
            "status": "running"
        }
    
    logger.info(f"Application configured: {settings.api_title} v{settings.api_version}")
    return app


app = create_application()
