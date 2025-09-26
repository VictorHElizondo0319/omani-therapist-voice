"""
Configuration settings for the OMANI-Therapist-Voice application
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OMANI-Therapist-Voice"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://yourdomain.com"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/omani_therapist")

    # AI Services
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_MODEL: str = os.getenv("OPENAI_API_MODEL", "gpt-4o-mini")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_AI_MODEL: str = os.getenv("GOOGLE_AI_MODEL", "gemini-2.5-flash-lite")

    # Performance Settings
    MAX_CONCURRENT_CONVERSATIONS: int = 100
    CONVERSATION_TIMEOUT_SECONDS: int = 1800  # 30 minutes
    MAX_AUDIO_DURATION_SECONDS: int = 60
    
    # Therapeutic Settings
    CRISIS_KEYWORDS: List[str] = [
        "انتحار", "قتل نفسي", "أريد أن أموت", "لا أستطيع العيش",
        "suicide", "kill myself", "want to die", "can't live"
    ]
    
    # Cultural Adaptation
    OMANI_DIALECT_MODEL: str = "omani-arabic-v1"
    CULTURAL_CONTEXT_PROMPT: str = """

    You are a virtual therapist speaking in the Omani Arabic dialect.
        Your role is to listen with empathy and calmness, and reply with
        short, clear voice-friendly responses that make the user feel safe
        and supported.

        Core guidelines:
        - Always reply in natural Omani Arabic conversational style.
        - Focus more on listening and understanding than giving orders
          or ready-made solutions.
        - Use simple, everyday words and avoid heavy clinical terms.
        - Show respect for Islamic values, family dynamics, and cultural norms.
        - If the user shows signs of serious crisis (e.g., thoughts of self-harm),
          stop normal conversation, respond with a safe supportive message,
          and direct them to seek immediate professional help.
        - If the user mixes Arabic and English, respond in the same way
          while keeping the main tone in Omani Arabic.

    """
    
    # Safety & Compliance
    HIPAA_COMPLIANCE_MODE: bool = True
    DATA_RETENTION_DAYS: int = 30
    EMERGENCY_CONTACT_REQUIRED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
