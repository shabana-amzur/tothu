"""
FastAPI Backend Application
Integrated with: Google Gemini, LangChain, Supabase
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Tothu API",
    description="FastAPI backend with Gemini, LangChain, and Supabase",
    version="1.0.0"
)

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Tothu API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "gemini": "configured" if os.getenv("GOOGLE_GEMINI_API_KEY") else "not configured",
            "supabase": "configured" if os.getenv("NEXT_PUBLIC_SUPABASE_URL") else "not configured"
        }
    }


@app.get("/api/test-gemini")
async def test_gemini():
    """Test Gemini API connection"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            return {"error": "Gemini API key not configured"}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Say hello in one sentence!")
        
        return {
            "status": "success",
            "message": "Gemini API is working",
            "response": response.text
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/test-supabase")
async def test_supabase():
    """Test Supabase connection"""
    try:
        from supabase import create_client
        
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        if not url or not key:
            return {"error": "Supabase credentials not configured"}
        
        supabase = create_client(url, key)
        
        return {
            "status": "success",
            "message": "Supabase client initialized",
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
