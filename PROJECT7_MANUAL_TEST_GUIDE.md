# 🧪 Project 7 Testing Guide - Document Upload + RAG

## Date: January 20, 2026
## Status: Ready for Testing

---

## 📋 What is Project 7?

Project 7 implements **RAG (Retrieval Augmented Generation)** which allows users to:
1. Upload documents (PDF, TXT, DOCX)
2. Ask questions about the uploaded documents
3. Get AI-powered answers grounded in the document content

---

## 🎯 Features to Test

### ✅ Feature 1: Document Upload
- Upload PDF files
- Upload TXT files  
- Upload DOCX files
- File size limit: 10MB per file
- Multiple documents per thread supported

### ✅ Feature 2: RAG-based Question Answering
- AI reads document content
- AI answers questions based ONLY on document content
- AI cites document names in responses
- AI says "I cannot find this information" if answer not in document

### ✅ Feature 3: Thread Isolation
- Documents are thread-specific
- Each thread has its own document collection
- No document leakage between threads
- ChromaDB vector store manages isolation

---

## 🚀 Step-by-Step Testing Instructions

### Prerequisites:
1. ✅ Backend server running on http://localhost:8001
2. ✅ Frontend server running on http://localhost:3000
3. ✅ User logged in (registration or Google OAuth)

---

### Test 1: Upload a TXT Document

#### Steps:
1. **Open the frontend**: http://localhost:3000
2. **Login** if not already logged in
3. **Create a new thread** (click "New Chat" button in sidebar)
4. **Look for the file upload section** in the chat input area
5. **Click "Choose File"** or the upload button (📎 icon)
6. **Select test_rag_document.txt** from `/Users/ferozshaik/Desktop/Tothu/`
7. **Click "Upload"** button
8. **Wait for confirmation message**: 
   ```
   ✅ Document uploaded successfully!
   test_rag_document.txt is being processed and will be available shortly.
   You can now ask questions about this document...
   ```

#### Expected Results:
- ✅ File uploads without errors
- ✅ Success message appears in chat
- ✅ No error messages in browser console
- ✅ Backend logs show: "Processing document for thread X"

---

### Test 2: Ask Questions About the Document

After uploading the test document, ask these questions:

#### Question 1: Basic Information
**Ask:** "Who is the CEO of TechCorp?"

**Expected Answer:**
```
The CEO of TechCorp Solutions is Sarah Johnson.
[Document: test_rag_document.txt]
```

✅ **Pass Criteria:**
- Answer is "Sarah Johnson" 
- AI mentions document name
- No hallucination or external knowledge used

---

#### Question 2: Specific Product Details
**Ask:** "What is the price of CloudSync Pro?"

**Expected Answer:**
```
CloudSync Pro costs $29.99 per month and includes 2TB of storage.
[Document: test_rag_document.txt]
```

✅ **Pass Criteria:**
- Correct price: $29.99/month
- Mentions storage: 2TB
- Cites document name

---

#### Question 3: Statistics
**Ask:** "How many total users does the company have?"

**Expected Answer:**
```
TechCorp Solutions has 1.2 million total users.
[Document: test_rag_document.txt]
```

✅ **Pass Criteria:**
- Correct number: 1.2 million
- Refers to correct metric
- Document cited

---

#### Question 4: Information NOT in Document
**Ask:** "What is the company's stock price?"

**Expected Answer:**
```
I cannot find this information in the uploaded document.
```

✅ **Pass Criteria:**
- AI admits information is not available
- Does NOT hallucinate or guess
- Does NOT use external knowledge
- Proper grounding behavior

---

#### Question 5: Complex Query
**Ask:** "Compare the features and pricing of all three products"

**Expected Answer:**
```
Based on the document, here's a comparison of TechCorp's three products:

1. **CloudSync Pro** - $29.99/month
   - 2TB storage
   - Real-time sync, end-to-end encryption, mobile apps

2. **DataVault Enterprise** - $499/month
   - Unlimited storage
   - Advanced security, compliance tools, API access, 24/7 support

3. **SmartBackup** - $14.99/month
   - 500GB storage
   - Automatic daily backups, version history, disaster recovery

[Document: test_rag_document.txt]
```

✅ **Pass Criteria:**
- All three products mentioned
- Correct prices for each
- Key features listed accurately
- Well-formatted table or list
- Document cited

---

### Test 3: Multiple Documents per Thread

#### Steps:
1. **In the same thread**, create another test document:
   
   Create file: `test_rag_document2.txt`
   ```
   COMPETITOR ANALYSIS
   
   Main Competitor: CloudStore Inc.
   CEO: Michael Chen
   Founded: 2018
   
   Their Product: CloudStore Ultimate
   Price: $39.99/month
   Storage: 5TB
   Features: AI organization, photo recognition, team collaboration
   
   Market Share: 25%
   User Base: 2.5 million
   Revenue: $95 million
   ```

2. **Upload this second document** to the same thread
3. **Ask:** "Compare TechCorp and CloudStore's user base and revenue"

**Expected Answer:**
```
Based on the uploaded documents:

**TechCorp Solutions:**
- Users: 1.2 million
- Revenue: $45 million

**CloudStore Inc. (Competitor):**
- Users: 2.5 million  
- Revenue: $95 million

CloudStore has a larger user base and higher revenue.
[Documents: test_rag_document.txt, test_rag_document2.txt]
```

✅ **Pass Criteria:**
- AI uses information from BOTH documents
- Correct numbers for both companies
- Both document names cited
- Accurate comparison

---

### Test 4: Thread Isolation (No Document Leakage)

#### Steps:
1. **Create a NEW thread** (click "New Chat" in sidebar)
2. **WITHOUT uploading any document**, ask: "Who is the CEO of TechCorp?"

