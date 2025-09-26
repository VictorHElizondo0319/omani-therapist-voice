"""
Speech processing service for Omani Arabic STT and TTS (OpenAI-based)
"""

import base64
import logging
import io
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class SpeechService:
    """Handles speech-to-text and text-to-speech operations via OpenAI"""

    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.is_initialized = False

    async def initialize(self):
        """Initialize AI service clients"""
        try:
            if settings.OPENAI_API_KEY:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.is_initialized = True
                logger.info("Speech service initialized successfully")
            else:
                raise ValueError("Missing OPENAI_API_KEY in settings")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise

    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """
        Convert speech audio to text using OpenAI Whisper models
        """
        if not self.client:
            raise RuntimeError("SpeechService not initialized. Call initialize() first.")

        try:
            audio_stream = io.BytesIO(audio_data)

            result = await self.client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=("audio.webm", audio_stream, "audio/webm"),
                language="ar"  # Arabic
            )

            transcript = result.text.strip()
            logger.info(transcript)
            transcript = self._apply_omani_dialect_corrections(transcript)
            logger.info(f"STT result: {transcript}")
            return transcript

        except Exception as e:
            logger.error(f"STT error: {e}")
            return None

    async def text_to_speech(self, text: str, voice_name: str = "verse") -> Optional[str]:
        """
        Convert text to speech using OpenAI TTS
        Optimized for Omani Arabic pronunciation
        """
        if not self.client:
            raise RuntimeError("SpeechService not initialized. Call initialize() first.")

        try:
            adjusted_text = self._apply_omani_pronunciation_adjustments(text)

            response = await self.client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=voice_name,
                input=adjusted_text
            )

            # Convert audio to base64
            audio_base64 = base64.b64encode(response.read()).decode("utf-8")
            logger.info("TTS synthesis completed successfully")
            return audio_base64

        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

    def _apply_omani_dialect_corrections(self, transcript: str) -> str:
        """Apply Omani dialect-specific corrections to transcript"""
        corrections = {
            "شكرا": "شكراً",
            "قلق": "قلق",
            "حزن": "حزن",
            "فرح": "فرح",
            "والدي": "والدي",
            "الله": "الله",
            "الصلاة": "الصلاة",
        }
        for incorrect, correct in corrections.items():
            transcript = transcript.replace(incorrect, correct)
        return transcript

    def _apply_omani_pronunciation_adjustments(self, text: str) -> str:
        """Apply Omani dialect pronunciation adjustments for TTS"""
        adjustments = {
            "إن شاء الله": "إن شاء الله",
            "ما شاء الله": "ما شاء الله",
            "الحمد لله": "الحمد لله",
        }
        for original, adjusted in adjustments.items():
            text = text.replace(original, adjusted)
        return text

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "openai_configured": bool(self.client)}

    async def cleanup(self):
        logger.info("Speech service cleaned up")
        self.is_initialized = False
        self.client = None
