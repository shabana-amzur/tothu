# 🚀 Quick Start Guide - Project 10: Image Rule Validation API

## The Problem That Was Fixed

**Issue:** The backend was taking a long time and timing out.  
**Root Cause:** Import error in `image_extraction_service.py`  
**Solution:** Fixed import statement from `settings` to `get_settings()`  
**Status:** ✅ RESOLVED - Backend now starts in ~2 seconds

---

## ✅ Current Status

**Backend Server:** Running on http://localhost:8001  
**API Status:** All endpoints working  
**Test Results:** 3/3 API tests passing  

---

## 🎯 What You Can Do Now

### 1. View API Documentation
Open in browser:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

### 2. Test the API

```bash
# Get available document types
curl http://localhost:8001/api/image-validation/document-types

# Get rules for invoice
curl http://localhost:8001/api/image-validation/rules/invoice

# Run automated tests
python3 test_image_validation.py
```

### 3. Test with a Real Image

```bash
# With an invoice image
python3 test_image_validation.py --image /path/to/invoice.jpg --type invoice

# With a receipt image
python3 test_image_validation.py --image /path/to/receipt.jpg --type receipt

# Interactive mode
python3 test_image_validation.py --interactive
```

### 4. Create Custom Rules

```bash
# Interactive rule creator
python3 create_rules.py

# Generate all sample rules
python3 create_rules.py --generate-samples
```

---

## 📋 Available Document Types

The API currently supports these document types:
- ✅ **invoice** - Invoice validation with 6 rules
- ✅ **receipt** - Receipt validation with 5 rules  
- ✅ **id_card** - ID card validation with 5 rules

---

## 🎨 Example API Usage

### Using cURL
```bash
# Validate an invoice
curl -X POST "http://localhost:8001/api/image-validation/validate" \
  -F "file=@invoice.jpg" \
  -F "document_type=invoice"

# Extract data without validation
curl -X POST "http://localhost:8001/api/image-validation/extract" \
  -F "file=@receipt.jpg" \
  -F "document_type=receipt"
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
    result = response.json()
    print(f"Status: {result['overall_status']}")
    print(f"Confidence: {result['confidence_score']}")
```

### Using JavaScript/TypeScript
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('document_type', 'invoice');

const response = await fetch('http://localhost:8001/api/image-validation/validate', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Status: ${result.overall_status}`);
```

---

## 📦 Key Features

### Rule Types
- ✅ **REQUIRED_FIELD** - Must exist and not be empty
- ✅ **REGEX_MATCH** - Must match pattern
- ✅ **RANGE_CHECK** - Must be within numeric range
- ✅ **DATE_CHECK** - Must be past/future date
- ✅ **ENUM_CHECK** - Must be one of allowed values

### API Features
- ✅ Single image validation
- ✅ Batch processing (up to 10 images)
- ✅ Data extraction without validation
- ✅ Dynamic rule loading
- ✅ Confidence scoring
- ✅ OCR fallback
- ✅ File size validation (10MB max)

---

## 🔑 Required Environment Variables

Make sure your `.env` file has:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

The OpenAI API key is required for the Vision API to extract data from images.

---

## 📁 Project Structure

```
backend/app/
├── api/
│   └── image_validation.py          # 5 API endpoints
├── services/
│   ├── image_extraction_service.py   # OpenAI Vision extraction
│   └── rule_validation_service.py    # Rule validation engine
├── schemas/
│   └── image_validation.py           # Pydantic models
└── rules/
    ├── invoice_rules.json            # Invoice validation rules
    ├── receipt_rules.json            # Receipt validation rules
    └── id_card_rules.json            # ID card validation rules
```

---

## 🎓 Example Workflow

1. **Upload Image** → POST to `/api/image-validation/validate`
2. **Extract Data** → OpenAI Vision processes image
3. **Load Rules** → System loads rules for document type
4. **Validate** → Each rule checked against extracted data
5. **Return Results** → Get validation results + overall status

---

## 🐛 Troubleshooting

### Backend not responding?
```bash
# Check if backend is running
ps aux | grep uvicorn

# Check logs
tail -50 /tmp/backend.log

# Restart backend
pkill -f uvicorn
cd backend && python main.py
```

### Import errors?
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # or 'venv\Scripts\activate' on Windows

# Install/update dependencies
pip install -r requirements.txt
```

### OpenAI API errors?
- Verify your `OPENAI_API_KEY` is set in `.env`
- Check your OpenAI account has credits
- Ensure you have access to GPT-4 with vision

---

## 📚 Documentation Files

- **PROJECT10_README.md** - Complete documentation with all details
- **PROJECT10_SUMMARY.md** - Implementation summary and results
- **QUICK_START.md** - This file!

---

## 🎉 Ready to Use!

Your Image Rule Validation API is fully operational. You can now:

1. ✅ Extract data from images using OpenAI Vision
2. ✅ Validate extracted data against custom rules
3. ✅ Process batches of images
4. ✅ Create custom validation rules
5. ✅ Integrate with your applications

**Test it now:**
```bash
python3 test_image_validation.py
```

**Need help?** Check the full documentation in `PROJECT10_README.md`

---

**Happy Coding! 🚀**
