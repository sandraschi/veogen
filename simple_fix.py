#!/usr/bin/env python3
"""
Simple fix for Gemini API issues
"""

import os
import re

def fix_gemini_config():
    """Fix the Gemini configuration issues"""
    
    print("Fixing Gemini API configuration...")
    
    # Fix 1: Update the config.py to use a working model
    config_path = "backend/app/config.py"
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace the model configuration
        content = re.sub(
            r'GEMINI_MODEL: str = ".*?"',
            'GEMINI_MODEL: str = "gemini-1.5-flash"',
            content
        )
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        print("Fixed config.py model setting")
        
    except Exception as e:
        print(f"Could not fix config.py: {e}")
    
    # Fix 2: Create a simple working generate_text override
    override_path = "backend/app/services/working_gemini.py"
    
    working_service = '''"""
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
'''
    
    try:
        with open(override_path, 'w') as f:
            f.write(working_service)
        print("Created working_gemini.py service")
    except Exception as e:
        print(f"Could not create working service: {e}")

if __name__ == "__main__":
    print("=== Fixing VeoGen Gemini Configuration ===")
    fix_gemini_config()
    print("\nFixes applied! Now:")
    print("1. Get API key from https://aistudio.google.com/")
    print("2. Run: python test_gemini_api.py")
    print("3. Update .env with working key")
    print("4. Restart backend: docker-compose restart backend")
