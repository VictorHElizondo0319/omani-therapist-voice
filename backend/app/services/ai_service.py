"""
AI service for therapeutic response generation (OpenAI GPT-4o only)
"""

import logging
from typing import Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AIService:
    """Handles AI model interactions with OpenAI only"""

    def __init__(self):
        self.openai_client: AsyncOpenAI | None = None
        self.gemini_client: Any = None  # Placeholder for future Google Gemini client
        self.is_initialized = False

        # Model configuration
        self.primary_model = settings.OPENAI_API_MODEL or "gpt-4o-mini"
        self.duel_model = settings.GOOGLE_AI_MODEL or "gemini-2.5-flash-lite"

        self.max_tokens = 800
        self.temperature = 0.7

    async def initialize(self):
        """Initialize AI service client"""
        try:
            if not settings.OPENAI_API_KEY:
                raise ValueError("Missing OPENAI_API_KEY in settings")

            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            if settings.GOOGLE_API_KEY:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.gemini_client = genai.GenerativeModel(self.duel_model)
            else:
                logger.warning("Missing GOOGLE_API_KEY; Google Gemini will not be used.")

            self.is_initialized = True
            logger.info("AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise

    async def generate_response(
        self,
        transcript: str,
        analysis: Dict[str, Any],
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Generate therapeutic response using GPT-4o
        """
        if not self.is_initialized:
            await self.initialize()

        context = self._build_therapeutic_context(transcript, analysis, session_id)

        try:
            # Build GPT-4o prompt
            prompt = self._build_gpt4_prompt(context)

            response = await self.openai_client.chat.completions.create(
                model=self.primary_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"{settings.CULTURAL_CONTEXT_PROMPT}\n\n"
                            "You are a mental health counselor specializing in Omani Arabic dialect. "
                            "Respond empathetically, using culturally sensitive therapeutic language. "
                            "Always reply in Arabic unless the user specifically requests English."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            response_text = response.choices[0].message.content.strip()
            logger.info(f"GPT-4o reply: {response_text}")

            ##TODO Safety check with Claude (simulated here as a placeholder)
            gemini_prompt = self._build_safety_check_prompt(transcript, response_text)
            gemini_response = self.gemini_client.generate_content(gemini_prompt)

            safety_check = gemini_response.text.strip() if gemini_response else "APPROVED"
            logger.info(f"Gemini safety check: {safety_check}")
            print(safety_check)
            # --- Step 3: Fusion ---
            if safety_check.upper().startswith("APPROVED"):
                final_response_text = response_text
            else:
                final_response_text = safety_check

            print(final_response_text)
            # Apply cultural adaptations
            final_response = await self._apply_cultural_adaptations(
                {"text": final_response_text, "confidence": 0.85}, analysis
            )

            return {
                "text": final_response["text"],
                "model_used": f"{self.primary_model},{self.duel_model}",
                "confidence": final_response["confidence"],
                "cultural_adaptations": final_response.get("adaptations", []),
                "therapeutic_techniques": final_response.get("techniques", []),
                "safety_assessment": final_response.get("safety", {}),
            }

        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            return self._generate_fallback_response(transcript, analysis)

    def _build_therapeutic_context(
        self,
        transcript: str,
        analysis: Dict[str, Any],
        session_id: str,
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI models"""
        return {
            "user_input": transcript,
            "emotional_state": analysis.get("emotional_state", "neutral"),
            "intent": analysis.get("intent", "general_conversation"),
            "cultural_context": analysis.get("cultural_context", {}),
            "session_metadata": {
                "session_id": session_id,
                "turn_number": analysis.get("turn_number", 1),
                "is_crisis": analysis.get("is_crisis", False),
            },
            "therapeutic_goals": [
                "Provide empathetic support",
                "Offer culturally appropriate guidance",
                "Maintain therapeutic boundaries",
                "Ensure user safety",
            ],
        }

    async def _apply_cultural_adaptations(
        self, response: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply Omani cultural adaptations to response"""
        text = response["text"]
        adaptations = []

        if "الله" in text or "إن شاء الله" in text:
            adaptations.append("religious_sensitivity")
        if any(term in text for term in ["عائلة", "والدين", "إخوان", "أخوات"]):
            adaptations.append("family_context")
        if any(term in text for term in ["مجتمع", "عادات", "تقاليد"]):
            adaptations.append("social_norms")
        if any(term in text for term in ["علاج", "نفسي", "استشارة", "دعم"]):
            adaptations.append("therapeutic_terminology")

        response["adaptations"] = adaptations
        response["techniques"] = ["active_listening", "empathetic_response"]

        # Simple safety placeholder
        response["safety"] = {"risk_level": "low", "intervention_required": False}
        return response

    def _build_gpt4_prompt(self, context: Dict[str, Any]) -> str:
        """Build GPT-4o prompt"""
        return f"""
        User Input (Omani Arabic): {context['user_input']}

        Emotional State: {context['emotional_state']}
        Intent: {context['intent']}
        Turn Number: {context['session_metadata']['turn_number']}
        Crisis Session: {context['session_metadata']['is_crisis']}

        Please provide a therapeutic response that:
        1. Is empathetic and supportive
        2. Uses appropriate Omani Arabic dialect
        3. Incorporates Islamic values when relevant
        4. Respects cultural norms and family dynamics
        5. Uses proper mental health terminology in Arabic
        6. Maintains therapeutic boundaries
        7. Ensures user safety

        Respond in Arabic unless the user specifically requests English.
        Keep response concise but meaningful (2-3 sentences).
        """

    def _build_safety_check_prompt(self, transcript: str, primary_text: str)-> str:
        """Build safety check prompt for Claude"""
        return f"""
            User said: {transcript}

            GPT-4o replied: {primary_text}

            Task: Review this reply for:
            - Empathy and supportive tone
            - Omani Arabic dialect appropriateness
            - Cultural sensitivity (Islamic/family/social norms)
            - Safety (no harmful or triggering content)

            If the reply is fine, answer: APPROVED.
            If changes are needed, output the improved reply directly.
            """
    def _generate_fallback_response(
        self, transcript: str, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate safe fallback response when AI services fail"""
        fallback_responses = {
            "crisis": "أفهم أنك تمر بوقت صعب. هل يمكنك مشاركة المزيد حول ما تشعر به؟ أنا هنا لمساعدتك.",
            "anxiety": "القلق أمر طبيعي أحياناً. دعنا نتحدث عن طرق للتعامل مع هذه المشاعر.",
            "sadness": "أرى أنك تشعر بالحزن. هذا شعور طبيعي. هل تريد التحدث عما يزعجك؟",
            "general": "شكراً لك على مشاركة مشاعرك معي. كيف يمكنني مساعدتك اليوم؟",
        }
        emotional_state = analysis.get("emotional_state", "general")
        response_text = fallback_responses.get(emotional_state, fallback_responses["general"])

        return {
            "text": response_text,
            "model_used": "fallback",
            "confidence": 0.5,
            "cultural_adaptations": ["emergency_fallback"],
            "therapeutic_techniques": ["active_listening"],
            "safety_assessment": {"risk_level": "low", "intervention_required": False},
        }

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "primary_model": self.primary_model,
        }

    async def cleanup(self):
        self.openai_client = None
        self.is_initialized = False
        logger.info("AI service cleaned up")
