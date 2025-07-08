"""
Simple, working persona chat service using direct Gemini API
"""

import google.generativeai as genai
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SimplePersonaChatService:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple persona definitions
        self.personas = {
            'creative_assistant': {
                'name': 'Creative Assistant',
                'description': 'Helps with creative projects and video ideas',
                'system_prompt': 'You are a creative assistant helping with video and content creation. Be enthusiastic and offer practical suggestions.'
            },
            'technical_helper': {
                'name': 'Technical Helper', 
                'description': 'Assists with technical questions and coding',
                'system_prompt': 'You are a technical assistant. Provide clear, accurate technical advice and code examples.'
            },
            'video_expert': {
                'name': 'Video Expert',
                'description': 'Specializes in video production and editing',
                'system_prompt': 'You are a video production expert. Help with filming, editing, and video creation techniques.'
            }
        }
    
    def get_personas(self) -> list:
        """Get available personas"""
        return [
            {
                'id': persona_id,
                'name': persona_data['name'],
                'description': persona_data['description']
            }
            for persona_id, persona_data in self.personas.items()
        ]
    
    async def start_conversation(self, persona_id: str, initial_message: str, user_id: str = None) -> Dict[str, Any]:
        """Start a new conversation with a persona"""
        try:
            if persona_id not in self.personas:
                raise ValueError(f"Persona {persona_id} not found")
            
            persona = self.personas[persona_id]
            
            # Create conversation ID
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{persona_id}"
            
            # Build prompt with persona context
            full_prompt = f"{persona['system_prompt']}\n\nUser: {initial_message}\n\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            response_text = response.text
            
            return {
                'conversation_id': conversation_id,
                'persona': {
                    'id': persona_id,
                    'name': persona['name'],
                    'description': persona['description']
                },
                'response': {
                    'content': response_text,
                    'type': 'text',
                    'timestamp': datetime.now().isoformat()
                },
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error in start_conversation: {e}")
            return {
                'conversation_id': 'error',
                'persona': {'id': persona_id, 'name': 'Error', 'description': 'Error occurred'},
                'response': {
                    'content': f"I apologize, but I encountered an error: {str(e)}",
                    'type': 'error',
                    'timestamp': datetime.now().isoformat()
                },
                'status': 'error'
            }

# Create singleton instance
simple_persona_service = SimplePersonaChatService()
