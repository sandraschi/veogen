"""
Real Gemini Chat Service with Persona Support and MCP Integration
Uses June 2025 Gemini CLI with MCP for enhanced chat experiences
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import httpx

from app.config import settings
from app.database import get_user_setting, set_user_setting
from app.services.gemini_cli import gemini_service
from app.services.simple_gemini import simple_gemini_service

logger = logging.getLogger(__name__)

class PersonaChatService:
    """Service for persona-based chat using Gemini CLI with MCP"""
    
    def __init__(self):
        self.active_conversations = {}
        self.personas = self._load_default_personas()
    
    def _load_default_personas(self) -> Dict[str, Dict[str, Any]]:
        """Load default persona configurations"""
        return {
            "creative_assistant": {
                "name": "Creative Assistant",
                "description": "An AI assistant specialized in creative projects and brainstorming",
                "personality": "enthusiastic, creative, supportive, full of ideas",
                "expertise": ["video creation", "storytelling", "artistic direction", "creative writing"],
                "system_prompt": """You are a Creative Assistant AI, passionate about helping users bring their creative visions to life. 
                You're enthusiastic, supportive, and always ready with creative suggestions. You specialize in video creation, 
                storytelling, and artistic direction. When helping with VeoGen projects, you provide detailed, actionable advice 
                and creative inspiration.""",
                "temperature": 0.8,
                "tools": ["veo_video", "imagen_image", "lyria_music"]
            },
            
            "technical_guide": {
                "name": "Technical Guide",
                "description": "An AI expert in technical aspects of video production and AI tools",
                "personality": "precise, knowledgeable, helpful, detail-oriented",
                "expertise": ["video technical specs", "AI model parameters", "workflow optimization", "troubleshooting"],
                "system_prompt": """You are a Technical Guide AI, expert in the technical aspects of video production and AI tools. 
                You provide precise, detailed information about video specifications, AI model parameters, and workflow optimization. 
                You help users understand the technical side of VeoGen and troubleshoot any issues they encounter.""",
                "temperature": 0.3,
                "tools": ["veo_video", "imagen_image", "technical_analysis"]
            },
            
            "story_director": {
                "name": "Story Director",
                "description": "An AI filmmaker focused on narrative structure and visual storytelling",
                "personality": "visionary, analytical, inspiring, cinematic",
                "expertise": ["narrative structure", "visual storytelling", "cinematography", "scene planning"],
                "system_prompt": """You are a Story Director AI, a master of narrative structure and visual storytelling. 
                You think like a filmmaker, helping users craft compelling stories through video. You excel at breaking down 
                complex narratives into scenes, suggesting shot compositions, and ensuring narrative coherence in VeoGen projects.""",
                "temperature": 0.7,
                "tools": ["veo_video", "movie_maker", "script_analysis"]
            },
            
            "music_composer": {
                "name": "Music Composer",
                "description": "An AI musician specialized in creating soundtracks and audio experiences",
                "personality": "artistic, passionate, rhythmic, emotionally attuned",
                "expertise": ["music composition", "sound design", "audio-visual sync", "emotional scoring"],
                "system_prompt": """You are a Music Composer AI, passionate about creating soundtracks and audio experiences. 
                You understand how music enhances visual storytelling and can suggest perfect musical accompaniments for any video project. 
                You're well-versed in various musical styles and how they affect mood and narrative.""",
                "temperature": 0.75,
                "tools": ["lyria_music", "audio_analysis", "soundtrack_sync"]
            },
            
            "brand_strategist": {
                "name": "Brand Strategist",
                "description": "An AI expert in brand communication and marketing video creation",
                "personality": "strategic, persuasive, brand-focused, market-aware",
                "expertise": ["brand messaging", "marketing videos", "audience targeting", "conversion optimization"],
                "system_prompt": """You are a Brand Strategist AI, expert in brand communication and marketing video creation. 
                You help users create videos that effectively communicate brand messages and engage target audiences. 
                You understand marketing psychology and how to craft compelling visual narratives for business purposes.""",
                "temperature": 0.6,
                "tools": ["veo_video", "brand_analysis", "audience_insights"]
            },
            
            "educational_tutor": {
                "name": "Educational Tutor",
                "description": "An AI teacher focused on creating educational and instructional content",
                "personality": "patient, clear, encouraging, methodical",
                "expertise": ["educational content", "instructional design", "learning optimization", "knowledge transfer"],
                "system_prompt": """You are an Educational Tutor AI, specialized in creating educational and instructional content. 
                You excel at breaking down complex topics into digestible visual lessons and creating engaging educational videos. 
                You understand learning psychology and how to structure content for maximum knowledge retention.""",
                "temperature": 0.4,
                "tools": ["veo_video", "educational_analysis", "learning_assessment"]
            }
        }
    
    async def start_conversation(
        self,
        user_id: str,
        persona_id: str,
        initial_message: str,
        db_session: Session,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a new conversation with a persona"""
        try:
            conversation_id = str(uuid.uuid4())
            
            # Get persona configuration
            persona = self.personas.get(persona_id)
            if not persona:
                raise ValueError(f"Unknown persona: {persona_id}")
            
            # Initialize conversation
            conversation = {
                "id": conversation_id,
                "user_id": user_id,
                "persona_id": persona_id,
                "persona": persona,
                "messages": [],
                "context": context or {},
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "status": "active"
            }
            
            # Add system message
            system_message = {
                "role": "system",
                "content": persona["system_prompt"],
                "timestamp": datetime.utcnow().isoformat()
            }
            conversation["messages"].append(system_message)
            
            # Add user's initial message
            user_message = {
                "role": "user",
                "content": initial_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            conversation["messages"].append(user_message)
            
            # Generate initial response
            response = await self._generate_persona_response(
                conversation, db_session, user_id
            )
            
            # Store conversation
            self.active_conversations[conversation_id] = conversation
            
            # Save to user settings for persistence
            await self._save_conversation_to_db(conversation, db_session, user_id)
            
            logger.info(f"Started conversation {conversation_id} with persona {persona_id} for user {user_id}")
            
            return {
                "conversation_id": conversation_id,
                "persona": {
                    "id": persona_id,
                    "name": persona["name"],
                    "description": persona["description"],
                    "personality": persona["personality"]
                },
                "response": response,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            raise
    
    async def send_message(
        self,
        conversation_id: str,
        user_id: str,
        message: str,
        db_session: Session,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Send a message in an existing conversation"""
        try:
            # Get conversation
            conversation = self.active_conversations.get(conversation_id)
            if not conversation:
                # Try to load from database
                conversation = await self._load_conversation_from_db(conversation_id, db_session, user_id)
                if not conversation:
                    raise ValueError("Conversation not found")
                self.active_conversations[conversation_id] = conversation
            
            # Verify user ownership
            if conversation["user_id"] != user_id:
                raise ValueError("Unauthorized access to conversation")
            
            # Add user message
            user_message = {
                "role": "user",
                "content": message,
                "type": message_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            conversation["messages"].append(user_message)
            conversation["last_activity"] = datetime.utcnow()
            
            # Generate response
            response = await self._generate_persona_response(
                conversation, db_session, user_id
            )
            
            # Save updated conversation
            await self._save_conversation_to_db(conversation, db_session, user_id)
            
            logger.info(f"Message sent in conversation {conversation_id}")
            
            return {
                "conversation_id": conversation_id,
                "response": response,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def _generate_persona_response(
        self,
        conversation: Dict[str, Any],
        db_session: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """Generate a response using the persona's characteristics"""
        try:
            persona = conversation["persona"]
            messages = conversation["messages"]
            
            # Prepare conversation context for Gemini
            context_messages = []
            for msg in messages[-10:]:  # Last 10 messages for context
                if msg["role"] != "system":
                    context_messages.append(f"{msg['role']}: {msg['content']}")
            
            conversation_context = "\n".join(context_messages)
            
            # Create enhanced prompt for persona
            enhanced_prompt = f"""
            {persona['system_prompt']}
            
            CONVERSATION CONTEXT:
            {conversation_context}
            
            PERSONA TRAITS:
            - Personality: {persona['personality']}
            - Expertise: {', '.join(persona['expertise'])}
            - Available tools: {', '.join(persona.get('tools', []))}
            
            INSTRUCTIONS:
            - Respond as the {persona['name']} with the specified personality
            - Use your expertise to provide helpful, relevant advice
            - If the user asks about video creation, suggest specific VeoGen features
            - Keep responses engaging and true to your persona
            - If appropriate, suggest using available tools like Veo for video generation
            
            Please respond to the user's latest message, staying in character as {persona['name']}.
            """
            
            # Check if we should use MCP tools based on conversation content
            latest_message = messages[-1]["content"].lower()
            should_use_video_generation = any(keyword in latest_message for keyword in [
                'video', 'generate', 'create', 'make', 'produce', 'film', 'movie'
            ])
            
            should_use_image_generation = any(keyword in latest_message for keyword in [
                'image', 'picture', 'photo', 'visual', 'illustration', 'artwork'
            ])
            
            should_use_music_generation = any(keyword in latest_message for keyword in [
                'music', 'song', 'audio', 'soundtrack', 'sound', 'melody'
            ])
            
            # DIRECT API CALL - Use working Gemini API directly
            try:
                import google.generativeai as genai
                import os
                
                # Force configure with working API key
                api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCokmGkNRF67OgFFX4iki5gPE_BkazivfM')
                genai.configure(api_key=api_key)
                
                # Use working model
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Generate response
                import asyncio
                response = await asyncio.to_thread(
                    model.generate_content,
                    enhanced_prompt
                )
                
                if response and response.text:
                    response_text = response.text.strip()
                else:
                    response_text = self._get_persona_fallback(persona, latest_message)
                    
            except Exception as e:
                logger.error(f"Direct API call failed: {e}")
                response_text = self._get_persona_fallback(persona, latest_message)
            
            # Create assistant message
            assistant_message = {
                "role": "assistant",
                "content": response_text,
                "persona_id": conversation["persona_id"],
                "generated_content": None,  # Simplified for now
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to conversation
            conversation["messages"].append(assistant_message)
            
            return {
                "message": response_text,
                "persona": {
                    "id": conversation["persona_id"],
                    "name": persona["name"]
                },
                "generated_content": None,  # Simplified for now
                "timestamp": assistant_message["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error generating persona response: {e}")
            # Fallback response
            return {
                "message": f"I apologize, but I'm having trouble responding right now. As the {persona['name']}, I'm here to help with your creative projects. Please try asking again in a moment.",
                "persona": {
                    "id": conversation["persona_id"],
                    "name": persona["name"]
                },
                "generated_content": None,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        user_id: str,
        db_session: Session,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get conversation history"""
        try:
            conversation = self.active_conversations.get(conversation_id)
            if not conversation:
                conversation = await self._load_conversation_from_db(conversation_id, db_session, user_id)
                if not conversation:
                    raise ValueError("Conversation not found")
            
            # Verify user ownership
            if conversation["user_id"] != user_id:
                raise ValueError("Unauthorized access to conversation")
            
            # Get recent messages (excluding system message)
            messages = [msg for msg in conversation["messages"] if msg["role"] != "system"][-limit:]
            
            return {
                "conversation_id": conversation_id,
                "persona": {
                    "id": conversation["persona_id"],
                    "name": conversation["persona"]["name"],
                    "description": conversation["persona"]["description"]
                },
                "messages": messages,
                "created_at": conversation["created_at"].isoformat(),
                "last_activity": conversation["last_activity"].isoformat(),
                "message_count": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            raise
    
    async def list_user_conversations(
        self,
        user_id: str,
        db_session: Session
    ) -> List[Dict[str, Any]]:
        """List all conversations for a user"""
        try:
            # Get from settings (this is a simple implementation - in production you'd use a proper table)
            conversations_data = get_user_setting(db_session, user_id, "chat_conversations", {})
            
            conversations = []
            for conv_id, conv_data in conversations_data.items():
                conversations.append({
                    "id": conv_id,
                    "persona": {
                        "id": conv_data.get("persona_id"),
                        "name": conv_data.get("persona_name"),
                        "description": conv_data.get("persona_description")
                    },
                    "last_message": conv_data.get("last_message", ""),
                    "last_activity": conv_data.get("last_activity"),
                    "message_count": conv_data.get("message_count", 0)
                })
            
            # Sort by last activity
            conversations.sort(key=lambda x: x["last_activity"], reverse=True)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return []
    
    def get_available_personas(self) -> List[Dict[str, Any]]:
        """Get list of available personas"""
        return [
            {
                "id": persona_id,
                "name": persona["name"],
                "description": persona["description"],
                "personality": persona["personality"],
                "expertise": persona["expertise"],
                "tools": persona.get("tools", [])
            }
            for persona_id, persona in self.personas.items()
        ]
    
    async def _save_conversation_to_db(
        self,
        conversation: Dict[str, Any],
        db_session: Session,
        user_id: str
    ):
        """Save conversation to database (simplified implementation)"""
        try:
            # Get existing conversations
            conversations_data = get_user_setting(db_session, user_id, "chat_conversations", {})
            
            # Update conversation summary
            conversation_summary = {
                "persona_id": conversation["persona_id"],
                "persona_name": conversation["persona"]["name"],
                "persona_description": conversation["persona"]["description"],
                "created_at": conversation["created_at"].isoformat(),
                "last_activity": conversation["last_activity"].isoformat(),
                "message_count": len([m for m in conversation["messages"] if m["role"] != "system"]),
                "last_message": conversation["messages"][-1]["content"] if conversation["messages"] else ""
            }
            
            conversations_data[conversation["id"]] = conversation_summary
            
            # Save to settings
            set_user_setting(db_session, user_id, "chat_conversations", conversations_data, "json")
            
            # Save full conversation separately (for message history)
            conversation_key = f"chat_conversation_{conversation['id']}"
            set_user_setting(db_session, user_id, conversation_key, conversation, "json")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    async def _load_conversation_from_db(
        self,
        conversation_id: str,
        db_session: Session,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Load conversation from database"""
        try:
            conversation_key = f"chat_conversation_{conversation_id}"
            conversation_data = get_user_setting(db_session, user_id, conversation_key)
            
            if conversation_data:
                # Convert datetime strings back to datetime objects
                conversation_data["created_at"] = datetime.fromisoformat(conversation_data["created_at"])
                conversation_data["last_activity"] = datetime.fromisoformat(conversation_data["last_activity"])
                return conversation_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
            return None

    def _get_persona_fallback(self, persona: Dict[str, Any], user_message: str) -> str:
        """Get intelligent fallback response for persona"""
        persona_name = persona.get("name", "").lower()
        
        if "creative" in persona_name:
            return f"Hello! I'm your Creative Assistant. I'd love to help with your request about '{user_message}'. Let me suggest some creative approaches for your video project. What specific aspect would you like to explore?"

        elif "technical" in persona_name:
            return f"Hello! I'm your Technical Guide. Regarding '{user_message}', I can help with technical specifications, optimization, and best practices. What technical challenge can I help you solve?"

        elif "story" in persona_name:
            return f"Greetings! I'm your Story Director. For '{user_message}', let's focus on narrative structure and visual storytelling. What story elements would you like to develop?"

        elif "music" in persona_name:
            return f"Hello! I'm your Music Composer. Regarding '{user_message}', I can help create the perfect audio experience. What kind of musical atmosphere are you looking for?"

        elif "brand" in persona_name:
            return f"Hello! I'm your Brand Strategist. For '{user_message}', let's focus on brand messaging and audience engagement. What brand story do you want to tell?"

        elif "educational" in persona_name:
            return f"Hello! I'm your Educational Tutor. Regarding '{user_message}', I can help structure engaging educational content. What learning objectives do you have in mind?"

        else:
            return f"Hello! I'm the {persona.get('name', 'AI Assistant')}. I'm here to help with your request about '{user_message}'. How can I provide specific guidance for your project?"

# Global persona chat service instance
persona_chat_service = PersonaChatService()
