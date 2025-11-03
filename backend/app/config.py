"""Application configuration management."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys (required - must be set in .env file or environment variables)
    huggingface_api_key: str
    pinecone_api_key: str
    
    # Pinecone Configuration
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "feature-assistant"
    pinecone_dimension: int = 384  # all-MiniLM-L6-v2 dimension
    
    # Model Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "meta-llama/llama-3.1-8b-instruct"
    
    # API Configuration
    api_title: str = "Feature Assistant API"
    api_version: str = "1.0.0"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # RAG Configuration
    top_k_results: int = 3
    similarity_threshold: float = 0.7
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
