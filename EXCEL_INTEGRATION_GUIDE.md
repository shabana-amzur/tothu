# Excel and Google Sheets Integration

## Overview
The application now supports uploading and analyzing Excel files (.xlsx, .xls, .csv) with natural language Q&A capabilities.

## Features

### 1. **Upload Excel Files**
- Upload Excel, CSV files up to 50MB
- Supports multiple sheets
- Automatic data validation and summary

### 2. **Data Analysis**
- View data summary (rows, columns, data types)
- Preview sample data
- Get sheet names
- Statistical summaries for numeric columns

### 3. **Natural Language Q&A**
- Ask questions about your data in plain English
- Powered by Google Gemini AI and pandas
- Supports calculations, filtering, aggregations

## API Endpoints

### Upload Excel File
```http
POST /api/excel/upload
Content-Type: multipart/form-data

Parameters:
- file: Excel/CSV file
- thread_id (optional): Associate with a chat thread
```

**Response:**
```json
{
  "id": 1,
  "filename": "uuid.xlsx",
  "original_filename": "sales_data.xlsx",
  "file_size": 12345,
  "file_type": "xlsx",
  "status": "ready",
  "rows": 1000,
  "columns": 5,
  "column_names": ["Date", "Product", "Quantity", "Price", "Total"],
  "sheet_names": ["Sheet1", "Sheet2"],
  "created_at": "2026-01-20T..."
}
```

### Get Excel Summary
```http
GET /api/excel/{document_id}/summary?sheet_name=Sheet1
```

**Response:**
```json
{
  "rows": 1000,
  "columns": 5,
  "column_names": ["Date", "Product", "Quantity", "Price", "Total"],
  "column_types": {
    "Date": "datetime64[ns]",
    "Product": "object",
    "Quantity": "int64",
    "Price": "float64",
    "Total": "float64"
  },
  "sample_data": [
    {
      "Date": "2026-01-01",
      "Product": "Widget A",
      "Quantity": 10,
      "Price": 19.99,
      "Total": 199.90
    }
  ],
  "sheet_names": ["Sheet1", "Sheet2"]
}
```

### Ask Question About Data
```http
POST /api/excel/{document_id}/ask
Content-Type: application/json

{
  "question": "What is the total revenue by product?",
  "sheet_name": "Sheet1"
}
```

**Response:**
```json
{
  "question": "What is the total revenue by product?",
  "answer": "Based on the data:\n- Widget A: $12,450\n- Widget B: $8,320\n- Widget C: $15,670",
  "file_name": "sales_data.xlsx",
  "data_shape": {
    "rows": 1000,
    "columns": 5
  },
  "error": false
}
```

### Get Sheet Names
```http
GET /api/excel/{document_id}/sheets
```

**Response:**
```json
{
  "document_id": 1,
  "filename": "sales_data.xlsx",
  "sheet_names": ["Sheet1", "Sheet2", "Summary"]
}
```

## Example Questions You Can Ask

### Basic Statistics
- "What is the average price?"
- "How many rows are in the dataset?"
- "What is the sum of the Quantity column?"

### Filtering & Aggregation
- "What is the total revenue by product?"
- "Show me sales for Widget A"
- "What products sold more than 100 units?"
- "Which month had the highest sales?"

### Analysis
- "What are the top 5 products by revenue?"
- "Calculate the average order value"
- "What percentage of total sales does Widget A represent?"
- "Find all orders above $1000"

### Comparisons
- "Compare sales between Product A and Product B"
- "What is the price difference between products?"
- "Which product has the highest profit margin?"

## Usage Example (Python)

```python
import requests

# Upload Excel file
with open('sales_data.xlsx', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/excel/upload',
        files={'file': f},
        headers={'Authorization': f'Bearer {token}'}
    )
    document = response.json()
    document_id = document['id']

# Ask a question
question_response = requests.post(
    f'http://localhost:8001/api/excel/{document_id}/ask',
    json={'question': 'What is the total revenue?'},
    headers={'Authorization': f'Bearer {token}'}
)
answer = question_response.json()
print(answer['answer'])
```

## Usage Example (cURL)

```bash
# Upload file
curl -X POST http://localhost:8001/api/excel/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sales_data.xlsx"

# Ask question
curl -X POST http://localhost:8001/api/excel/1/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the average price?"}'
```

## Supported File Formats

- **.xlsx** - Modern Excel format (recommended)
- **.xls** - Legacy Excel format
- **.xlsm** - Excel with macros
- **.csv** - Comma-separated values

## Limitations

- Maximum file size: 50MB
- For very large datasets (>100k rows), consider using aggregated data
- Complex formulas in Excel cells are not evaluated
- Charts and images are ignored

## Security

- Files are isolated per user (authentication required)
- Files can be associated with specific chat threads
- Uploaded files are stored securely with UUID filenames
- Only the uploader can query their files

## Tips for Best Results

1. **Use clear column headers** - This helps the AI understand your data
2. **Keep data clean** - Remove empty rows/columns
3. **Be specific in questions** - "What is the total sales in January 2026?" vs "Show me sales"
4. **Use sheet names** - If your Excel has multiple sheets, specify which one
5. **Check data types** - Use the summary endpoint to verify column types

## Integration with Chat

Excel Q&A can be integrated with the chat interface:
- Upload Excel files within a chat thread
- Ask questions about the data in natural conversation
- Combine with other AI features (RAG, image generation)

## Error Handling

Common errors and solutions:

- **"Invalid or corrupted Excel file"** - Ensure file is a valid Excel/CSV format
- **"File too large"** - Compress data or split into smaller files
- **"Column not found"** - Check column names in the summary
- **"Unable to generate answer"** - Rephrase your question or check if data exists

## Future Enhancements

- Google Sheets integration (connect via Google Drive)
- Real-time collaboration on shared sheets
- Data visualization (charts/graphs)
- Export query results
- Scheduled data updates

---

**Ready to analyze your data!** Upload an Excel file and start asking questions.
