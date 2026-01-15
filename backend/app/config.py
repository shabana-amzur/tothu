"""
Application Configuration
Loads environment variables and provides configuration settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Chat Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Keys
    GOOGLE_GEMINI_API_KEY: str
    OPENAI_API_KEY: str = ""  # For future use
    
    # Gemini Model Configuration
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048
    
    # Server Configuration
    FASTAPI_PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Database (for future projects)
    DATABASE_URL: str = ""
    NEXT_PUBLIC_SUPABASE_URL: str = ""
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
