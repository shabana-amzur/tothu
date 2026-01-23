# 🎨 Testing Image Validation from the Chatbot

## ✅ Setup Complete!

Image validation is now integrated into your chatbot interface at **http://localhost:3000**

---

## 🖼️ How to Test

### Method 1: Using the Chatbot UI

1. **Open the chatbot**: http://localhost:3000

2. **Look for the purple image icon** 📷 at the bottom (next to the attachment icon)

3. **Click the image icon** to open the Image Validation panel

4. **Select document type**:
   - Invoice
   - Receipt  
   - ID Card

5. **Click "Choose Image File"** and select an image (JPG, PNG, JPEG)

6. **Click "Validate"** to process the image

7. **See the results** in the chat with:
   - ✅ Extracted data from the image
   - ✅ Validation results for each rule
   - ✅ Overall VALID/INVALID status
   - ✅ Confidence score

---

## 🎯 What You'll See

### Example Result in Chat:

```
## 📋 Image Validation Results

**Document Type:** invoice
**Overall Status:** ✅ VALID
**Confidence Score:** 90.0%

### Extracted Data:
{
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "total_amount": 1500.00,
  "currency": "USD",
  "vendor_name": "ABC Corp",
  "email": "contact@abccorp.com"
}

### Validation Results:

✅ invoice_number (REQUIRED_FIELD): PASS
✅ invoice_date (DATE_CHECK): PASS
✅ total_amount (RANGE_CHECK): PASS
✅ currency (ENUM_CHECK): PASS
✅ vendor_name (REQUIRED_FIELD): PASS
✅ email (REGEX_MATCH): PASS
```

---

## 🧪 Testing Options

### Option A: Test with Sample Images
Create or download sample images of:
- Invoices
- Receipts
- ID cards

### Option B: Use the Swagger UI
http://localhost:8001/docs
- Go to `/api/image-validation/validate`
- Click "Try it out"
- Upload an image
- Select document type
- Execute

### Option C: Use cURL
```bash
curl -X POST "http://localhost:8001/api/image-validation/validate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@path/to/invoice.jpg" \
  -F "document_type=invoice"
```

---

## 🎨 UI Features Added

1. **Purple Image Button** 🖼️
   - Click to toggle image validation panel
   - Located next to file upload button

2. **Image Validation Panel**
   - Document type dropdown (invoice/receipt/id_card)
   - File chooser for images
   - Validate button
   - Shows selected image details

3. **Results Display**
   - Formatted markdown in chat
   - Color-coded validation results
   - JSON formatted extracted data
   - Overall status with emoji indicators

---

## 📊 Document Types & Rules

### Invoice
- ✅ invoice_number (required)
- ✅ invoice_date (must be past)
- ✅ total_amount (must be > 0)
- ✅ currency (INR, USD, EUR, GBP)
- ✅ vendor_name (required)
- ✅ email (valid format)

### Receipt
- ✅ receipt_number (required)
- ✅ date (must be past)
- ✅ total (must be > 0)
- ✅ merchant_name (required)
- ✅ payment_method (CASH, CARD, UPI, NET_BANKING)

### ID Card
- ✅ id_number (required, alphanumeric format)
- ✅ full_name (required)
- ✅ date_of_birth (must be past)
- ✅ expiry_date (must be future)

---

## 🚀 Quick Test Steps

1. Open http://localhost:3000
2. Login if needed
3. Click the purple 🖼️ icon at bottom
4. Select "Invoice" from dropdown
5. Click "Choose Image File"
6. Select an invoice image
7. Click "Validate"
8. See results in chat!

---

## 💡 Tips

- **Max file size**: 10MB
- **Supported formats**: JPG, PNG, JPEG
- **Best results**: Clear, well-lit images with readable text
- **Processing time**: 2-5 seconds per image
- **Confidence score**: Higher is better (>80% is good)

---

## 🐛 Troubleshooting

**No image button?**
- Refresh the page
- Check frontend is running on port 3000

**Validation failing?**
- Ensure OpenAI API key is set in `.env`
- Check image is clear and readable
- Verify image file size < 10MB

**No results?**
- Check browser console for errors
- Verify backend is running on port 8001
- Check `/tmp/backend.log` for errors

---

## 🎉 You're Ready!

The image validation feature is fully integrated into your chatbot. Just click the purple image icon and start validating documents!

**Pro Tip**: You can switch between document types to test different validation rules on the same image.
