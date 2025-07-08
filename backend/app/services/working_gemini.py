"""
Simple working Gemini service
"""

import google.generativeai as genai
import asyncio
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class WorkingGeminiService:
    def __init__(self):
        self.model = None
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        try:
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                
                # Try working models in order
                models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                
                for model_name in models:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        logger.info(f"Initialized with {model_name}")
                        self.initialized = True
                        break
                    except Exception as e:
                        logger.warning(f"{model_name} failed: {e}")
                        continue
                        
            else:
                logger.warning("No GEMINI_API_KEY found")
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    
    async def generate_text(self, prompt, temperature=0.7, **kwargs):
        """Generate text with working API"""
        
        if not self.initialized or not self.model:
            return self._fallback_response(prompt)
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
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