**Expected Answer:**
```
I cannot find this information in the uploaded document.
```
OR (if no documents in thread):
```
I don't have any context about TechCorp. Could you provide more information?
```

✅ **Pass Criteria:**
- AI does NOT remember documents from other threads
- No access to previous thread's documents
- Proper isolation confirmed

---

### Test 5: PDF Upload (If Available)

#### Steps:
1. **Create a new thread**
2. **Find or create a PDF file** (any PDF will work)
3. **Upload the PDF**
4. **Ask questions about the PDF content**

✅ **Pass Criteria:**
- PDF uploads successfully
- Text extracted from PDF
- AI can answer questions about PDF content
- Same RAG behavior as TXT files

---

## 🔍 Technical Verification

### Backend Logs to Check:
```
✅ "Processing document: test_rag_document.txt"
✅ "Extracted X characters from document"
✅ "Document processed: X chunks created"
✅ "Document saved for thread X"
✅ "RAG enabled for thread X"
✅ "Retrieved Y relevant chunks for query"
✅ "Using RAG with Y chunks for user..."
```

### ChromaDB Verification:
```bash
# Check ChromaDB collections
ls -la /Users/ferozshaik/Desktop/Tothu/backend/chroma_db/

# Should see:
# - chroma.sqlite3 (database file)
# - Collections for each thread: thread_{user_id}_{thread_id}
```

### Database Verification:
Check `documents` table:
```sql
SELECT id, user_id, thread_id, filename, file_path, processed 
FROM documents 
WHERE user_id = <your_user_id>;
```

Expected:
- ✅ Document records created
- ✅ Correct thread_id
- ✅ processed = true
- ✅ file_path points to uploaded file

---

## 🐛 Common Issues & Solutions

### Issue 1: "File upload failed"
**Solutions:**
- Check file size (must be < 10MB)
- Check file type (PDF, TXT, DOCX only)
- Check backend logs for detailed error
- Verify thread_id exists

### Issue 2: "Cannot find this information in document"
**Possible Causes:**
- Document not fully processed yet (wait 5-10 seconds)
- Question uses different wording than document
- Information truly not in document (expected behavior)

**Debug:**
- Check backend logs: "Using RAG with X chunks"
- If X = 0, document might not be in vector store
- Try asking a more direct question

### Issue 3: AI uses external knowledge instead of document
**This is a BUG - should not happen**
**Expected:** AI should ONLY use document content
**Solution:** Check system prompt in `/backend/app/services/chat_service.py`

### Issue 4: Document not isolated to thread
**This is a CRITICAL BUG**
**Expected:** Documents should be thread-specific
**Debug:** Check ChromaDB collection names in logs

---

## 📊 Test Results Template

```
TEST DATE: _______________
TESTER: __________________

Test 1: Upload TXT Document
Result: [ ] PASS  [ ] FAIL
Notes: ________________________________

Test 2: Question - CEO Name
Expected: Sarah Johnson
Actual: ________________________________
Result: [ ] PASS  [ ] FAIL

Test 3: Question - Product Price
Expected: $29.99/month
Actual: ________________________________
Result: [ ] PASS  [ ] FAIL

Test 4: Question - User Count
Expected: 1.2 million
Actual: ________________________________
Result: [ ] PASS  [ ] FAIL

Test 5: Question - Info Not in Doc
Expected: "I cannot find..."
Actual: ________________________________
Result: [ ] PASS  [ ] FAIL

Test 6: Complex Comparison Query
Result: [ ] PASS  [ ] FAIL
Notes: ________________________________

Test 7: Multiple Documents
Result: [ ] PASS  [ ] FAIL
Notes: ________________________________

Test 8: Thread Isolation
Result: [ ] PASS  [ ] FAIL
Notes: ________________________________

Test 9: PDF Upload (if tested)
Result: [ ] PASS  [ ] FAIL  [ ] N/A
Notes: ________________________________

OVERALL RESULT: [ ] ALL TESTS PASSED  [ ] SOME FAILURES
```

---

## 🎯 Success Criteria

Project 7 is **FULLY WORKING** if:
- ✅ Documents upload without errors (TXT, PDF, DOCX)
- ✅ AI answers questions using document content
- ✅ AI cites document names in responses
- ✅ AI refuses to answer when info not in document
- ✅ Multiple documents per thread work correctly
- ✅ Thread isolation prevents document leakage
- ✅ ChromaDB stores embeddings correctly
- ✅ No errors in browser console or backend logs

---

## 🔗 Files to Reference

### Frontend:
- `/frontend/app/page.tsx` - File upload UI (lines 270-350)
- Upload button and file input
- Success/error messages

### Backend:
- `/backend/app/api/documents.py` - Upload endpoint
- `/backend/app/services/document_service.py` - Document processing
- `/backend/app/services/rag_service.py` - RAG implementation
- `/backend/app/services/chat_service.py` - RAG integration (lines 90-155)

### Documentation:
- `PROJECT7_README.md` - Full documentation
- `PROJECT7_SUMMARY.md` - Implementation summary
- `PROJECT7_TESTING_GUIDE.md` - Original test guide
- `PROJECT7_API_EXAMPLES.md` - API examples

---

## 📞 Support

If you encounter issues:
1. Check backend logs in terminal
2. Check browser console (F12)
3. Verify servers are running
4. Review documentation files
5. Check ChromaDB directory exists

---

**Project 7 Status: ✅ FULLY IMPLEMENTED**
**Last Updated: January 20, 2026**
**Test Document Located: `/Users/ferozshaik/Desktop/Tothu/test_rag_document.txt`**
