# PROJECT 1: BASIC CHATBOT

## ✅ Implementation Complete

### 📐 Architecture

```
Frontend (Next.js)          Backend (FastAPI)           AI Service
Port 3000                   Port 8000                   
     │                           │                           │
     │   HTTP POST /api/chat     │    LangChain              │
     ├──────────────────────────>│─────────────────────────>│
     │                           │                          │
     │   JSON Response            │   Gemini Response        │
     │<──────────────────────────│<─────────────────────────│
```

---

## 📁 Project Structure

```
Tothu/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration & environment settings
│   │   ├── api/
│   │   │   └── chat.py            # Chat API routes
│   │   ├── models/
│   │   │   └── chat.py            # Pydantic models
│   │   └── services/
│   │       └── chat_service.py    # LangChain + Gemini logic
│   └── main.py                    # FastAPI application
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Chat UI component
│   │   ├── layout.tsx             # Root layout
│   │   └── globals.css            # Global styles
│   ├── package.json
│   └── tsconfig.json
│
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
└── README_PROJECT1.md             # This file
```

---

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - AI orchestration framework
- **Google Gemini API** - LLM for chat responses
- **Pydantic** - Data validation

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Hooks** - State management

---

## 🚀 Installation & Setup

### 1. Backend Setup

```bash
# Navigate to project root
cd /Users/ferozshaik/Desktop/Tothu

# Activate virtual environment
source venv/bin/activate

# Verify dependencies are installed
pip list | grep -E "fastapi|langchain|google-generativeai"

# Environment variables are already configured in .env
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not already done)
npm install

# No additional configuration needed
```

---

## ▶️ Running the Application

### Terminal 1: Start Backend

```bash
cd /Users/ferozshaik/Desktop/Tothu
source venv/bin/activate
cd backend
uvicorn main:app --reload --port 8000
```

**Backend will run on:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

### Terminal 2: Start Frontend

```bash
cd /Users/ferozshaik/Desktop/Tothu/frontend
npm run dev
```

**Frontend will run on:** http://localhost:3000

---

## 📡 API Endpoints

### POST /api/chat
Send a message to the AI assistant.

**Request Body:**
```json
{
  "message": "What is artificial intelligence?",
  "conversation_history": [
    {
      "role": "user",
      "content": "Hello!",
      "timestamp": "2026-01-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help you?",
      "timestamp": "2026-01-15T10:00:01Z"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Artificial Intelligence (AI) is the simulation of human intelligence...",
  "timestamp": "2026-01-15T10:00:02Z",
  "model": "gemini-1.5-pro"
}
```

### GET /api/chat/model-info
Get information about the current AI model.

**Response:**
```json
{
  "model": "gemini-1.5-pro",
  "temperature": "0.7",
  "max_tokens": "2048"
}
```

### GET /health
Health check endpoint.

---

## 🎨 Features Implemented

### Backend Features
- ✅ FastAPI with CORS enabled
- ✅ LangChain integration with Google Gemini
- ✅ Conversation history support (context-aware responses)
- ✅ Proper error handling
- ✅ Async/await for performance
- ✅ Logging system
- ✅ Configuration management
- ✅ API documentation (Swagger/OpenAPI)

### Frontend Features
- ✅ ChatGPT-style interface
- ✅ Message bubbles (user/assistant differentiation)
- ✅ Real-time message updates
- ✅ Loading states with spinner
- ✅ Auto-scroll to latest message
- ✅ Timestamp display
- ✅ Error handling with user feedback
- ✅ Responsive design
- ✅ Disabled input during loading

---

## 🧪 Testing the Application

### Test 1: Basic Chat
1. Open http://localhost:3000
2. Type: "Hello, who are you?"
3. Press Send
4. Verify AI responds appropriately

### Test 2: Conversation Context
1. Send: "What is Python?"
2. Wait for response
3. Send: "Can you give me an example?"
4. Verify AI remembers Python context

### Test 3: Error Handling
1. Stop backend server
2. Try sending a message
3. Verify error message appears

---

## 🔐 Environment Variables

All configured in `.env`:

```env
# Google Gemini API
GOOGLE_GEMINI_API_KEY=AIzaSyDwK-M85lwn_FfbqOiBhQ5OlnnpDVdjTO8
GEMINI_MODEL=gemini-1.5-pro

# Server Configuration
FASTAPI_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📝 Code Architecture Details

### Backend Service Layer
**`chat_service.py`** handles all AI logic:
- Formats conversation history for LangChain
- Manages system prompts
- Calls Gemini via LangChain
- Returns structured responses

### API Layer
**`chat.py`** handles HTTP requests:
- Validates input with Pydantic
- Calls service layer
- Returns formatted JSON responses
- Handles errors gracefully

### Frontend State Management
**`page.tsx`** manages UI state:
- Messages array (conversation history)
- Input state (user typing)
- Loading state (API calls)
- Auto-scroll on new messages

---

## 🐛 Common Issues & Solutions

### Issue: CORS Error
**Solution:** Verify ALLOWED_ORIGINS in `.env` includes `http://localhost:3000`

### Issue: Backend won't start
**Solution:** 
```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9
```

### Issue: Frontend won't start
**Solution:**
```bash
# Kill process on port 3000
lsof -ti :3000 | xargs kill -9
```

### Issue: API Key Error
**Solution:** Verify `GOOGLE_GEMINI_API_KEY` in `.env` is valid

---

## 📊 Performance Notes

- **Response Time:** ~1-3 seconds (depends on Gemini API)
- **Conversation Context:** Maintains full history (will optimize in Project 4)
- **Concurrent Users:** Backend supports multiple simultaneous connections

---

## 🎯 What's Next?

**Project 2: Database + Employee Login**
- Add PostgreSQL/Supabase
- User authentication
- Persistent chat storage
- User management

---

## ✅ Project 1 Checklist

- [x] FastAPI backend setup
- [x] LangChain integration
- [x] Google Gemini API connection
- [x] REST endpoint /api/chat
- [x] Conversation history support
- [x] Next.js frontend setup
- [x] ChatGPT-style UI
- [x] Message bubbles
- [x] Loading states
- [x] Error handling
- [x] CORS configuration
- [x] Documentation

---

## 📚 Documentation Links

- **FastAPI:** https://fastapi.tiangolo.com
- **LangChain:** https://python.langchain.com
- **Gemini API:** https://ai.google.dev/docs
- **Next.js:** https://nextjs.org/docs

---

**Status:** ✅ PROJECT 1 COMPLETE
**Date:** January 15, 2026
**Version:** 1.0.0
