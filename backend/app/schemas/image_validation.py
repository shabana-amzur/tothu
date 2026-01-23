"""
Pydantic schemas for image validation and rule engine.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class RuleType(str, Enum):
    """Supported rule types for validation."""
    REQUIRED_FIELD = "REQUIRED_FIELD"
    REGEX_MATCH = "REGEX_MATCH"
    RANGE_CHECK = "RANGE_CHECK"
    DATE_CHECK = "DATE_CHECK"
    ENUM_CHECK = "ENUM_CHECK"


class DateCondition(str, Enum):
    """Date validation conditions."""
    PAST = "PAST"
    FUTURE = "FUTURE"
    ANY = "ANY"


class Rule(BaseModel):
    """Single validation rule definition."""
    field: str = Field(..., description="Field name to validate")
    type: RuleType = Field(..., description="Type of validation rule")
    condition: Optional[DateCondition] = Field(None, description="Condition for DATE_CHECK")
    min: Optional[float] = Field(None, description="Minimum value for RANGE_CHECK")
    max: Optional[float] = Field(None, description="Maximum value for RANGE_CHECK")
    pattern: Optional[str] = Field(None, description="Regex pattern for REGEX_MATCH")
    values: Optional[List[str]] = Field(None, description="Allowed values for ENUM_CHECK")
    
    class Config:
        use_enum_values = True


class RuleSet(BaseModel):
    """Complete rule set for a document type."""
    document_type: str = Field(..., description="Type of document (e.g., invoice, receipt)")
    rules: List[Rule] = Field(..., description="List of validation rules")


class ValidationResult(BaseModel):
    """Result of a single rule validation."""
    field: str = Field(..., description="Field name that was validated")
    rule_type: str = Field(..., description="Type of rule that was applied")
    status: Literal["PASS", "FAIL"] = Field(..., description="Validation status")
    reason: Optional[str] = Field(None, description="Reason for failure if status is FAIL")


class ImageValidationRequest(BaseModel):
    """Request model for image validation."""
    document_type: str = Field(..., description="Type of document to validate against")
    expected_fields: Optional[List[str]] = Field(None, description="Expected fields to extract")


class ImageValidationResponse(BaseModel):
    """Response model for image validation."""
    extracted_data: Dict[str, Any] = Field(..., description="Data extracted from image")
    validation_results: List[ValidationResult] = Field(..., description="Per-rule validation results")
    overall_status: Literal["VALID", "INVALID"] = Field(..., description="Overall validation status")
    confidence_score: Optional[float] = Field(None, description="Extraction confidence (0-1)")


class ExtractionRequest(BaseModel):
    """Request model for data extraction only."""
    expected_fields: Optional[List[str]] = Field(None, description="Expected fields to extract")
    document_type: Optional[str] = Field(None, description="Type of document for context")


class ExtractionResponse(BaseModel):
    """Response model for data extraction."""
    extracted_data: Dict[str, Any] = Field(..., description="Data extracted from image")
    confidence_score: Optional[float] = Field(None, description="Extraction confidence (0-1)")
    extraction_method: str = Field(..., description="Method used (vision_ai, ocr)")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
