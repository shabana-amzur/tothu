"""
Main FastAPI Application
AI Chat Backend - Project 1: Basic Chatbot
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from app.config import get_settings
from app.api import chat, auth, documents, nl2sql, excel
from app.api import threads, oauth, image_validation
from app.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # Startup
    logger.info("🚀 Starting AI Chat Application...")
    logger.info(f"📦 Model: {settings.GEMINI_MODEL}")
    logger.info(f"🌡️  Temperature: {settings.GEMINI_TEMPERATURE}")
    
    # Create database tables
    try:
        logger.info("🗄️  Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}")
    
    yield
    # Shutdown
    logger.info("👋 Shutting down AI Chat Application...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Chat Application with FastAPI, LangChain, and Google Gemini",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Session Middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=3600,  # 1 hour session timeout
    same_site="lax",  # Required for OAuth redirects
    https_only=False  # Set to True in production with HTTPS
)

# Include routers
app.include_router(auth.router)
app.include_router(oauth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(threads.router)
app.include_router(nl2sql.router)
app.include_router(excel.router)
app.include_router(image_validation.router)

# Mount static files for serving uploaded documents and generated images
uploads_path = Path("uploads")
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": settings.GEMINI_MODEL,
        "api_configured": bool(settings.GOOGLE_GEMINI_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.FASTAPI_PORT,
        reload=settings.DEBUG
    )
