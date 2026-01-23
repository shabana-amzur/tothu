# Project 10: Image Rule Validation & Data Extraction App

## Overview
A production-ready FastAPI backend service that extracts structured data from images using OpenAI Vision API (GPT-4o) and validates the extracted data against predefined rules.

## Features

### 1. Image Upload & Processing
- ✅ Accept multiple image formats (JPG, PNG, JPEG)
- ✅ File validation (type, size up to 10MB)
- ✅ Temporary storage for processing
- ✅ Batch processing support (up to 10 images)

### 2. Rule Definition Engine
- ✅ JSON-based rule configuration
- ✅ Pre-configured rules for: invoice, receipt, id_card
- ✅ Support for 5 rule types:
  - **REQUIRED_FIELD**: Field must exist and not be empty
  - **REGEX_MATCH**: Pattern validation
  - **RANGE_CHECK**: Numeric min/max validation
  - **DATE_CHECK**: Past/future date validation
  - **ENUM_CHECK**: Allowed values validation

### 3. Image Data Extraction
- ✅ OpenAI Vision API (GPT-4o) for primary extraction
- ✅ Structured JSON output
- ✅ OCR fallback using pytesseract (optional)
- ✅ Confidence scoring
- ✅ Support for expected fields specification

### 4. Rule Validation Logic
- ✅ Per-rule validation with detailed results
- ✅ Overall status determination (VALID/INVALID)
- ✅ Failure reason reporting
- ✅ Comprehensive error handling

## Architecture

```
backend/
├── app/
│   ├── api/
│   │   └── image_validation.py      # API endpoints
│   ├── services/
│   │   ├── image_extraction_service.py    # OpenAI Vision extraction
│   │   └── rule_validation_service.py     # Rule validation engine
│   ├── schemas/
│   │   └── image_validation.py      # Pydantic models
│   └── rules/
│       ├── invoice_rules.json       # Invoice validation rules
│       ├── receipt_rules.json       # Receipt validation rules
│       └── id_card_rules.json       # ID card validation rules
```

## API Endpoints

### 1. Validate Image with Rules
**POST** `/api/image-validation/validate`

Upload an image, extract data, and validate against rules.

**Parameters:**
- `file`: Image file (multipart/form-data)
- `document_type`: Type of document (invoice, receipt, id_card)
- `expected_fields`: Optional JSON array of fields to extract

**Response:**
```json
{
  "extracted_data": {
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-01-15",
    "total_amount": 1500.00,
    "currency": "USD",
    "vendor_name": "ABC Corp",
    "email": "contact@abccorp.com"
  },
  "validation_results": [
    {
      "field": "invoice_number",
      "rule_type": "REQUIRED_FIELD",
      "status": "PASS"
    },
    {
      "field": "invoice_date",
      "rule_type": "DATE_CHECK",
      "status": "PASS"
    },
    {
      "field": "total_amount",
      "rule_type": "RANGE_CHECK",
      "status": "PASS"
    },
    {
      "field": "currency",
      "rule_type": "ENUM_CHECK",
      "status": "PASS"
    },
    {
      "field": "email",
      "rule_type": "REGEX_MATCH",
      "status": "PASS"
    }
  ],
  "overall_status": "VALID",
  "confidence_score": 0.9
}
```

### 2. Extract Data Only
**POST** `/api/image-validation/extract`

Extract structured data without validation.

**Parameters:**
- `file`: Image file
- `document_type`: Optional document type for context
- `expected_fields`: Optional JSON array of fields

**Response:**
```json
{
  "extracted_data": {
    "invoice_number": "INV-2024-001",
    "total_amount": 1500.00
  },
  "confidence_score": 0.9,
  "extraction_method": "vision_ai"
}
```

### 3. Get Available Document Types
**GET** `/api/image-validation/document-types`

List all document types with available rules.

**Response:**
```json
{
  "document_types": ["invoice", "receipt", "id_card"],
  "count": 3
}
```

### 4. Get Rules for Document Type
**GET** `/api/image-validation/rules/{document_type}`

Get validation rules for a specific document type.

**Response:**
```json
{
  "document_type": "invoice",
  "rules": [
    {
      "field": "invoice_number",
      "type": "REQUIRED_FIELD"
    },
    {
      "field": "invoice_date",
      "type": "DATE_CHECK",
      "condition": "PAST"
    },
    {
      "field": "total_amount",
      "type": "RANGE_CHECK",
      "min": 1
    }
  ]
}
```

### 5. Batch Validation
**POST** `/api/image-validation/validate-batch`

Validate multiple images in one request.

