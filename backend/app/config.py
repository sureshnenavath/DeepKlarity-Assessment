"""
Configuration settings for the DeepKlarity Quiz Generator application.
Loads environment variables and provides application-wide settings.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./deepklarity_quiz.db"
    
    # OpenAI API
    OPENAI_API_KEY: str = ""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Application
    APP_NAME: str = "DeepKlarity Quiz Generator"
    APP_VERSION: str = "1.0.0"
    MAX_QUESTIONS: int = 10
    MIN_CONTENT_WORDS: int = 300
    
    # LLM Settings
    LLM_TEMPERATURE: float = 0.3
    LLM_MODEL: str = "gpt-4o-mini"
    
    # Scraping
    REQUEST_TIMEOUT: int = 30
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Create global settings instance
settings = Settings()
