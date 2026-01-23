"""
Image data extraction service using OpenAI Vision API.
"""
import base64
import io
import json
from typing import Dict, Any, Optional, List
from PIL import Image
import openai
from openai import OpenAI
import os
from app.config import get_settings

settings = get_settings()


class ImageExtractionService:
    """Service for extracting structured data from images using OpenAI Vision."""
    
    def __init__(self):
        """Initialize the extraction service with OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # GPT-4 with vision capabilities
    
    def encode_image(self, image_bytes: bytes) -> str:
        """
        Encode image bytes to base64 string.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def validate_image(self, image_bytes: bytes) -> tuple[bool, Optional[str]]:
        """
        Validate image format and size.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size (max 10MB)
            if len(image_bytes) > 10 * 1024 * 1024:
                return False, "Image size exceeds 10MB limit"
            
            # Validate image format
            image = Image.open(io.BytesIO(image_bytes))
            if image.format not in ['JPEG', 'PNG', 'JPG']:
                return False, f"Unsupported image format: {image.format}"
            
            return True, None
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    def build_extraction_prompt(
        self,
        document_type: Optional[str] = None,
        expected_fields: Optional[List[str]] = None
    ) -> str:
        """
        Build a structured prompt for data extraction.
        
        Args:
            document_type: Type of document (invoice, receipt, etc.)
            expected_fields: List of fields to extract
            
        Returns:
            Formatted prompt string
        """
        prompt = "Extract structured data from this image and return it as valid JSON.\n\n"
        
        if document_type:
            prompt += f"Document Type: {document_type}\n\n"
        
        if expected_fields:
            prompt += "Extract the following fields:\n"
            for field in expected_fields:
                prompt += f"- {field}\n"
            prompt += "\n"
        else:
            prompt += "Extract all relevant fields including but not limited to:\n"
            prompt += "- Document numbers (invoice, receipt, ID, etc.)\n"
            prompt += "- Dates (issue date, due date, expiry, etc.)\n"
            prompt += "- Monetary amounts (total, subtotal, tax, etc.)\n"
            prompt += "- Names (vendor, merchant, customer, etc.)\n"
            prompt += "- Contact information (email, phone, address)\n"
            prompt += "- Any other relevant information\n\n"
        
        prompt += """
IMPORTANT INSTRUCTIONS:
1. Return ONLY valid JSON, no additional text or markdown
2. Use snake_case for field names (e.g., invoice_number, total_amount)
3. For dates, use ISO format: YYYY-MM-DD
4. For monetary values, return as numbers (not strings)
5. If a field is not found, omit it from the JSON (do not use null)
6. Extract exactly what you see, do not infer or guess
7. For currency, use standard codes (INR, USD, EUR, etc.)

Example response format:
{
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-01-15",
    "total_amount": 1500.00,
    "currency": "USD",
    "vendor_name": "ABC Corp"
}
"""
        return prompt
    
    async def extract_from_image(
        self,
        image_bytes: bytes,
        document_type: Optional[str] = None,
        expected_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from an image using OpenAI Vision.
        
        Args:
            image_bytes: Raw image bytes
            document_type: Type of document being processed
            expected_fields: List of fields to extract
            
        Returns:
            Dictionary containing extracted data
            
        Raises:
            ValueError: If image is invalid or extraction fails
        """
        # Validate image
        is_valid, error_msg = self.validate_image(image_bytes)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Encode image
        base64_image = self.encode_image(image_bytes)
        
        # Build prompt
        prompt = self.build_extraction_prompt(document_type, expected_fields)
        
        try:
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1,  # Lower temperature for more consistent extraction
            )
            
            # Extract and parse response
            content = response.choices[0].message.content
            
            # Try to parse JSON from response
            try:
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()
                
                extracted_data = json.loads(content)
                return extracted_data
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse extracted data as JSON: {str(e)}\nContent: {content}")
        
        except openai.APIError as e:
            raise ValueError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Extraction failed: {str(e)}")
    
    async def extract_with_fallback(
        self,
        image_bytes: bytes,
        document_type: Optional[str] = None,
        expected_fields: Optional[List[str]] = None
    ) -> tuple[Dict[str, Any], str]:
        """
        Extract data with OCR fallback if Vision API fails.
        
        Args:
            image_bytes: Raw image bytes
            document_type: Type of document being processed
            expected_fields: List of fields to extract
            
        Returns:
            Tuple of (extracted_data, extraction_method)
        """
        try:
            # Try Vision API first
            data = await self.extract_from_image(image_bytes, document_type, expected_fields)
            return data, "vision_ai"
        except Exception as e:
            # If Vision fails, try OCR fallback
            try:
                data = await self._ocr_fallback(image_bytes, document_type, expected_fields)
                return data, "ocr"
            except Exception as ocr_error:
                raise ValueError(f"Both Vision and OCR extraction failed. Vision error: {str(e)}, OCR error: {str(ocr_error)}")
    
    async def _ocr_fallback(
        self,
        image_bytes: bytes,
        document_type: Optional[str] = None,
        expected_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fallback OCR extraction using pytesseract.
        
        Args:
            image_bytes: Raw image bytes
            document_type: Type of document being processed
            expected_fields: List of fields to extract
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            import pytesseract
            
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            # Simple extraction logic (can be enhanced)
            extracted_data = {"raw_text": text}
            
            # Try to find common patterns
            import re
            
            # Look for dates
            date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'
            dates = re.findall(date_pattern, text)
            if dates:
                extracted_data["extracted_dates"] = dates
            
            # Look for amounts
            amount_pattern = r'\$?\s*\d+[,.]?\d*\.?\d{2}'
            amounts = re.findall(amount_pattern, text)
            if amounts:
                extracted_data["extracted_amounts"] = amounts
            
            # Look for email
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, text)
            if emails:
                extracted_data["email"] = emails[0]
            
            return extracted_data
            
        except ImportError:
            raise ValueError("OCR fallback requires pytesseract library")
        except Exception as e:
            raise ValueError(f"OCR extraction failed: {str(e)}")


# Singleton instance
_extraction_service = None


def get_extraction_service() -> ImageExtractionService:
    """Get or create singleton extraction service instance."""
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ImageExtractionService()
    return _extraction_service
