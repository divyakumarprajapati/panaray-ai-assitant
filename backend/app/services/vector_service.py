"""Vector database service using Pinecone."""
import logging
from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
import time

from ..config import get_settings

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing vector storage in Pinecone.
    
    Follows Single Responsibility Principle - only handles vector operations.
    """
    
    def __init__(self):
        """Initialize Pinecone client and index."""
        self._settings = get_settings()
        logger.info("Initializing Pinecone client")
        
        self._pc = Pinecone(api_key=self._settings.pinecone_api_key)
        self._index_name = self._settings.pinecone_index_name
        self._ensure_index_exists()
        self._index = self._pc.Index(self._index_name)
        
        logger.info(f"Vector service initialized with index: {self._index_name}")
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists, create if not."""
        existing_indexes = [index.name for index in self._pc.list_indexes()]
        
        if self._index_name not in existing_indexes:
            logger.info(f"Creating new index: {self._index_name}")
            self._pc.create_index(
                name=self._index_name,
                dimension=self._settings.pinecone_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=self._settings.pinecone_environment
                )
            )
            
            # Wait for index to be ready
            while not self._pc.describe_index(self._index_name).status['ready']:
                time.sleep(1)
            
            logger.info("Index created successfully")
    
    def upsert_vectors(
        self,
        vectors: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> int:
        """Insert or update vectors in the index.
        
        Args:
            vectors: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: Optional list of IDs (auto-generated if not provided)
            
        Returns:
            Number of vectors upserted
        """
        if not ids:
            ids = [f"doc_{i}" for i in range(len(vectors))]
        
        # Prepare records for upsert
        records = []
        for id_, vector, metadata in zip(ids, vectors, metadatas):
            records.append({
                "id": id_,
                "values": vector,
                "metadata": metadata
            })
        
        # Upsert in batches of 100
        batch_size = 100
        total_upserted = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            self._index.upsert(vectors=batch)
            total_upserted += len(batch)
            logger.debug(f"Upserted batch {i//batch_size + 1}, total: {total_upserted}")
        
        logger.info(f"Successfully upserted {total_upserted} vectors")
        return total_upserted
    
    def query_similar(
        self,
        query_vector: List[float],
        top_k: int = 3,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """Query for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of similar documents with metadata and scores
        """
        results = self._index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        similar_docs = []
        for match in results.matches:
            similar_docs.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
        
        logger.debug(f"Found {len(similar_docs)} similar documents")
        return similar_docs
    
    def delete_all(self):
        """Delete all vectors from the index."""
        logger.warning("Deleting all vectors from index")
        self._index.delete(delete_all=True)
    
    def get_stats(self) -> Dict:
        """Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        stats = self._index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension
        }
