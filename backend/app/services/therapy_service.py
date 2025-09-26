"""
Hybrid Therapy Service:
- Rule-based crisis detection (regex/keywords)
- LLM-powered emotional & intent analysis
- Safety-first fusion of results
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class TherapyService:
    def __init__(self):
        self.is_initialized = False
        self.client: AsyncOpenAI | None = None

        # Rule-based crisis patterns
        self.crisis_patterns = {
            "suicide_ideation": [
                r"أريد أن أموت", r"قتل نفسي", r"انتحار", r"لا أستطيع العيش",
                r"أفضل الموت", r"لا فائدة من الحياة", r"أريد إنهاء حياتي"
            ],
            "self_harm": [
                r"أجرح نفسي", r"أؤذي نفسي", r"أقطع نفسي", r"أحرق نفسي"
            ],
            "hopelessness": [
                r"لا أمل", r"لا فائدة", r"مستحيل", r"لا أرى مخرج", r"ضائع"
            ]
        }

    async def initialize(self):
        """Initialize with OpenAI client"""
        try:
            if not settings.OPENAI_API_KEY:
                raise ValueError("Missing OPENAI_API_KEY")
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.is_initialized = True
            logger.info("TherapyService initialized with hybrid mode")
        except Exception as e:
            logger.error(f"Failed to initialize TherapyService: {e}")
            raise

    async def analyze_user_input(self, transcript: str) -> Dict[str, Any]:
        """
        Hybrid analysis:
        1. Rule-based analysis
        2. LLM-based analysis
        3. Safety-first fusion
        """
        if not self.is_initialized:
            await self.initialize()

        # --- Step 1: Rule-based ---
        rule_based = self._rule_based_analysis(transcript)

        # --- Step 2: LLM-based ---
        llm_based = await self._llm_based_analysis(transcript)

        # --- Step 3: Fusion ---
        fused = self._fuse_analysis(rule_based, llm_based)
        fused["timestamp"] = datetime.utcnow().isoformat()
        return fused

    def _rule_based_analysis(self, text: str) -> Dict[str, Any]:
        """Detect crisis risk with regex rules"""
        risk_indicators = []
        risk_level = "low"

        for risk_type, patterns in self.crisis_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    risk_indicators.append(risk_type)

        if "suicide_ideation" in risk_indicators or "self_harm" in risk_indicators:
            risk_level = "critical"
        elif "hopelessness" in risk_indicators:
            risk_level = "high"
        elif risk_indicators:
            risk_level = "medium"

        return {
            "source": "rule_based",
            "emotional_state": "neutral",  # regex not strong at emotions
            "intent": "unknown",
            "crisis_assessment": {
                "risk_level": risk_level,
                "indicators": risk_indicators,
                "requires_intervention": risk_level in ["high", "critical"],
                "escalation_required": risk_level == "critical"
            },
            "confidence": 0.6 if risk_indicators else 0.3,
        }

    async def _llm_based_analysis(self, text: str) -> Dict[str, Any]:
        """Use GPT-4o for emotional state, intent, crisis detection"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a therapeutic AI assistant. "
                            "Analyze the user's message and output JSON only. "
                            "Keys: emotional_state, intent, crisis_assessment {risk_level, requires_intervention}, "
                            "recommended_technique, cultural_context {religious, family, social}."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0,
                max_tokens=300,
            )

            parsed = response.choices[0].message.content
            import json
            llm_result = json.loads(parsed)

            return {
                "source": "llm",
                **llm_result,
                "confidence": 0.8,
            }
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return {
                "source": "llm",
                "emotional_state": "neutral",
                "intent": "general_conversation",
                "crisis_assessment": {
                    "risk_level": "low",
                    "requires_intervention": False,
                    "escalation_required": False,
                },
                "confidence": 0.0,
            }

    def _fuse_analysis(self, rule_based: Dict[str, Any], llm_based: Dict[str, Any]) -> Dict[str, Any]:
        """Combine rule-based + LLM with safety-first priority"""
        crisis = rule_based["crisis_assessment"]
        if crisis["risk_level"] in ["high", "critical"]:
            # Rule-based always overrides → deterministic safety
            return {**llm_based, "crisis_assessment": crisis, "is_crisis": True}

        # Otherwise trust LLM more for nuance
        return {**llm_based, "is_crisis": llm_based["crisis_assessment"]["risk_level"] in ["high", "critical"]}
    
    async def cleanup(self):
        """Cleanup resources if needed"""
        self.is_initialized = False
        self.client = None
        logger.info("TherapyService resources cleaned up")
