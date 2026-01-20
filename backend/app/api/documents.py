"""
Documents API Endpoints
Handles document upload, listing, and deletion
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
import uuid
import os
from pathlib import Path

from app.database import get_db
from app.models.database import User, Document
from app.models.document import DocumentUploadResponse, DocumentListItem, DocumentDelete
from app.utils.auth import get_current_user
from app.services.document_service import get_document_service, UPLOAD_DIR

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".xlsx", ".xls", ".xlsm", ".csv"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    thread_id: int = None,  # Thread ID for document isolation
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document (PDF, TXT, or DOCX) to a specific thread"""
    try:
        # Validate thread exists and belongs to user if thread_id provided
        if thread_id:
            from app.models.database import ChatThread
            thread = db.query(ChatThread).filter(
                ChatThread.id == thread_id,
                ChatThread.user_id == current_user.id
            ).first()
            
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found or access denied"
                )
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)} MB"
            )
        
        # Validate file is not empty
        if file_size < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty or too small"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create database record
        file_type = file_ext[1:]  # Remove the dot
        doc = Document(
            user_id=current_user.id,
            thread_id=thread_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_type,
            status="processing"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        logger.info(f"Document uploaded: {file.filename} by user {current_user.email} to thread {thread_id}")
        
        # Process document in background
        doc_service = get_document_service()
        background_tasks.add_task(
            doc_service.process_document,
            str(file_path),
            file_type,
            doc.id,
            current_user.id,
            thread_id or 0,  # Default to 0 if no thread
            file.filename,
            db
        )
        
        return DocumentUploadResponse.model_validate(doc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/", response_model=List[DocumentListItem])
async def list_documents(
    thread_id: int = None,  # Optional filter by thread
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of user's uploaded documents, optionally filtered by thread"""
    try:
        query = db.query(Document).filter(Document.user_id == current_user.id)
        
        if thread_id is not None:
            query = query.filter(Document.thread_id == thread_id)
        
        documents = query.order_by(Document.created_at.desc()).all()
        
        return [DocumentListItem.model_validate(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.delete("/{document_id}", response_model=DocumentDelete)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    try:
        # Find document
        doc = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file from filesystem
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        
        # Delete from vector store
        doc_service = get_document_service()
        try:
            doc_service.delete_document_from_vectorstore(
                document_id, 
                current_user.id, 
                doc.thread_id or 0
            )
        except Exception as e:
            logger.warning(f"Could not delete from vector store: {str(e)}")
        
        # Delete from database
        db.delete(doc)
        db.commit()
        
        logger.info(f"Document {document_id} deleted by user {current_user.email}")
        
        return DocumentDelete(
            message="Document deleted successfully",
            document_id=document_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.get("/health")
async def documents_health():
    """Health check for documents service"""
    return {"status": "ok", "service": "documents"}
