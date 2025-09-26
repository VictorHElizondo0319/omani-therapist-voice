"""
Database configuration and models
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.config import settings

# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class ConversationSession(Base):
    """Model for storing conversation sessions"""
    __tablename__ = "conversation_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=True)  # Anonymous sessions allowed
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    language = Column(String, default="omani-arabic")
    cultural_context = Column(JSON, nullable=True)
    emergency_contacts = Column(JSON, nullable=True)
    is_crisis_session = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversationTurn(Base):
    """Model for storing individual conversation turns"""
    __tablename__ = "conversation_turns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    turn_number = Column(Integer, nullable=False)
    
    # User input
    user_audio_data = Column(Text, nullable=True)  # Base64 encoded audio
    user_transcript = Column(Text, nullable=True)
    user_emotional_analysis = Column(JSON, nullable=True)
    
    # AI response
    ai_response_text = Column(Text, nullable=True)
    ai_response_audio = Column(Text, nullable=True)  # Base64 encoded audio
    ai_model_used = Column(String, nullable=True)  # "gpt4o" or "claude-opus4"
    cultural_adaptations = Column(JSON, nullable=True)
    
    # Metadata
    processing_time_ms = Column(Integer, nullable=True)
    latency_metrics = Column(JSON, nullable=True)
    safety_flags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SafetyIncident(Base):
    """Model for storing safety-related incidents"""
    __tablename__ = "safety_incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    incident_type = Column(String, nullable=False)  # "crisis", "harmful_content", etc.
    severity_level = Column(String, nullable=False)  # "low", "medium", "high", "critical"
    detected_at = Column(DateTime, default=datetime.utcnow)
    user_input = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    intervention_taken = Column(Text, nullable=True)
    escalation_required = Column(Boolean, default=False)
    escalated_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

class CulturalAdaptation(Base):
    """Model for storing cultural adaptation data"""
    __tablename__ = "cultural_adaptations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    input_text = Column(Text, nullable=False)
    adapted_text = Column(Text, nullable=False)
    adaptation_type = Column(String, nullable=False)  # "terminology", "cultural_context", "religious_sensitivity"
    confidence_score = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