**Parameters:**
- `files`: Multiple image files (max 10)
- `document_type`: Document type for all images

**Response:**
```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "valid_documents": 2,
  "results": [
    {
      "file_name": "invoice1.jpg",
      "index": 0,
      "status": "success",
      "overall_status": "VALID",
      "extracted_data": {...},
      "validation_results": [...]
    }
  ]
}
```

## Rule Configuration

### Rule Types

#### 1. REQUIRED_FIELD
```json
{
  "field": "invoice_number",
  "type": "REQUIRED_FIELD"
}
```

#### 2. REGEX_MATCH
```json
{
  "field": "email",
  "type": "REGEX_MATCH",
  "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
}
```

#### 3. RANGE_CHECK
```json
{
  "field": "total_amount",
  "type": "RANGE_CHECK",
  "min": 1,
  "max": 1000000
}
```

#### 4. DATE_CHECK
```json
{
  "field": "invoice_date",
  "type": "DATE_CHECK",
  "condition": "PAST"
}
```

#### 5. ENUM_CHECK
```json
{
  "field": "currency",
  "type": "ENUM_CHECK",
  "values": ["INR", "USD", "EUR", "GBP"]
}
```

## Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Add to your `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the Server
```bash
cd backend
python main.py
```

The server will start at `http://localhost:8001`

### 4. Access API Documentation
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Testing

### Using cURL

#### Validate an Invoice
```bash
curl -X POST "http://localhost:8001/api/image-validation/validate" \
  -F "file=@invoice.jpg" \
  -F "document_type=invoice"
```

#### Extract Data Only
```bash
curl -X POST "http://localhost:8001/api/image-validation/extract" \
  -F "file=@receipt.jpg" \
  -F "document_type=receipt"
```

#### Get Document Types
```bash
curl "http://localhost:8001/api/image-validation/document-types"
```

#### Get Rules
```bash
curl "http://localhost:8001/api/image-validation/rules/invoice"
```

### Using Python
```python
import requests

# Validate image
with open('invoice.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/image-validation/validate',
        files={'file': f},
        data={'document_type': 'invoice'}
    )
    print(response.json())
```

## Error Handling

### Common Errors

#### 1. Invalid Image Format
```json
{
  "detail": "Unsupported image format: BMP"
}
```

#### 2. Image Size Exceeds Limit
```json
{
  "detail": "Image size exceeds 10MB limit"
}
```

#### 3. Unknown Document Type
```json
{
  "detail": "No rules found for document type: unknown"
}
```

#### 4. Extraction Failure
```json
{
  "detail": "Failed to parse extracted data as JSON"
}
```

## Adding New Document Types

1. Create a new rule file in `backend/app/rules/`:
```json
// purchase_order_rules.json
{
  "document_type": "purchase_order",
  "rules": [
    {
      "field": "po_number",
      "type": "REQUIRED_FIELD"
    },
    {
      "field": "total",
      "type": "RANGE_CHECK",
      "min": 0
    }
  ]
}
```

2. The new document type is automatically available via the API.

## Technical Details

### Technologies Used
- **FastAPI**: High-performance web framework
- **OpenAI GPT-4o**: Vision model for image understanding
- **Pydantic**: Data validation and schema definition
- **Pillow (PIL)**: Image processing
- **pytesseract**: OCR fallback (optional)

### Key Features
- Clean, modular architecture
- Type hints throughout
- Comprehensive error handling
- Singleton service patterns
- Async/await support
- Production-ready code quality

### Performance
- Image validation: ~2-5 seconds per image (Vision AI)
- Batch processing: Up to 10 images concurrently
- Confidence scoring for extraction quality

## Use Cases

1. **Invoice Processing**
   - Extract invoice details
   - Validate mandatory fields
   - Check date validity and amounts

2. **Receipt Scanning**
   - Extract merchant info and totals
   - Validate payment methods
   - Verify transaction dates

3. **ID Verification**
   - Extract identification details
   - Validate ID format
   - Check expiry dates

4. **Document Management**
   - Automated data entry
   - Compliance checking
   - Quality assurance

## Security Considerations

- File size limits (10MB)
- Format validation
- Secure API key handling
- No persistent file storage
- Input sanitization

## Future Enhancements

- [ ] Custom rule definition API
- [ ] Webhook support for async processing
- [ ] Multi-page document support
- [ ] Template matching
- [ ] Advanced OCR with layout analysis
- [ ] Support for more document types
- [ ] Machine learning model for classification

## License
MIT

## Support
For issues and questions, please open an issue on GitHub.
