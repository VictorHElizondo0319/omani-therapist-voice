"""
Pydantic models for emotional analysis and intent detection
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class VoiceRequest(BaseModel):
    """Schema for voice input request"""
    audio_metadata: dict = Field(..., description="Audio payload with mime_type and base64 data")
    session_context: dict = Field(..., description="Session information")

class VoiceResponse(BaseModel):
    """Schema for voice response"""
    transcript: str
    audio_base64: str  # synthesized speech (if you want TTS reply)
    message: str       # optional AI response message


class AnalysisRequest(BaseModel):
    """Model for analysis request"""
    transcript: str = Field(..., description="User input transcript")
    audio_metadata: Optional[Dict[str, Any]] = None
    session_context: Optional[Dict[str, Any]] = None

class CrisisAssessment(BaseModel):
    """Model for crisis risk assessment"""
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    indicators: List[str] = Field(default_factory=list, description="Detected risk indicators")
    requires_intervention: bool = Field(default=False, description="Whether intervention is required")
    escalation_required: bool = Field(default=False, description="Whether escalation is required")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Assessment confidence")

class CulturalContext(BaseModel):
    """Model for cultural context analysis"""
    detected_markers: Dict[str, List[str]] = Field(default_factory=dict)
    requires_religious_sensitivity: bool = Field(default=False)
    family_dynamics_present: bool = Field(default=False)
    social_pressure_indicators: bool = Field(default=False)
    cultural_adaptations_needed: List[str] = Field(default_factory=list)

class EmotionalAnalysis(BaseModel):
    """Model for emotional state analysis"""
    primary_emotion: str = Field(..., description="Primary emotional state")
    emotion_confidence: float = Field(..., ge=0.0, le=1.0)
    secondary_emotions: List[str] = Field(default_factory=list)
    intensity_level: str = Field(default="moderate", description="Emotion intensity: low, moderate, high")
    emotional_triggers: List[str] = Field(default_factory=list)

class AnalysisResponse(BaseModel):
    """Model for analysis response"""
    session_id: str
    transcript: Optional[str] = None
    emotional_state: str = Field(..., description="Detected emotional state")
    intent: str = Field(..., description="Classified intent")
    crisis_assessment: CrisisAssessment
    cultural_context: CulturalContext
    emotional_analysis: Optional[EmotionalAnalysis] = None
    recommended_technique: str = Field(..., description="Recommended therapeutic technique")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall analysis confidence")
    is_crisis: bool = Field(default=False, description="Whether this is a crisis situation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TherapeuticTechnique(BaseModel):
    """Model for therapeutic technique recommendation"""
    technique_name: str = Field(..., description="Name of the therapeutic technique")
    technique_type: str = Field(..., description="Type: active_listening, cognitive_reframing, mindfulness, etc.")
    rationale: str = Field(..., description="Why this technique is recommended")
    implementation_guidance: List[str] = Field(default_factory=list)
    cultural_considerations: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)

class SafetyAssessment(BaseModel):
    """Model for safety assessment"""
    risk_level: str = Field(..., description="Overall safety risk level")
    immediate_concerns: List[str] = Field(default_factory=list)
    intervention_required: bool = Field(default=False)
    escalation_protocols: List[str] = Field(default_factory=list)
    monitoring_required: bool = Field(default=False)
    professional_referral_needed: bool = Field(default=False)
