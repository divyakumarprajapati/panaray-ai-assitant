"""Data loading and indexing utilities."""
import json
import logging
from pathlib import Path
from typing import List, Dict

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
