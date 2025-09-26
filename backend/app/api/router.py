"""
Main API router for OMANI-Therapist-Voice
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from datetime import datetime
import base64

from app.core.database import get_db, ConversationSession, ConversationTurn
from app.services.therapy_service import TherapyService
from app.services.ai_service import AIService
from app.services.speech_service import SpeechService
from app.models.conversation import ConversationCreate, ConversationResponse
from app.models.analysis import AnalysisRequest, AnalysisResponse, VoiceRequest, VoiceResponse

router = APIRouter()

# Initialize services
therapy_service = TherapyService()
ai_service = AIService()
speech_service = SpeechService()

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new conversation session"""
    try:
        # Create new conversation session
        session = ConversationSession(
            user_id=conversation_data.user_id,
            language=conversation_data.language or "omani-arabic",
            cultural_context=conversation_data.cultural_context,
            emergency_contacts=conversation_data.emergency_contacts
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Initialize services if needed
        if not therapy_service.is_initialized:
            await therapy_service.initialize()
        
        return ConversationResponse(
            session_id=str(session.id),
            created_at=session.created_at,
            language=session.language,
            status="active"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

@router.post("/conversations/{session_id}/analyze", response_model=AnalysisResponse)
async def analyze_input(
    session_id: str,
    analysis_request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze user input for emotional state and intent"""
    try:
        # Validate session exists
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Analyze user input
        analysis = await therapy_service.analyze_user_input(
            analysis_request.transcript
        )
        
        return AnalysisResponse(
            session_id=session_id,
            emotional_state=analysis["emotional_state"],
            intent=analysis["intent"],
            crisis_assessment=analysis["crisis_assessment"],
            cultural_context=analysis["cultural_context"],
            recommended_technique=analysis["recommended_technique"],
            confidence=analysis["confidence"],
            is_crisis=analysis["is_crisis"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/conversations/{session_id}")
async def get_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    try:
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        turns = db.query(ConversationTurn).filter(
            ConversationTurn.session_id == session_id
        ).order_by(ConversationTurn.created_at).all()
        
        return {
            "session": {
                "id": str(session.id),
                "created_at": session.created_at,
                "language": session.language,
                "is_crisis_session": session.is_crisis_session,
                "turn_count": session.turn_count
            },
            "turns": [
                {
                    "turn_number": turn.turn_number,
                    "user_transcript": turn.user_transcript,
                    "ai_response": turn.ai_response_text,
                    "created_at": turn.created_at,
                    "emotional_analysis": turn.user_emotional_analysis,
                    "cultural_adaptations": turn.cultural_adaptations
                }
                for turn in turns
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")

@router.post("/conversations/{session_id}/process_voice", 
            #  response_model=VoiceResponse
             )
async def process_voice(
    session_id: str,
    voice_request: VoiceRequest,
    db: Session = Depends(get_db)
):
    """Process voice input: STT -> Analysis -> AI Response -> TTS"""
    try:
        # Validate session exists
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        audio_b64 = voice_request.audio_metadata.get("base64")
        if not audio_b64:
            raise HTTPException(status_code=400, detail="Missing audio base64 data")
        
        audio_bytes = base64.b64decode(audio_b64)

        if not speech_service.is_initialized:
            await speech_service.initialize()
        # Step 1: Speech-to-Text
        transcript = await speech_service.speech_to_text(audio_bytes)
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not process speech")
        
        # # Step 2: Analyze input
        analysis = await therapy_service.analyze_user_input(transcript)

        # # Step 3: Generate AI response
        response = await ai_service.generate_response(
            transcript=transcript,
            analysis=analysis,
            session_id=session_id
        ) 
        # # Step 4: Text-to-Speech
        audio_response = await speech_service.text_to_speech(response["text"])
        return {
            "transcript": transcript,
            "response": response,
            "audio": audio_response,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
@router.post("/conversations/{session_id}/end")
async def end_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """End a conversation session"""
    try:
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.ended_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Conversation ended successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end conversation: {str(e)}")

@router.get("/health")
async def health_check():
    """Comprehensive health check for all services"""
    try:
        return {
            "status": "healthy",
            "services": {
                "therapy_service": await therapy_service.health_check(),
                "ai_service": await ai_service.health_check(),
                "speech_service": await speech_service.health_check()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
