"""
Simple working Gemini service
"""

import asyncio
import logging

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class WorkingGeminiService:
    def __init__(self):
        self.model = None
        self.initialized = False
        self._initialize()

    def _initialize(self):
        try:
            if getattr(settings, "GEMINI_API_KEY", None):
                try:
                    genai.configure(api_key=settings.GEMINI_API_KEY)

                    # Try working models in order
                    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
                    for model_name in models:
                        try:
                            self.model = genai.GenerativeModel(model_name)
                            # Test with a simple prompt
                            self.model.generate_content("Test connection")
                            logger.info(f"Successfully initialized with model: {model_name}")
                            self.initialized = True
                            return
                        except Exception as e:
                            logger.warning(f"Failed to initialize with {model_name}: {e}")
                            continue
                except Exception as e:
                    logger.warning(f"Failed to configure Gemini: {e}")

            # If we get here, initialization failed
            logger.warning("Gemini API is not properly configured. Some features may be limited.")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")

        # Set a flag to indicate Gemini is not available
        self.initialized = False

    async def generate_text(self, prompt, temperature=0.7, **kwargs):
        """Generate text with working API"""

        if not self.initialized or not self.model:
            return self._fallback_response(prompt)

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)

            if response and response.text:
                return response.text.strip()
            else:
                return self._fallback_response(prompt)

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt):
        """Intelligent fallback when API fails"""
        if "creative" in prompt.lower():
            return "Hello! I'm your Creative Assistant. While I'm having API connectivity issues right now, I'm still here to help with your creative projects. What would you like to work on today?"
        elif "technical" in prompt.lower():
            return "Hello! I'm your Technical Guide. I'm experiencing some API issues but I'm ready to help with technical guidance. What can I assist you with?"
        else:
            return "Hello! I'm here to help you with your projects. I'm having some connectivity issues with my AI backend, but I'm still ready to provide guidance. What would you like to work on?"


# Global instance
working_gemini = WorkingGeminiService()
