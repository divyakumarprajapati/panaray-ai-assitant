"""Data loading and indexing utilities."""
import json
import logging
from pathlib import Path
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..services import VectorService, EmbeddingService

logger = logging.getLogger(__name__)


class DataLoader:
    """Utility for loading and preparing data for indexing.
    
    Follows Single Responsibility Principle - only handles data loading.
    """
    
    @staticmethod
    def load_jsonl(file_path: str) -> List[Dict]:
        """Load data from JSONL file.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of parsed JSON objects
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"Data file not found: {file_path}")
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num}: {e}")
        
        logger.info(f"Loaded {len(data)} records from {file_path}")
        return data
    
    @staticmethod
    def prepare_documents(data: List[Dict]) -> List[Dict[str, str]]:
        """Prepare documents for indexing from conversation data.
        
        Args:
            data: List of conversation objects with 'messages' field
            
        Returns:
            List of documents with 'content' field
        """
        documents = []
        
        for idx, item in enumerate(data):
            messages = item.get("messages", [])
            
            # Extract user question and assistant answer
            user_msg = ""
            assistant_msg = ""
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "user":
                    user_msg = content
                elif role == "assistant":
                    assistant_msg = content
            
            if user_msg and assistant_msg:
                # Combine question and answer for better retrieval
                combined_content = f"Q: {user_msg}\nA: {assistant_msg}"
                
                documents.append({
                    "id": f"doc_{idx}",
                    "content": combined_content,
                    "question": user_msg,
                    "answer": assistant_msg
                })
        
        logger.info(f"Prepared {len(documents)} documents for indexing")
        return documents
    
    @staticmethod
    def load_and_index_data(vector_service: "VectorService", embedding_service: "EmbeddingService", force_reindex: bool = False) -> dict:
        """Load data from file and index it in Pinecone.
        
        This function is used both during application startup and by the /index endpoint.
        
        Args:
            vector_service: VectorService instance
            embedding_service: EmbeddingService instance
            force_reindex: If True, clear existing data before indexing
            
        Returns:
            Dictionary with indexing results: {"indexed_count": int, "status": str}
        """
        logger.info("Starting data indexing process")
        
        # Check if already indexed
        stats = vector_service.get_stats()
        if stats["total_vectors"] > 0 and not force_reindex:
            logger.info(f"Index already contains {stats['total_vectors']} vectors, skipping")
            return {
                "indexed_count": stats["total_vectors"],
                "status": "already_indexed"
            }
        
        # Clear existing data if force reindex
        if force_reindex and stats["total_vectors"] > 0:
            logger.info("Force reindex requested, clearing existing data")
            vector_service.delete_all()
        
        # Load data from file
        data_file = "backend/data/features.jsonl"
        logger.info(f"Loading data from {data_file}")
        raw_data = DataLoader.load_jsonl(data_file)
        documents = DataLoader.prepare_documents(raw_data)
        
        if not documents:
            logger.warning("No valid documents found in data file")
            return {
                "indexed_count": 0,
                "status": "no_documents"
            }
        
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
        return {
            "indexed_count": indexed_count,
            "status": "success"
        }
