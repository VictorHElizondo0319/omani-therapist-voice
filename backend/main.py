"""
OMANI-Therapist-Voice Backend
FastAPI application for Omani Arabic mental health chatbot
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.api.router import router as api_router
from app.core.database import engine, Base
from app.core.websocket_manager import WebSocketManager
from app.services.speech_service import SpeechService
from app.services.ai_service import AIService
from app.services.therapy_service import TherapyService
from app.core.config import settings
from scripts.init_database import main as init_db_main
load_dotenv()

# Initialize services
speech_service = SpeechService()
ai_service = AIService()
therapy_service = TherapyService()
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    init_db_main()  # Ensure database and tables are created
    Base.metadata.create_all(bind=engine)
    await speech_service.initialize()
    await ai_service.initialize()
    await therapy_service.initialize()
    # Start websocket cleanup background task now that an event loop is running
    websocket_manager.start_cleanup_task()
    
    yield
    
    # Shutdown
    await speech_service.cleanup()
    await ai_service.cleanup()
    await therapy_service.cleanup()

app = FastAPI(
    title="OMANI-Therapist-Voice",
    description="Omani Arabic Mental Health Chatbot API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "OMANI-Therapist-Voice API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "speech_service": await speech_service.health_check(),
            "ai_service": await ai_service.health_check(),
            "therapy_service": await therapy_service.health_check()
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice conversation"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Process the audio through the speech pipeline
            result = await process_voice_conversation(data, websocket)
            
            # Send response back
            await websocket_manager.send_personal_message(result, websocket)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

async def process_voice_conversation(audio_data: bytes, websocket: WebSocket):
    """
    Main conversation processing pipeline:
    1. Speech-to-Text (STT)
    2. Intent Analysis & Emotional Detection
    3. AI Response Generation (Dual-model)
    4. Cultural Adaptation
    5. Text-to-Speech (TTS)
    """
    try:
        # Step 1: Convert speech to text
        transcript = await speech_service.speech_to_text(audio_data)
        
        if not transcript:
            return {"error": "Could not process speech"}
        
        # Step 2: Analyze intent and emotional state
        analysis = await therapy_service.analyze_user_input(transcript)
        
        # Step 3: Generate therapeutic response using dual-model approach
        response = await ai_service.generate_response(
            transcript=transcript,
            analysis=analysis,
            session_id=websocket_manager.get_session_id(websocket)
        )
        
        # Step 4: Convert response to speech
        audio_response = await speech_service.text_to_speech(response["text"])
        
        return {
            "transcript": transcript,
            "response": response,
            "audio": audio_response,
            "analysis": analysis
        }
        
    except Exception as e:
        return {"error": f"Processing error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
