"""
RAG (Retrieval-Augmented Generation) Service
Handles document-based question answering using OpenAI embeddings
"""

from typing import List, Dict, Optional
import logging

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize OpenAI embeddings with text-embedding-3-large
embeddings = OpenAIEmbeddings(
    model=settings.OPENAI_EMBEDDING_MODEL,
    openai_api_key=settings.OPENAI_API_KEY
)

# Chroma DB path
CHROMA_PATH = Path("chroma_db")


class RAGService:
    """Service for retrieval-augmented generation"""
    
    def __init__(self):
        self.embeddings = embeddings
    
    def get_vectorstore_for_user(self, user_id: int):
        """Get vector store for a specific user"""
        try:
            collection_name = f"user_{user_id}_docs"
            return Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(CHROMA_PATH)
            )
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return None
    
    def retrieve_relevant_chunks(
        self, 
        user_id: int, 
        query: str, 
        k: int = 4
    ) -> List[Dict[str, any]]:
        """
        Retrieve relevant document chunks for a query
        
        Args:
            user_id: User ID
            query: User's question
            k: Number of chunks to retrieve
        
        Returns:
            List of relevant chunks with metadata
        """
        try:
            vectorstore = self.get_vectorstore_for_user(user_id)
            
            if not vectorstore:
                return []
            
            # Perform similarity search
            results = vectorstore.similarity_search_with_score(query, k=k)
            
            # Format results
            chunks = []
            for doc, score in results:
                chunks.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                })
            
            logger.info(f"Retrieved {len(chunks)} chunks for user {user_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            return []
    
    def format_context_for_prompt(self, chunks: List[Dict[str, any]]) -> str:
        """Format retrieved chunks into context for LLM prompt"""
        if not chunks:
            return ""
        
        context = "Based on the following relevant information from your uploaded documents:\n\n"
        
        for i, chunk in enumerate(chunks, 1):
            filename = chunk["metadata"].get("filename", "Unknown")
            content = chunk["content"]
            context += f"[Document: {filename}]\n{content}\n\n"
        
        return context
    
    def should_use_rag(self, user_id: int) -> bool:
        """Check if user has documents uploaded and should use RAG"""
        try:
            vectorstore = self.get_vectorstore_for_user(user_id)
            if not vectorstore:
                return False
            
            # Check if collection has any documents
            collection = vectorstore._collection
            count = collection.count()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking RAG availability: {str(e)}")
            return False


def get_rag_service() -> RAGService:
    """Get RAG service instance"""
    return RAGService()
