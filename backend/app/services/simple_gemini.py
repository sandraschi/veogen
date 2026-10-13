"""
Emergency Gemini Fix - Simple working text generation
"""

import asyncio
import logging
import os

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class SimpleGeminiService:
    """Simple, working Gemini service with proper fallbacks"""

    def __init__(self):
        self.model = None
        self.initialized = False
        self._initialize()

    def _initialize(self):
        """Initialize with working model"""
        try:
            # API key comes from environment (.env) - never hardcode keys in source.
            api_key = os.getenv("GOOGLE_API_KEY", "")

            if api_key and api_key.startswith("AIza"):
                genai.configure(api_key=api_key)

                # GenerativeModel() makes no API call, so a try/except fallback chain
                # here never fired; the model comes from the config registry instead.
                self.model = genai.GenerativeModel(settings.GEMINI_FLASH_MODEL)
                logger.info("Initialized with %s", settings.GEMINI_FLASH_MODEL)

                self.initialized = True
            else:
                logger.error("No valid API key found")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.initialized = False

    async def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text with working fallbacks"""
        if not self.initialized or not self.model:
            return self._fallback_response(prompt)

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)

            if response and response.text:
                return response.text.strip()
            else:
                return self._fallback_response(prompt)

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Provide intelligent fallback responses"""
        prompt_lower = prompt.lower()

        # Creative Assistant fallback
        if "creative" in prompt_lower or "video" in prompt_lower or "story" in prompt_lower:
            return """✨ Hello! I'm your Creative Assistant, ready to spark your imagination! 

I'd love to help you with video ideas! Here are some exciting directions we could explore:

🎬 **Trending Video Concepts:**
• Short-form storytelling with visual impact
• Behind-the-scenes creative processes  
• Cinematic lifestyle content
• Educational content with stunning visuals

🎥 **VeoGen Features I recommend:**
• Use our AI video generation for concept testing
• Try different artistic styles and moods
• Experiment with various aspect ratios
• Create series with consistent visual themes

What type of video project are you most excited about? I'm here to help brainstorm, plan, and bring your creative vision to life! 🚀

*Note: I'm currently running in offline mode, but I'm still here to help with creative guidance!*"""

        # Technical Guide fallback
        elif "technical" in prompt_lower or "help" in prompt_lower:
            return """🔧 Hello! I'm your Technical Guide, here to help with the technical aspects of your projects.

I can assist with:
• Video specifications and formats
• Optimal settings for different platforms
• Technical troubleshooting
• Workflow optimization
• AI model parameters

What technical challenge can I help you solve today?

*Note: Running in offline mode - for full technical analysis, please check your API configuration.*"""

        # General assistant fallback
        else:
            return """Hello! I'm an AI assistant ready to help you with your creative projects.

While I'm currently running in offline mode, I can still provide guidance on:
• Creative brainstorming and ideas
• Project planning and workflow
• Best practices and techniques
• General assistance and support

How can I help you today? Please let me know what you're working on!

*To enable full AI capabilities, please check the API configuration in settings.*"""


# Create global instance
simple_gemini_service = SimpleGeminiService()
