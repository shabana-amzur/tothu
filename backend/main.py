"""
Main FastAPI Application
AI Chat Backend - Project 1: Basic Chatbot
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api import chat

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

# Include routers
app.include_router(chat.router)


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
