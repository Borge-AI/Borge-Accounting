"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import json
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Database (must be real connection string; use Railway "Add Reference" for PostgreSQL)
    DATABASE_URL: str
    
    # JWT (set in Railway Variables; e.g. generate with: openssl rand -hex 32)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # OCR
    TESSERACT_CMD: str = "/usr/bin/tesseract"
    
    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: Union[str, List[str]] = '["http://localhost:3000", "http://localhost:3001"]'
    PORT: int = 8000
    
    @field_validator('DATABASE_URL', mode='after')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or "(Auto-set)" in v or v.strip() == "(Auto-set)":
            raise ValueError(
                "DATABASE_URL must be the real PostgreSQL URL. "
                "In Railway: remove any manual DATABASE_URL, then use Variables → Add Reference → select your PostgreSQL service → DATABASE_URL."
            )
        return v

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from JSON string or return as-is if already a list."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, treat as comma-separated string
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # File upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
