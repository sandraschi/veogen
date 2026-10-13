"""
Simple, working persona chat service using direct Gemini API
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


class SimplePersonaChatService:
    def __init__(self):
        # Configure Gemini API if key is available
        self.model = None
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini model: {str(e)}")

        # Simple persona definitions
        self.personas = {
            "creative_assistant": {
                "name": "Creative Assistant",
                "description": "Helps with creative projects and video ideas",
                "system_prompt": "You are a creative assistant helping with video and content creation. Be enthusiastic and offer practical suggestions.",
            },
            "technical_helper": {
                "name": "Technical Helper",
                "description": "Assists with technical questions and coding",
                "system_prompt": "You are a technical assistant. Provide clear, accurate technical advice and code examples.",
            },
            "video_expert": {
                "name": "Video Expert",
                "description": "Specializes in video production and editing",
                "system_prompt": "You are a video production expert. Help with filming, editing, and video creation techniques.",
            },
        }

    def get_personas(self) -> list:
        """Get available personas"""
        return [
            {"id": persona_id, "name": persona_data["name"], "description": persona_data["description"]}
            for persona_id, persona_data in self.personas.items()
        ]

    def chat(self, persona_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a message with the specified persona
        """
        if persona_id not in self.personas:
            raise ValueError(f"Unknown persona: {persona_id}")

        persona = self.personas[persona_id]

        if not self.model:
            return {
                "response": "Gemini API is not configured. Please set GEMINI_API_KEY environment variable to enable this feature.",
                "persona": {"id": persona_id, "name": persona["name"], "description": persona["description"]},
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Gemini API not configured",
            }

        try:
            # Create the prompt with context
            prompt = f"""{persona["system_prompt"]}

Context: {json.dumps(context, indent=2) if context else "No context provided"}

User: {message}

Assistant:"""

            # Generate response
            response = self.model.generate_content(prompt)

            # Extract the response text
            response_text = response.text

            # Log the interaction
            logger.info(f"Persona: {persona_id}, Input: {message}, Response: {response_text}")

            return {
                "response": response_text,
                "persona": {"id": persona_id, "name": persona["name"], "description": persona["description"]},
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in start_conversation: {e}")
            return {
                "conversation_id": "error",
                "persona": {"id": persona_id, "name": "Error", "description": "Error occurred"},
                "response": {
                    "content": f"I apologize, but I encountered an error: {str(e)}",
                    "type": "error",
                    "timestamp": datetime.now().isoformat(),
                },
                "status": "error",
            }


# Create singleton instance with error handling
try:
    simple_persona_service = SimplePersonaChatService()
except Exception as e:
    logger.warning(f"Could not initialize SimplePersonaChatService: {str(e)}")

    # Create a dummy instance that will return error messages
    class DummyPersonaService:
        def chat(self, *args, **kwargs):
            return {
                "response": "Gemini API is not configured. Please set GEMINI_API_KEY environment variable to enable this feature.",
                "error": "Gemini API not configured",
            }

    simple_persona_service = DummyPersonaService()
