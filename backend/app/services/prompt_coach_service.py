"""
AI Prompt coach built on Gemini Live/Pro.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class PromptCoachService:
    """Provides quick critique + rewrite suggestions."""

    def __init__(self):
        self.enabled = settings.PROMPT_COACH_ENABLED and bool(settings.GEMINI_API_KEY)
        self.model = None
        self.sessions: Dict[str, Dict] = {}
        if self.enabled:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.PROMPT_COACH_MODEL)
            except Exception as exc:
                logger.error("Prompt coach initialization failed: %s", exc)
                self.enabled = False

    def start_session(self, user_id: str) -> Dict[str, str]:
        if not self.enabled:
            raise RuntimeError("Prompt coach disabled")
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "messages": [],
        }
        return {"session_id": session_id}

    async def critique_prompt(self, session_id: str, prompt: str) -> Dict[str, List[str]]:
        if not self.enabled or not self.model:
            raise RuntimeError("Prompt coach disabled")
        if session_id not in self.sessions:
            raise ValueError("Session not found")

        instructions = (
            "Act as a creative director for Veo/Imagen/Lyria prompts. "
            "Rate clarity, cinematic detail, safety compliance, and supply a"
            " bullet list of actionable fixes. Return JSON with 'summary',"
            " 'score', and 'recommendations'."
        )

        response = await asyncio.to_thread(
            self.model.generate_content,
            f"{instructions}\nUSER PROMPT:\n{prompt}\n",
            generation_config={"response_mime_type": "application/json"},
        )
        data = self._parse_response(response)
        entry = {"prompt": prompt, "response": data, "timestamp": datetime.utcnow()}
        self.sessions[session_id]["messages"].append(entry)
        return data

    def _parse_response(self, response):
        try:
            return genai.types.content_types.from_json(response.text)
        except Exception:
            return {"summary": response.text, "recommendations": []}


prompt_coach_service = PromptCoachService()
