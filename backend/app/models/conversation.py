"""
Pydantic models for conversation management
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class ConversationCreate(BaseModel):
    """Model for creating a new conversation"""
    user_id: Optional[str] = None
    language: str = Field(default="omani-arabic", description="Conversation language")
    cultural_context: Optional[Dict[str, Any]] = None
    emergency_contacts: Optional[List[Dict[str, str]]] = None

class ConversationResponse(BaseModel):
    """Model for conversation response"""
    session_id: str
    created_at: datetime
    language: str
    status: str

class ConversationTurnCreate(BaseModel):
    """Model for creating a conversation turn"""
    session_id: str
    user_audio_data: Optional[str] = None  # Base64 encoded
    user_transcript: Optional[str] = None
    turn_number: int

class ConversationTurnResponse(BaseModel):
    """Model for conversation turn response"""
    turn_id: str
    session_id: str
    turn_number: int
    user_transcript: Optional[str]
    ai_response_text: Optional[str]
    ai_response_audio: Optional[str]
    processing_time_ms: Optional[int]
    cultural_adaptations: Optional[List[str]]
    safety_flags: Optional[Dict[str, Any]]
    created_at: datetime

class ConversationSummary(BaseModel):
    """Model for conversation summary"""
    session_id: str
    total_turns: int
    duration_minutes: float
    emotional_progression: List[str]
    crisis_interventions: int
    cultural_adaptations_used: List[str]
    therapeutic_techniques_used: List[str]
    overall_sentiment: str
    created_at: datetime
    ended_at: Optional[datetime]
