"""
Document Processing Service
Handles file upload, text extraction, chunking, and vector storage
"""

import os
import uuid
from typing import List, Dict
from pathlib import Path
import logging

from pypdf import PdfReader
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.database import Document

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize HuggingFace embeddings (FREE, no API key needed, runs locally)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Chroma DB path
CHROMA_PATH = Path("chroma_db")
CHROMA_PATH.mkdir(exist_ok=True)

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class DocumentService:
    """Service for processing documents"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading TXT file: {str(e)}")
            raise
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text based on file type"""
        if file_type == "pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_type == "docx":
            return self.extract_text_from_docx(file_path)
        elif file_type == "txt":
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    def save_to_vectorstore(
        self, 
        chunks: List[str], 
        document_id: int, 
        user_id: int,
        thread_id: int,
        filename: str
    ):
        """Save document chunks to Chroma vector store with thread isolation"""
        try:
            # Create metadata for each chunk
            metadatas = [
                {
                    "document_id": document_id,
                    "user_id": user_id,
                    "thread_id": thread_id,
                    "filename": filename,
                    "chunk_index": i
                }
                for i in range(len(chunks))
            ]
            
            # Create collection name based on user_id and thread_id for isolation
            collection_name = f"user_{user_id}_thread_{thread_id}"
            
            # Initialize or load vector store
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=str(CHROMA_PATH)
            )
            
            # Add documents
            vectorstore.add_texts(
                texts=chunks,
                metadatas=metadatas
            )
            
            logger.info(f"Saved {len(chunks)} chunks for document {document_id} in thread {thread_id}")
            
        except Exception as e:
            logger.error(f"Error saving to vector store: {str(e)}")
            raise
    
    async def process_document(
        self, 
        file_path: str, 
        file_type: str, 
        document_id: int,
        user_id: int,
        thread_id: int,
        filename: str,
        db: Session
    ):
        """Process uploaded document: extract text, chunk, and store in vectordb"""
        try:
            # Extract text
            logger.info(f"Extracting text from {filename}")
            text = self.extract_text(file_path, file_type)
            
            if not text or len(text.strip()) < 10:
                raise ValueError("Document appears to be empty or has insufficient content")
            
            # Chunk text
            logger.info(f"Chunking text from {filename}")
            chunks = self.chunk_text(text)
            
            if not chunks:
                raise ValueError("No chunks created from document")
            
            # Save to vector store with thread isolation
            logger.info(f"Saving {len(chunks)} chunks to vector store for thread {thread_id}")
            self.save_to_vectorstore(chunks, document_id, user_id, thread_id, filename)
            
            # Update document status in database
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "ready"
                doc.chunk_count = len(chunks)
                db.commit()
            
            logger.info(f"Document {filename} processed successfully with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            # Update document status to failed
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "failed"
                db.commit()
            raise
    
    def get_vectorstore_for_thread(self, user_id: int, thread_id: int):
        """Get vector store for a specific thread"""
        collection_name = f"user_{user_id}_thread_{thread_id}"
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_PATH)
        )
    
    def delete_document_from_vectorstore(self, document_id: int, user_id: int, thread_id: int):
        """Delete document chunks from vector store"""
        try:
            vectorstore = self.get_vectorstore_for_thread(user_id, thread_id)
            # Filter and delete by document_id
            vectorstore._collection.delete(
                where={"document_id": document_id}
            )
            logger.info(f"Deleted document {document_id} from vector store")
        except Exception as e:
            logger.error(f"Error deleting from vector store: {str(e)}")
            raise


def get_document_service() -> DocumentService:
    """Get document service instance"""
    return DocumentService()
