"""
API endpoints for image validation and data extraction.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
import json

from app.schemas.image_validation import (
    ImageValidationResponse,
    ExtractionResponse,
    ErrorResponse,
)
from app.services.image_extraction_service import get_extraction_service
from app.services.rule_validation_service import get_validation_service

router = APIRouter(prefix="/api/image-validation", tags=["Image Validation"])


@router.post(
    "/validate",
    response_model=ImageValidationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def validate_image(
    file: UploadFile = File(..., description="Image file to validate"),
    document_type: str = Form(..., description="Type of document (invoice, receipt, id_card)"),
    expected_fields: Optional[str] = Form(None, description="JSON array of expected fields")
):
    """
    Upload an image, extract data, and validate against rules.
    
    - **file**: Image file (JPG, PNG, JPEG)
    - **document_type**: Type of document for validation rules
    - **expected_fields**: Optional JSON array of fields to extract
    
    Returns extracted data with validation results.
    """
    try:
        # Parse expected fields if provided
        fields_list = None
        if expected_fields:
            try:
                fields_list = json.loads(expected_fields)
                if not isinstance(fields_list, list):
                    raise ValueError("expected_fields must be a JSON array")
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="expected_fields must be valid JSON array"
                )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Get services
        extraction_service = get_extraction_service()
        validation_service = get_validation_service()
        
        # Extract data from image
        try:
            extracted_data, method = await extraction_service.extract_with_fallback(
                image_bytes,
                document_type,
                fields_list
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # Validate extracted data
        try:
            validation_results, overall_status = validation_service.validate_data(
                extracted_data,
                document_type
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # Build response
        response = ImageValidationResponse(
            extracted_data=extracted_data,
            validation_results=validation_results,
            overall_status=overall_status,
            confidence_score=0.9 if method == "vision_ai" else 0.7
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def extract_data(
    file: UploadFile = File(..., description="Image file to extract data from"),
    document_type: Optional[str] = Form(None, description="Type of document for context"),
    expected_fields: Optional[str] = Form(None, description="JSON array of expected fields")
):
    """
    Extract structured data from an image without validation.
    
    - **file**: Image file (JPG, PNG, JPEG)
    - **document_type**: Optional document type for context
    - **expected_fields**: Optional JSON array of fields to extract
    
    Returns only extracted data without rule validation.
    """
    try:
        # Parse expected fields if provided
        fields_list = None
        if expected_fields:
            try:
                fields_list = json.loads(expected_fields)
                if not isinstance(fields_list, list):
                    raise ValueError("expected_fields must be a JSON array")
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="expected_fields must be valid JSON array"
                )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Get extraction service
        extraction_service = get_extraction_service()
        
        # Extract data from image
        try:
            extracted_data, method = await extraction_service.extract_with_fallback(
                image_bytes,
                document_type,
                fields_list
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # Build response
        response = ExtractionResponse(
            extracted_data=extracted_data,
            confidence_score=0.9 if method == "vision_ai" else 0.7,
            extraction_method=method
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/document-types")
async def get_document_types():
    """
    Get list of available document types with validation rules.
    
    Returns list of document types that can be validated.
    """
    try:
        validation_service = get_validation_service()
        document_types = validation_service.get_available_document_types()
        
        return {
            "document_types": document_types,
            "count": len(document_types)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document types: {str(e)}"
        )


@router.get("/rules/{document_type}")
async def get_rules(document_type: str):
    """
    Get validation rules for a specific document type.
    
    - **document_type**: Type of document (invoice, receipt, id_card)
    
    Returns the rule set for the specified document type.
    """
    try:
        validation_service = get_validation_service()
        rule_set = validation_service.load_rules(document_type)
        
        if not rule_set:
            raise HTTPException(
                status_code=404,
                detail=f"No rules found for document type: {document_type}"
            )
        
        return rule_set.dict()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve rules: {str(e)}"
        )


@router.post("/validate-demo")
async def validate_demo(
    document_type: str = Form(..., description="Type of document (invoice, receipt, id_card)")
):
    """
    Demo validation endpoint - returns sample data without API calls.
    Useful for testing when OpenAI API is unavailable or quota exceeded.
    
    - **document_type**: Type of document to generate sample data for
    
    Returns sample validation results.
    """
    try:
        validation_service = get_validation_service()
        
        # Generate sample extracted data based on document type
        sample_data = {}
        if document_type == "invoice":
            sample_data = {
                "invoice_number": "INV-2024-001",
                "invoice_date": "2024-01-15",
                "total_amount": 1500.00,
                "currency": "USD",
                "vendor_name": "ABC Corporation",
                "email": "billing@abccorp.com"
            }
        elif document_type == "receipt":
            sample_data = {
                "receipt_number": "RCP-123456",
                "date": "2024-01-20",
                "total": 45.50,
                "merchant_name": "Coffee Shop",
                "payment_method": "CARD"
            }
        elif document_type == "id_card":
            sample_data = {
                "id_number": "AB12345678",
                "full_name": "John Doe",
                "date_of_birth": "1990-05-15",
                "expiry_date": "2030-05-15"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown document type: {document_type}. Use: invoice, receipt, or id_card"
            )
        
        # Validate the sample data
        validation_results, overall_status = validation_service.validate_data(
            sample_data,
            document_type
        )
        
        # Build response
        response = ImageValidationResponse(
            extracted_data=sample_data,
            validation_results=validation_results,
            overall_status=overall_status,
            confidence_score=0.95  # Demo confidence
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Demo validation failed: {str(e)}"
        )


@router.post("/validate-batch")
async def validate_batch(
    files: List[UploadFile] = File(..., description="Multiple image files to validate"),
    document_type: str = Form(..., description="Type of document for all images")
):
    """
    Validate multiple images in a batch.
    
    - **files**: List of image files
    - **document_type**: Document type to validate against
    
    Returns validation results for each image.
    """
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 files allowed per batch"
            )
        
        extraction_service = get_extraction_service()
        validation_service = get_validation_service()
        
        results = []
        
        for idx, file in enumerate(files):
            try:
                # Read image bytes
                image_bytes = await file.read()
                
                # Extract data
                extracted_data, method = await extraction_service.extract_with_fallback(
                    image_bytes,
                    document_type,
                    None
                )
                
                # Validate data
                validation_results, overall_status = validation_service.validate_data(
                    extracted_data,
                    document_type
                )
                
                results.append({
                    "file_name": file.filename,
                    "index": idx,
                    "status": "success",
                    "extracted_data": extracted_data,
                    "validation_results": [v.dict() for v in validation_results],
                    "overall_status": overall_status
                })
            
            except Exception as e:
                results.append({
                    "file_name": file.filename,
                    "index": idx,
                    "status": "error",
                    "error": str(e)
                })
        
        # Calculate summary
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        valid = sum(1 for r in results if r.get("overall_status") == "VALID")
        
        return {
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "valid_documents": valid,
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch validation failed: {str(e)}"
        )
