"""RAG orchestration service using LangGraph state graph pattern."""
import logging
from typing import Dict, TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

from .embedding_service import EmbeddingService
from .llm_service import LLMService
from .vector_service import VectorService
from ..models.schemas import QueryResponse
from ..config import get_settings

logger = logging.getLogger(__name__)


# Define the state structure for LangGraph
class RAGState(TypedDict):
    """State structure for the RAG workflow graph.
    
    This defines all the data that flows through the LangGraph nodes.
    """
    query: str
    query_embedding: list[float]
    retrieved_docs: list[Dict]
    filtered_docs: list[Dict]
    context: list[Dict]
    answer: str
    confidence: float
    sources_used: int
    error: str | None


class RAGService:
    """Orchestrates RAG pipeline using LangGraph state graph pattern.
    
    This implementation uses LangGraph to create a stateful, cyclic workflow
    that manages the RAG pipeline with clear nodes and edges.
    
    Follows Dependency Inversion Principle - depends on abstractions (services).
    Follows Open/Closed Principle - extensible without modification.
    """
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        vector_service: VectorService
    ):
        """Initialize RAG service with dependencies and build LangGraph.
        
        Args:
            embedding_service: Service for generating embeddings
            llm_service: Service for generating responses
            vector_service: Service for vector operations
        """
        self._embedding_service = embedding_service
        self._llm_service = llm_service
        self._vector_service = vector_service
        self._settings = get_settings()
        
        # Build the LangGraph workflow
        self._graph = self._build_graph()
        
        logger.info("RAG service initialized with LangGraph state graph")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph for RAG pipeline.
        
        Returns:
            Compiled LangGraph StateGraph
        """
        # Create the graph
        workflow = StateGraph(RAGState)
        
        # Add nodes for each step in the pipeline
        workflow.add_node("generate_embedding", self._generate_embedding_node)
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("filter_results", self._filter_results_node)
        workflow.add_node("prepare_context", self._prepare_context_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("calculate_confidence", self._calculate_confidence_node)
        
        # Define the workflow edges (execution order)
        workflow.set_entry_point("generate_embedding")
        workflow.add_edge("generate_embedding", "retrieve_context")
        workflow.add_edge("retrieve_context", "filter_results")
        workflow.add_edge("filter_results", "prepare_context")
        workflow.add_edge("prepare_context", "generate_response")
        workflow.add_edge("generate_response", "calculate_confidence")
        workflow.add_edge("calculate_confidence", END)
        
        # Compile the graph
        return workflow.compile()
    
    # Node functions for the LangGraph workflow
    
    def _generate_embedding_node(self, state: RAGState) -> Dict:
        """Node: Generate embedding for the query.
        
        Args:
            state: Current RAG state
            
        Returns:
            Updated state with query embedding
        """
        logger.info("Node: Generating query embedding")
        query = state["query"]
        
        query_embedding = self._embedding_service.generate_embedding(query)
        
        return {
            "query_embedding": query_embedding
        }
    
    def _retrieve_context_node(self, state: RAGState) -> Dict:
        """Node: Retrieve similar documents from vector store.
        
        Args:
            state: Current RAG state
            
        Returns:
            Updated state with retrieved documents
        """
        logger.info("Node: Retrieving similar documents")
        query_embedding = state["query_embedding"]
        
        similar_docs = self._vector_service.query_similar(
            query_vector=query_embedding,
            top_k=self._settings.top_k_results
        )
        
        logger.info(f"Retrieved {len(similar_docs)} documents")
        
        return {
            "retrieved_docs": similar_docs
        }
    
    def _filter_results_node(self, state: RAGState) -> Dict:
        """Node: Filter documents by similarity threshold.
        
        Args:
            state: Current RAG state
            
        Returns:
            Updated state with filtered documents
        """
        logger.info("Node: Filtering results by similarity threshold")
        retrieved_docs = state["retrieved_docs"]
        
        filtered_docs = [
            doc for doc in retrieved_docs
            if doc["score"] >= self._settings.similarity_threshold
        ]
        
        logger.info(f"Filtered to {len(filtered_docs)} relevant documents")
        
        return {
            "filtered_docs": filtered_docs
        }
    
    def _prepare_context_node(self, state: RAGState) -> Dict:
        """Node: Prepare context for LLM from filtered documents.
        
        Args:
            state: Current RAG state
            
        Returns:
            Updated state with prepared context
        """
        logger.info("Node: Preparing context for LLM")
        filtered_docs = state["filtered_docs"]
        
        context = [
            {"content": doc["metadata"].get("content", "")}
            for doc in filtered_docs
        ]
        
        return {
            "context": context
        }
    
    async def _generate_response_node(self, state: RAGState) -> Dict:
        """Node: Generate response using LLM with context.
        
        Args:
            state: Current RAG state
            
        Returns:
            Updated state with generated answer
        """
        logger.info("Node: Generating response")
        query = state["query"]
        context = state["context"]
        
        answer = await self._llm_service.generate_response(
            query=query,
            context=context
        )
        
        return {
            "answer": answer
        }
    
    def _calculate_confidence_node(self, state: RAGState) -> Dict:
        """Node: Calculate confidence and finalize metadata.
        
        Args:
            state: Current RAG state
            
        Returns:
            Updated state with confidence and sources_used
        """
        logger.info("Node: Calculating confidence")
        filtered_docs = state["filtered_docs"]
        
        confidence = self._calculate_confidence(filtered_docs)
        sources_used = len(filtered_docs)
        
        return {
            "confidence": confidence,
            "sources_used": sources_used
        }
    
    async def process_query(self, query: str) -> QueryResponse:
        """Process a user query through the LangGraph RAG pipeline.
        
        Args:
            query: User's question
            
        Returns:
            QueryResponse with answer and metadata
        """
        logger.info(f"Processing query through LangGraph: {query[:50]}...")
        
        # Initialize state
        initial_state: RAGState = {
            "query": query,
            "query_embedding": [],
            "retrieved_docs": [],
            "filtered_docs": [],
            "context": [],
            "answer": "",
            "confidence": 0.0,
            "sources_used": 0,
            "error": None
        }
        
        try:
            # Execute the graph
            final_state = await self._graph.ainvoke(initial_state)
            
            logger.info("Query processed successfully through LangGraph")
            
            # Build and return response
            return QueryResponse(
                answer=final_state["answer"],
                sources_used=final_state["sources_used"],
                confidence=final_state["confidence"]
            )
        
        except Exception as e:
            logger.error(f"Error in LangGraph pipeline: {e}", exc_info=True)
            
            # Return error response
            return QueryResponse(
                answer=f"I apologize, but I encountered an error processing your request: {str(e)}",
                sources_used=0,
                confidence=0.0
            )
    
    def _calculate_confidence(self, docs: list) -> float:
        """Calculate confidence score based on retrieved documents.
        
        Args:
            docs: List of retrieved documents with scores
            
        Returns:
            Confidence score between 0 and 1
        """
        if not docs:
            return 0.0
        
        # Average similarity score of top results
        avg_score = sum(doc["score"] for doc in docs) / len(docs)
        return round(avg_score, 2)
    
    def visualize_graph(self) -> str:
        """Get a visual representation of the LangGraph workflow.
        
        Returns:
            String representation of the graph structure
        """
        return """
LangGraph RAG Pipeline:

???????????????????????
? generate_embedding  ? (Generate query embedding vector)
???????????????????????
          ?
          ?
???????????????????????
?  retrieve_context   ? (Search vector DB for similar docs)
???????????????????????
          ?
          ?
???????????????????????
?   filter_results    ? (Filter by similarity threshold)
???????????????????????
          ?
          ?
???????????????????????
?  prepare_context    ? (Format context for LLM)
???????????????????????
          ?
          ?
???????????????????????
? generate_response   ? (LLM generates answer)
???????????????????????
          ?
          ?
???????????????????????
?calculate_confidence ? (Calculate final confidence score)
???????????????????????
          ?
          ?
        [END]
"""
