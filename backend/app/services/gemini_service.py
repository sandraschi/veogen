import io
import logging
import os
import wave
from typing import List

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider:
    """
    Industrial v3.1 Gemini Provider for Chat, Reasoning, and Flash TTS.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY (or GEMINI_API_KEY) must be provided.")

        self.client = genai.Client(api_key=self.api_key)
        self.chat_model = settings.GEMINI_PRO_MODEL
        self.flash_model = settings.GEMINI_FLASH_MODEL
        self.tts_model = settings.GEMINI_TTS_MODEL

        # Audio specs for Gemini Flash TTS
        self.sample_rate = 24000
        self.channels = 1
        self.sample_width = 2  # 16-bit

    def generate_chat_response(self, prompt: str, history: List[dict] = None) -> str:
        """Generates a text response using Gemini 3.1 Pro/Flash"""
        try:
            response = self.client.models.generate_content(
                model=self.chat_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are VeoGen Industrial, a premium SOTA media agent.", temperature=0.7
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini Chat generation failed: {e}")
            raise

    def synthesize_speech(self, text: str, voice_name: str = "Kore") -> bytes:
        """
        Generates high-fidelity audio using Gemini 3.1 Flash TTS.
        Supports prosody tags like [whispers], [happy], [excited].
        """
        try:
            response = self.client.models.generate_content(
                model=self.tts_model,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                        )
                    ),
                ),
            )

            # Extract PCM bytes and wrap in WAV
            pcm_bytes = response.candidates[0].content.parts[0].inline_data.data
            return self._pcm_to_wav(pcm_bytes)

        except Exception as e:
            logger.error(f"Gemini TTS synthesis failed: {e}")
            raise

    def _pcm_to_wav(self, pcm_bytes: bytes) -> bytes:
        """Helper to wrap raw PCM in WAV container"""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.sample_width)
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm_bytes)
        return buf.getvalue()


# Global instance - lazy so the app boots without an API key configured.
# Media endpoints fail at request time with an explicit error instead of
# crashing the whole server at import time.
_gemini_provider = None


def get_provider():
    global _gemini_provider
    if _gemini_provider is None:
        _gemini_provider = GeminiProvider()
    return _gemini_provider


class GeminiServiceFacade:
    """Compatibility facade for the interface the v1 endpoints expect.

    Phase 2 salvage: the v3.1 rewrite replaced the old gemini_service
    module with GeminiProvider but never updated the importers, so the
    endpoints import a name that no longer exists. This facade restores
    the old interface:

    - Chat/text (generate_content/generate_text) delegates to the real
      GeminiProvider.
    - Media generation (video/image/music) is NOT wired: the v3.1 media
      stack was never finished (simulated responses, mismatched service
      interfaces, dead MCP bridge, unverifiable model IDs). It returns an
      explicit error instead of fake data. Wiring real media calls is
      follow-up work that needs the user's API key and current model IDs.
    """

    def __init__(self):
        self.provider = None  # lazily initialized via get_provider()

    # --- Chat / text (real) ---
    def generate_content(self, prompt: str, **kwargs) -> str:
        return get_provider().generate_chat_response(prompt)

    async def generate_text(self, prompt: str, **kwargs) -> str:
        return get_provider().generate_chat_response(prompt)

    def initialize(self, db_session=None, user_id=None, **kwargs):
        return True

    # --- Media generation (honest stubs until wired) ---
    @staticmethod
    def _media_unavailable(kind: str) -> dict:
        return {
            "status": "error",
            "message": (
                f"{kind} generation is not wired in this build. "
                "Set a valid Google API key and current model IDs in .env "
                "(see config.py GEMINI_*/VEO_*/LYRIA_*/IMAGEN_* settings)."
            ),
            "error_type": "provider_not_wired",
        }

    async def generate_video(self, **kwargs) -> dict:
        return self._media_unavailable("Video")

    async def generate_image(self, **kwargs) -> dict:
        return self._media_unavailable("Image")

    async def generate_music(self, **kwargs) -> dict:
        return self._media_unavailable("Music")


gemini_service = GeminiServiceFacade()
