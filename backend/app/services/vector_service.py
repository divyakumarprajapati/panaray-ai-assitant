"""Vector database service using LangChain Pinecone integration."""
import logging
from typing import List, Dict, Optional
from langchain_community.vectorstores import Pinecone as LangChainPinecone
from pinecone import Pinecone, ServerlessSpec
from pinecone.core.client.exceptions import ServiceException, PineconeException
import time

from ..config import get_settings

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing vector storage using LangChain Pinecone integration.
    
    Follows Single Responsibility Principle - only handles vector operations.
    Now using LangChain's Pinecone wrapper for better integration with LangChain ecosystem.
    """
    
    def __init__(self, embedding_service=None):
        """Initialize Pinecone client and index with LangChain integration.
        
        Args:
            embedding_service: Optional EmbeddingService instance for LangChain integration
        """
        self._settings = get_settings()
        logger.info("Initializing Pinecone client with LangChain")
        
        # Initialize native Pinecone client for management operations
        self._pc = Pinecone(api_key=self._settings.pinecone_api_key)
        self._index_name = self._settings.pinecone_index_name
        self._ensure_index_exists()
        self._index = self._pc.Index(self._index_name)
        
        # Store embedding service for LangChain integration
        self._embedding_service = embedding_service
        self._vectorstore = None
        
        logger.info(f"Vector service initialized with index: {self._index_name}")
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists, create if not.
        
        Handles Pinecone API errors gracefully, including 500 Internal Server Errors
        which can occur due to transient issues or race conditions.
        """
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                existing_indexes = [index.name for index in self._pc.list_indexes()]
                
                if self._index_name not in existing_indexes:
                    logger.info(f"Creating new index: {self._index_name} (attempt {attempt + 1}/{max_retries})")
                    
                    try:
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
                        logger.info("Waiting for index to be ready...")
                        while not self._pc.describe_index(self._index_name).status['ready']:
                            time.sleep(1)
                        
                        logger.info("Index created successfully")
                        return
                        
                    except ServiceException as e:
                        # Handle 500 Internal Server Error from Pinecone
                        if e.status == 500:
                            logger.warning(f"Pinecone returned 500 error: {e.reason}")
                            
                            # Check if index was actually created despite the error
                            time.sleep(retry_delay)
                            existing_indexes = [index.name for index in self._pc.list_indexes()]
                            
                            if self._index_name in existing_indexes:
                                logger.info("Index exists despite 500 error - continuing")
                                # Wait for index to be ready
                                desc = self._pc.describe_index(self._index_name)
                                while not desc.status['ready']:
                                    time.sleep(1)
                                    desc = self._pc.describe_index(self._index_name)
                                return
                            
                            # If not the last attempt, retry
                            if attempt < max_retries - 1:
                                logger.info(f"Retrying index creation in {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                continue
                            else:
                                # Last attempt failed
                                raise RuntimeError(
                                    f"Failed to create Pinecone index after {max_retries} attempts. "
                                    f"Pinecone returned 500 Internal Server Error. "
                                    f"This might be a temporary issue with Pinecone service. "
                                    f"Please try again later or check your Pinecone dashboard."
                                ) from e
                        else:
                            # Re-raise other ServiceException errors
                            raise
                            
                else:
                    logger.info(f"Index {self._index_name} already exists")
                    return
                    
            except (ServiceException, PineconeException) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error checking/creating index (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Failed to ensure index exists after {max_retries} attempts: {e}")
                    raise
    
    def get_vectorstore(self, embeddings):
        """Get or create LangChain Pinecone vectorstore.
        
        Args:
            embeddings: LangChain embeddings object
            
        Returns:
            LangChain Pinecone vectorstore instance
        """
        if self._vectorstore is None:
            self._vectorstore = LangChainPinecone(
                index=self._index,
                embedding=embeddings,
                text_key="content"
            )
        return self._vectorstore
    
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
    
    def add_texts_with_langchain(
        self,
        texts: List[str],
        metadatas: List[Dict],
        embeddings
    ) -> List[str]:
        """Add texts using LangChain's vectorstore interface.
        
        Args:
            texts: List of text documents
            metadatas: List of metadata dictionaries
            embeddings: LangChain embeddings object
            
        Returns:
            List of document IDs
        """
        vectorstore = self.get_vectorstore(embeddings)
        ids = vectorstore.add_texts(texts=texts, metadatas=metadatas)
        logger.info(f"Added {len(ids)} texts via LangChain vectorstore")
        return ids
    
    def query_similar(
        self,
        query_vector: List[float],
        top_k: int = 3,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """Query for similar vectors using native Pinecone.
        
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
    
    def similarity_search_with_langchain(
        self,
        query: str,
        embeddings,
        k: int = 3
    ) -> List[Dict]:
        """Similarity search using LangChain's vectorstore interface.
        
        Args:
            query: Query text
            embeddings: LangChain embeddings object
            k: Number of results to return
            
        Returns:
            List of documents with scores
        """
        vectorstore = self.get_vectorstore(embeddings)
        results = vectorstore.similarity_search_with_score(query, k=k)
        
        # Format results
        docs = []
        for doc, score in results:
            docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })
        
        logger.debug(f"Found {len(docs)} similar documents via LangChain")
        return docs
    
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
