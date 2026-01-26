"""
Excel API Endpoints
Handles Excel file upload, analysis, and Q&A
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import uuid
import os
from pathlib import Path

from app.database import get_db
from app.models.database import User, Document
from app.utils.auth import get_current_user
from app.services.excel_service import get_excel_service
from app.services.document_service import UPLOAD_DIR
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/excel", tags=["excel"])

# Allowed Excel file extensions
EXCEL_EXTENSIONS = {".xlsx", ".xls", ".xlsm", ".csv"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class ExcelQuestionRequest(BaseModel):
    """Request model for asking questions about Excel data"""
    question: str
    sheet_name: Optional[str] = None


class GoogleSheetRequest(BaseModel):
    """Request model for loading Google Sheets"""
    url: str
    sheet_name: Optional[str] = None
    thread_id: Optional[int] = None


class ExcelQuestionResponse(BaseModel):
    """Response model for Excel Q&A"""
    question: str
    answer: str
    file_name: str
    data_shape: Dict[str, int]
    error: bool = False


class ExcelSummaryResponse(BaseModel):
    """Response model for Excel file summary"""
    rows: int
    columns: int
    column_names: List[str]
    column_types: Dict[str, str]
    sample_data: List[Dict[str, Any]]
    sheet_names: Optional[List[str]] = None


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_excel_file(
    file: UploadFile = File(...),
    thread_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an Excel or CSV file"""
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in EXCEL_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(EXCEL_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024} MB"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_ext}"
        file_path = UPLOAD_DIR / filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Validate Excel file
        excel_service = get_excel_service()
        if not excel_service.validate_excel_file(str(file_path)):
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted Excel file"
            )
        
        # Load and get summary
        df = excel_service.load_excel_file(str(file_path))
        summary = excel_service.get_dataframe_summary(df)
        sheet_names = excel_service.get_sheet_names(str(file_path))
        
        # Create document record
        document = Document(
            user_id=current_user.id,
            thread_id=thread_id,
            filename=filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_ext.lstrip('.'),
            status="ready",
            chunk_count=len(df)  # Using row count for Excel files
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Excel file uploaded: {file.filename} by user {current_user.email}")
        
        return {
            "id": document.id,
            "filename": document.filename,
            "original_filename": document.original_filename,
            "file_size": document.file_size,
            "file_type": document.file_type,
            "status": document.status,
            "rows": summary.get("rows", 0),
            "columns": summary.get("columns", 0),
            "column_names": summary.get("column_names", []),
            "sheet_names": sheet_names,
            "created_at": document.created_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading Excel file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/{document_id}/summary", response_model=ExcelSummaryResponse)
async def get_excel_summary(
    document_id: int,
    sheet_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary information about an Excel file"""
    try:
        # Get document
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Load Excel file or Google Sheet
        excel_service = get_excel_service()
        
        if document.file_type == "gsheet":
            df = excel_service.load_google_sheet(document.file_path, sheet_name)
            sheet_names = []
        else:
            df = excel_service.load_excel_file(document.file_path, sheet_name)
            sheet_names = excel_service.get_sheet_names(document.file_path)
        
        summary = excel_service.get_dataframe_summary(df)
        
        return ExcelSummaryResponse(
            rows=summary["rows"],
            columns=summary["columns"],
            column_names=summary["column_names"],
            column_types=summary["column_types"],
            sample_data=summary["sample_data"],
            sheet_names=sheet_names
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Excel summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting summary: {str(e)}"
        )


@router.post("/{document_id}/ask", response_model=ExcelQuestionResponse)
async def ask_excel_question(
    document_id: int,
    request: ExcelQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about the Excel data using natural language"""
    try:
        # Get document
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Load Excel file or Google Sheet
        excel_service = get_excel_service()
        
        if document.file_type == "gsheet":
            # Load from Google Sheets URL
            df = excel_service.load_google_sheet(document.file_path, request.sheet_name)
        else:
            # Load from local file
            df = excel_service.load_excel_file(document.file_path, request.sheet_name)
        
        # Ask question
        result = excel_service.ask_question(
            df=df,
            question=request.question,
            file_name=document.original_filename
        )
        
        return ExcelQuestionResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error asking Excel question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


@router.get("/{document_id}/sheets")
async def get_sheet_names(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of sheet names in an Excel file"""
    try:
        # Get document
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get sheet names
        excel_service = get_excel_service()
        sheet_names = excel_service.get_sheet_names(document.file_path)
        
        return {
            "document_id": document_id,
            "filename": document.original_filename,
            "sheet_names": sheet_names
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sheet names: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting sheet names: {str(e)}"
        )


@router.post("/google-sheet", status_code=status.HTTP_201_CREATED)
async def load_google_sheet(
    request: GoogleSheetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Load a Google Sheet from URL"""
    try:
        excel_service = get_excel_service()
        
        # Validate URL
        if not excel_service.is_google_sheets_url(request.url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google Sheets URL"
            )
        
        # Load the Google Sheet
        df = excel_service.load_google_sheet(request.url, request.sheet_name)
        summary = excel_service.get_dataframe_summary(df)
        
        # Extract sheet ID for filename
        sheet_id = excel_service.extract_sheet_id(request.url)
        filename = f"gsheet_{sheet_id}_{request.sheet_name or 'default'}"
        
        # Create document record (no actual file saved for Google Sheets)
        document = Document(
            user_id=current_user.id,
            thread_id=request.thread_id,
            filename=filename,
            original_filename=f"Google Sheet ({sheet_id})",
            file_path=request.url,  # Store URL instead of file path
            file_size=0,  # No local file
            file_type="gsheet",
            status="ready",
            chunk_count=len(df)
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Google Sheet loaded: {sheet_id} by user {current_user.email}")
        
        return {
            "id": document.id,
            "filename": document.filename,
            "original_filename": document.original_filename,
            "file_type": "gsheet",
            "status": document.status,
            "rows": summary.get("rows", 0),
            "columns": summary.get("columns", 0),
            "column_names": summary.get("column_names", []),
            "url": request.url,
            "created_at": document.created_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading Google Sheet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading Google Sheet: {str(e)}"
        )
