import os
import io
import wave
import logging
from typing import Optional, List
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
        self.sample_width = 2 # 16-bit

    def generate_chat_response(self, prompt: str, history: List[dict] = None) -> str:
        """Generates a text response using Gemini 3.1 Pro/Flash"""
        try:
            response = self.client.models.generate_content(
                model=self.chat_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are VeoGen Industrial, a premium SOTA media agent.",
                    temperature=0.7
                )
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
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    )
                )
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

# Global instance
gemini_provider = GeminiProvider()
鼓
