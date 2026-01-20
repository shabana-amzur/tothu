# Quick Test Guide for Excel Integration

## ✅ Backend is Running
The API documentation is now open in your browser at: http://localhost:8001/docs

## 📊 Testing Excel Features

### Step 1: Login First
Before testing Excel endpoints, you need to authenticate:

1. Scroll to the **Authentication** section
2. Click on `POST /api/auth/login`
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "email": "test@example.com",
     "password": "test123"
   }
   ```
5. Click "Execute"
6. Copy the `access_token` from the response
7. Click the "Authorize" button at the top (🔓)
8. Paste the token in the format: `Bearer YOUR_TOKEN_HERE`
9. Click "Authorize"

### Step 2: Upload Excel File

There's a sample Excel file ready at: `backend/uploads/sample_sales_data.xlsx`

1. Scroll to the **excel** section in the API docs
2. Click on `POST /api/excel/upload`
3. Click "Try it out"
4. Click "Choose File" and select: `C:\Users\Shabana\Desktop\Tothu\backend\uploads\sample_sales_data.xlsx`
5. Click "Execute"
6. Note the `id` from the response (e.g., `"id": 1`)

### Step 3: Get Summary

1. Click on `GET /api/excel/{document_id}/summary`
2. Click "Try it out"
3. Enter the document ID from step 2
4. Click "Execute"
5. You'll see:
   - Row and column counts
   - Column names and types
   - Sample data
   - Sheet names

### Step 4: Ask Questions

1. Click on `POST /api/excel/{document_id}/ask`
2. Click "Try it out"
3. Enter the document ID
4. Enter a question like:
   ```json
   {
     "question": "What is the total revenue?",
     "sheet_name": "Sales"
   }
   ```
5. Click "Execute"
6. The AI will analyze the data and provide an answer!

## 💡 Example Questions to Try:

- "What is the total revenue?"
- "What is the average quantity sold?"
- "Which product generated the most revenue?"
- "How many unique products are there?"
- "What is the revenue for Widget A?"
- "Show me the top 3 products by sales"
- "What percentage of sales is from the North region?"

## 📁 Sample Data Structure

The sample file contains:
- **Sales Sheet**: 50 rows of sales data
  - Date, Product, Quantity, Price, Region, Total
- **Summary Sheet**: Aggregated data by product

## 🔍 What to Look For

✅ **Upload Response** should include:
- document_id
- file information
- row/column counts
- sheet names

✅ **Summary Response** should show:
- Complete data structure
- Column types
- Sample rows
- Statistics

✅ **Q&A Response** should provide:
- Natural language answer
- Based on actual data analysis
- Accurate calculations

## 🎯 Success Indicators

- Upload: Status 201, returns document info
- Summary: Status 200, shows data details
- Ask: Status 200, returns intelligent answer

## 📝 Notes

- Maximum file size: 50MB
- Supported formats: .xlsx, .xls, .xlsm, .csv
- AI uses Google Gemini for analysis
- All files are user-specific (requires authentication)

---

**Current Status:**
- ✅ Backend Running: http://localhost:8001
- ✅ API Docs: http://localhost:8001/docs
- ✅ Sample File: backend/uploads/sample_sales_data.xlsx
- ✅ Test User: test@example.com / test123

**Ready to test!** 🚀
