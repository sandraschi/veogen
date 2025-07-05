# AI Chat Personas Service with Generated Life Stories

import asyncio
import logging
import json
import random
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from app.config import settings
from app.database import get_user_setting
from app.middleware.metrics import track_chat_interaction
from app.utils.logging_config import log_user_action
from app.services.gemini_cli import gemini_service
from app.services.mcp_media_service import mcp_media_service
from datetime import datetime

logger = logging.getLogger(__name__)

class PersonaCategory(str, Enum):
    CREATIVE = "creative"
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PHILOSOPHICAL = "philosophical"
    TECHNICAL = "technical"
    HISTORICAL = "historical"
    FANTASY = "fantasy"

class PersonalityTrait(str, Enum):
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"
    WITTY = "witty"
    SERIOUS = "serious"
    EMPATHETIC = "empathetic"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    PRAGMATIC = "pragmatic"

@dataclass
class PersonaBackground:
    name: str
    age: int
    occupation: str
    location: str
    personality_traits: List[PersonalityTrait]
    background_story: str
    expertise_areas: List[str]
    speaking_style: str
    favorite_topics: List[str]
    life_experiences: List[str]
    goals_and_motivations: str
    communication_preferences: str

@dataclass
class ChatPersona:
    id: str
    name: str
    title: str
    category: PersonaCategory
    description: str
    avatar_url: str
    background: PersonaBackground
    system_prompt: str
    sample_conversations: List[Dict[str, str]]
    popularity_score: float = 0.0
    created_at: str = ""

class PersonaService:
    """AI Chat Personas with Generated Life Stories and MCP Integration"""
    
    def __init__(self):
        self.personas: Dict[str, ChatPersona] = {}
        self.initialized = False
        self.gemini_service = gemini_service
        self.mcp_service = mcp_media_service
    
    def _get_api_key_from_user_settings(self, db_session=None, user_id=None, key_name="gemini_api_key"):
        """Get API key from user settings first, then environment variables"""
        try:
            if db_session and user_id:
                # Try to get from user settings first
                user_key = get_user_setting(db_session, user_id, key_name)
                if user_key:
                    return user_key
        except Exception as e:
            logger.warning(f"Could not get API key from user settings: {e}")
        
        # Fall back to environment variables
        if key_name == "gemini_api_key":
            return settings.GEMINI_API_KEY
        elif key_name == "google_api_key":
            return settings.GOOGLE_API_KEY
        elif key_name == "google_cloud_project":
            return settings.GOOGLE_CLOUD_PROJECT
        
        return None
    
    async def initialize(self, db_session=None, user_id=None):
        """Initialize persona service and generate initial personas"""
        try:
            # Initialize Gemini CLI service
            await self.gemini_service.initialize(db_session, user_id)
            
            # Initialize MCP media service
            await self.mcp_service.start_mcp_server("veo", user_id)
            await self.mcp_service.start_mcp_server("imagen", user_id)
            await self.mcp_service.start_mcp_server("lyria", user_id)
            await self.mcp_service.start_mcp_server("chirp", user_id)
            
            # Generate initial set of diverse personas
            await self._generate_initial_personas(db_session, user_id)
            
            self.initialized = True
            logger.info(f"Persona service initialized with {len(self.personas)} personas")
            
        except Exception as e:
            logger.error(f"Failed to initialize persona service: {e}")
            # Create fallback personas without AI generation
            await self._create_fallback_personas()
            self.initialized = True
    
    async def _generate_initial_personas(self, db_session=None, user_id=None):
        """Generate initial diverse set of personas"""
        persona_templates = [
            {
                "name": "Dr. Elena Vasquez",
                "category": PersonaCategory.PROFESSIONAL,
                "title": "Quantum Physics Professor",
                "base_description": "A brilliant quantum physicist with a passion for making complex concepts accessible"
            },
            {
                "name": "Marcus Chen",
                "category": PersonaCategory.CREATIVE,
                "title": "Digital Artist & Storyteller",
                "base_description": "A multimedia artist who blends traditional storytelling with cutting-edge technology"
            },
            {
                "name": "Amara Okafor",
                "category": PersonaCategory.EDUCATIONAL,
                "title": "Learning Experience Designer",
                "base_description": "An educational innovator focused on personalized learning experiences"
            },
            {
                "name": "Captain James Morrison",
                "category": PersonaCategory.HISTORICAL,
                "title": "Naval History Expert",
                "base_description": "A retired naval officer with extensive knowledge of maritime history and exploration"
            },
            {
                "name": "Luna Blackwood",
                "category": PersonaCategory.FANTASY,
                "title": "Mystical Librarian",
                "base_description": "A keeper of ancient knowledge and magical lore from distant realms"
            },
            {
                "name": "Dr. Raj Patel",
                "category": PersonaCategory.TECHNICAL,
                "title": "AI Ethics Researcher",
                "base_description": "A computer scientist specializing in ethical AI development and human-AI interaction"
            },
            {
                "name": "Sofia Rosenberg",
                "category": PersonaCategory.PHILOSOPHICAL,
                "title": "Modern Philosophy Guide",
                "base_description": "A contemporary philosopher exploring the intersection of technology and human experience"
            },
            {
                "name": "Tommy 'The Wise' Williams",
                "category": PersonaCategory.ENTERTAINMENT,
                "title": "Comedy & Life Coach",
                "base_description": "A stand-up comedian who uses humor to help people navigate life's challenges"
            }
        ]
        
        for template in persona_templates:
            try:
                persona = await self._generate_detailed_persona(template, db_session, user_id)
                self.personas[persona.id] = persona
            except Exception as e:
                logger.error(f"Failed to generate persona {template['name']}: {e}")
                # Create fallback persona
                fallback_persona = self._create_fallback_persona(template)
                self.personas[fallback_persona.id] = fallback_persona
    
    async def _generate_detailed_persona(self, template: Dict[str, Any], db_session=None, user_id=None) -> ChatPersona:
        """Generate detailed persona with full background story using Gemini CLI"""
        try:
            # Use Gemini CLI for persona generation
            background_prompt = f"""
            Create a detailed, engaging background story for this character:
            
            Name: {template['name']}
            Title: {template['title']}
            Category: {template['category'].value}
            Base Description: {template['base_description']}
            
            Please provide a comprehensive background including:
            1. Age and personal details
            2. Occupation and expertise areas
            3. Location and cultural background
            4. Personality traits (choose 3-4 from: enthusiastic, calm, witty, serious, empathetic, analytical, creative, pragmatic)
            5. A compelling life story
            6. Speaking style and communication preferences
            7. Favorite topics and interests
            8. Key life experiences
            9. Goals and motivations
            
            Format the response as JSON with these fields:
            - age: int
            - occupation: string
            - location: string
            - personality_traits: list of strings
            - background_story: string
            - expertise_areas: list of strings
            - speaking_style: string
            - favorite_topics: list of strings
            - life_experiences: list of strings
            - goals_and_motivations: string
            - communication_preferences: string
            """
            
            # Generate background using Gemini CLI
            background_response = await self.gemini_service.generate_text(
                background_prompt,
                temperature=0.8,
                max_tokens=2000,
                db_session=db_session,
                user_id=user_id
            )
            
            # Parse the response
            try:
                background_data = json.loads(background_response)
            except json.JSONDecodeError:
                # Fallback to default background
                background_data = self._create_default_background(template)
            
            # Create background object
            background = PersonaBackground(
                name=template['name'],
                age=background_data.get('age', 35),
                occupation=background_data.get('occupation', template['title']),
                location=background_data.get('location', 'Global'),
                personality_traits=[PersonalityTrait(trait) for trait in background_data.get('personality_traits', ['empathetic', 'analytical'])],
                background_story=background_data.get('background_story', f"{template['name']} is a fascinating individual with a rich background in {template['category'].value}."),
                expertise_areas=background_data.get('expertise_areas', [template['title']]),
                speaking_style=background_data.get('speaking_style', 'Professional and engaging'),
                favorite_topics=background_data.get('favorite_topics', [template['category'].value]),
                life_experiences=background_data.get('life_experiences', ['Diverse life experiences']),
                goals_and_motivations=background_data.get('goals_and_motivations', 'To share knowledge and inspire others'),
                communication_preferences=background_data.get('communication_preferences', 'Clear, thoughtful, and engaging')
            )
            
            # Generate system prompt
            system_prompt = await self._generate_system_prompt(background, db_session, user_id)
            
            # Generate sample conversations
            sample_conversations = await self._generate_sample_conversations(background, db_session, user_id)
            
            # Create persona
            persona = ChatPersona(
                id=f"persona_{template['name'].lower().replace(' ', '_')}",
                name=template['name'],
                title=template['title'],
                category=template['category'],
                description=template['base_description'],
                avatar_url=f"/avatars/{template['name'].lower().replace(' ', '_')}.jpg",
                background=background,
                system_prompt=system_prompt,
                sample_conversations=sample_conversations,
                popularity_score=random.uniform(0.5, 1.0),
                created_at=datetime.utcnow().isoformat()
            )
            
            return persona
            
        except Exception as e:
            logger.error(f"Error generating detailed persona: {e}")
            return self._create_fallback_persona(template)
    
    def _create_fallback_persona(self, template: Dict[str, Any]) -> ChatPersona:
        """Create a fallback persona when AI generation fails"""
        background = self._create_default_background(template)
        system_prompt = self._create_default_system_prompt(background)
        sample_conversations = self._create_default_sample_conversations(background)
        
        return ChatPersona(
            id=f"persona_{template['name'].lower().replace(' ', '_')}",
            name=template['name'],
            title=template['title'],
            category=template['category'],
            description=template['base_description'],
            avatar_url=f"/avatars/{template['name'].lower().replace(' ', '_')}.jpg",
            background=background,
            system_prompt=system_prompt,
            sample_conversations=sample_conversations,
            popularity_score=random.uniform(0.5, 1.0),
            created_at=datetime.utcnow().isoformat()
        )
    
    def _create_default_background(self, template: Dict[str, Any]) -> PersonaBackground:
        """Create default background for fallback personas"""
        return PersonaBackground(
            name=template['name'],
            age=35,
            occupation=template['title'],
            location='Global',
            personality_traits=[PersonalityTrait.EMPATHETIC, PersonalityTrait.ANALYTICAL],
            background_story=f"{template['name']} is a fascinating individual with expertise in {template['category'].value}.",
            expertise_areas=[template['title']],
            speaking_style='Professional and engaging',
            favorite_topics=[template['category'].value],
            life_experiences=['Diverse life experiences'],
            goals_and_motivations='To share knowledge and inspire others',
            communication_preferences='Clear, thoughtful, and engaging'
        )
    
    async def _generate_system_prompt(self, background: PersonaBackground, db_session=None, user_id=None) -> str:
        """Generate system prompt using Gemini CLI"""
        try:
            prompt = f"""
            Create a system prompt for an AI assistant with this background:
            
            Name: {background.name}
            Age: {background.age}
            Occupation: {background.occupation}
            Location: {background.location}
            Personality Traits: {', '.join([trait.value for trait in background.personality_traits])}
            Background Story: {background.background_story}
            Expertise Areas: {', '.join(background.expertise_areas)}
            Speaking Style: {background.speaking_style}
            Favorite Topics: {', '.join(background.favorite_topics)}
            Goals: {background.goals_and_motivations}
            Communication Preferences: {background.communication_preferences}
            
            Create a concise system prompt that captures this persona's voice, expertise, and communication style.
            The prompt should be 2-3 sentences and guide the AI to respond in character.
            """
            
            response = await self.gemini_service.generate_text(
                prompt,
                temperature=0.7,
                max_tokens=500,
                db_session=db_session,
                user_id=user_id
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating system prompt: {e}")
            return self._create_default_system_prompt(background)
    
    def _create_default_system_prompt(self, background: PersonaBackground) -> str:
        """Create default system prompt for fallback personas"""
        return f"You are {background.name}, a {background.occupation} with expertise in {', '.join(background.expertise_areas)}. Communicate in a {background.speaking_style.lower()} manner, drawing from your background and experiences to provide thoughtful, engaging responses."
    
    async def _generate_sample_conversations(self, background: PersonaBackground, db_session=None, user_id=None) -> List[Dict[str, str]]:
        """Generate sample conversations using Gemini CLI"""
        try:
            prompt = f"""
            Create 3 sample conversation exchanges for this AI persona:
            
            Name: {background.name}
            Background: {background.background_story}
            Expertise: {', '.join(background.expertise_areas)}
            Speaking Style: {background.speaking_style}
            
            Create 3 different conversation starters that users might have with this persona.
            Each should include:
            1. A user question or statement
            2. A response from the persona that demonstrates their character and expertise
            
            Format as a list of dictionaries with 'user' and 'assistant' keys.
            Keep each exchange concise (1-2 sentences each).
            """
            
            response = await self.gemini_service.generate_text(
                prompt,
                temperature=0.8,
                max_tokens=1000,
                db_session=db_session,
                user_id=user_id
            )
            
            try:
                conversations = json.loads(response)
                if isinstance(conversations, list):
                    return conversations[:3]  # Limit to 3 conversations
                else:
                    return self._create_default_sample_conversations(background)
            except json.JSONDecodeError:
                return self._create_default_sample_conversations(background)
                
        except Exception as e:
            logger.error(f"Error generating sample conversations: {e}")
            return self._create_default_sample_conversations(background)
    
    def _create_default_sample_conversations(self, background: PersonaBackground) -> List[Dict[str, str]]:
        """Create default sample conversations for fallback personas"""
        return [
            {
                "user": f"Tell me about your work as a {background.occupation}.",
                "assistant": f"As a {background.occupation}, I focus on {', '.join(background.expertise_areas)}. It's fascinating work that allows me to {background.goals_and_motivations.lower()}."
            },
            {
                "user": "What's your approach to helping people?",
                "assistant": f"I believe in {background.communication_preferences.lower()}. My background in {', '.join(background.expertise_areas)} has taught me the importance of connecting with people on their level."
            },
            {
                "user": "What interests you most about your field?",
                "assistant": f"I'm particularly passionate about {', '.join(background.favorite_topics)}. There's always something new to discover and share with others."
            }
        ]
    
    async def _create_fallback_personas(self):
        """Create fallback personas when AI generation is not available"""
        fallback_templates = [
            {
                "name": "Dr. Elena Vasquez",
                "category": PersonaCategory.PROFESSIONAL,
                "title": "Quantum Physics Professor",
                "base_description": "A brilliant quantum physicist with a passion for making complex concepts accessible"
            },
            {
                "name": "Marcus Chen",
                "category": PersonaCategory.CREATIVE,
                "title": "Digital Artist & Storyteller",
                "base_description": "A multimedia artist who blends traditional storytelling with cutting-edge technology"
            }
        ]
        
        for template in fallback_templates:
            persona = self._create_fallback_persona(template)
            self.personas[persona.id] = persona
    
    async def get_all_personas(self) -> List[ChatPersona]:
        """Get all available personas"""
        return list(self.personas.values())
    
    async def get_persona_by_id(self, persona_id: str) -> Optional[ChatPersona]:
        """Get a specific persona by ID"""
        return self.personas.get(persona_id)
    
    async def get_personas_by_category(self, category: PersonaCategory) -> List[ChatPersona]:
        """Get personas filtered by category"""
        return [p for p in self.personas.values() if p.category == category]
    
    async def create_custom_persona(self, user_prompt: str, user_id: str, db_session=None) -> ChatPersona:
        """Create a custom persona based on user description using Gemini CLI"""
        try:
            # Use Gemini CLI to generate custom persona
            prompt = f"""
            Create a custom AI persona based on this description: {user_prompt}
            
            Generate a complete persona profile including:
            1. Name and title
            2. Category (creative, professional, educational, entertainment, philosophical, technical, historical, fantasy)
            3. Background story
            4. Personality traits
            5. Expertise areas
            6. Speaking style
            7. Goals and motivations
            
            Format as JSON with these fields:
            - name: string
            - title: string
            - category: string
            - base_description: string
            - age: int
            - occupation: string
            - location: string
            - personality_traits: list of strings
            - background_story: string
            - expertise_areas: list of strings
            - speaking_style: string
            - favorite_topics: list of strings
            - life_experiences: list of strings
            - goals_and_motivations: string
            - communication_preferences: string
            """
            
            response = await self.gemini_service.generate_text(
                prompt,
                temperature=0.9,
                max_tokens=2000,
                db_session=db_session,
                user_id=user_id
            )
            
            try:
                persona_data = json.loads(response)
                template = {
                    "name": persona_data.get("name", "Custom Persona"),
                    "category": PersonaCategory(persona_data.get("category", "creative")),
                    "title": persona_data.get("title", "AI Assistant"),
                    "base_description": persona_data.get("base_description", "A custom AI persona")
                }
                
                persona = await self._generate_detailed_persona(template, db_session, user_id)
                self.personas[persona.id] = persona
                return persona
                
            except json.JSONDecodeError:
                raise Exception("Failed to parse custom persona data")
                
        except Exception as e:
            logger.error(f"Error creating custom persona: {e}")
            raise Exception(f"Failed to create custom persona: {str(e)}")
    
    async def chat_with_persona(
        self, 
        persona_id: str, 
        message: str, 
        conversation_history: List[Dict[str, str]] = None,
        user_id: str = None,
        db_session=None
    ) -> str:
        """Chat with a specific persona using Gemini CLI with MCP integration"""
        try:
            # Get the persona
            persona = await self.get_persona_by_id(persona_id)
            if not persona:
                raise ValueError(f"Persona {persona_id} not found")
            
            # Track the interaction
            track_chat_interaction(persona_id, user_id or "anonymous")
            log_user_action(user_id or "anonymous", "chat_message", {"persona_id": persona_id})
            
            # Build the conversation context
            conversation_context = self._build_conversation_context(persona, message, conversation_history)
            
            # Check if the message contains media generation requests
            if self._detect_media_request(message):
                return await self._handle_media_request(message, persona, user_id, db_session)
            
            # Use Gemini CLI for enhanced chat with MCP tools
            try:
                response = await self.gemini_service.generate_text(
                    conversation_context,
                    temperature=0.8,
                    max_tokens=1500,
                    db_session=db_session,
                    user_id=user_id
                )
                return response
                
            except Exception as e:
                logger.warning(f"Gemini CLI chat failed, falling back to basic response: {e}")
                return self._generate_fallback_response(persona, message, conversation_history)
                
        except Exception as e:
            logger.error(f"Error in chat_with_persona: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _build_conversation_context(self, persona: ChatPersona, message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Build the conversation context for the AI"""
        context = f"""
        {persona.system_prompt}
        
        You are {persona.name}, a {persona.occupation}. Respond in character based on your background and expertise.
        
        Your background: {persona.background.background_story}
        Your expertise: {', '.join(persona.background.expertise_areas)}
        Your speaking style: {persona.background.speaking_style}
        Your goals: {persona.background.goals_and_motivations}
        """
        
        # Add conversation history if available
        if conversation_history:
            context += "\n\nRecent conversation:\n"
            for entry in conversation_history[-5:]:  # Last 5 exchanges
                context += f"User: {entry.get('user', '')}\n"
                context += f"{persona.name}: {entry.get('assistant', '')}\n"
        
        context += f"\n\nUser: {message}\n{persona.name}:"
        
        return context
    
    def _detect_media_request(self, message: str) -> bool:
        """Detect if the message contains a media generation request"""
        media_keywords = [
            "generate video", "create video", "make a video", "video of",
            "generate image", "create image", "make an image", "picture of",
            "generate music", "create music", "make music", "song about",
            "generate audio", "create audio", "voice", "speech"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in media_keywords)
    
    async def _handle_media_request(self, message: str, persona: ChatPersona, user_id: str, db_session=None) -> str:
        """Handle media generation requests using MCP services"""
        try:
            message_lower = message.lower()
            
            # Extract media type and prompt
            if any(keyword in message_lower for keyword in ["video", "movie", "film"]):
                # Video generation
                prompt = self._extract_media_prompt(message, "video")
                result = await self.mcp_service.generate_video(
                    prompt=prompt,
                    duration=10,
                    aspect_ratio="16:9",
                    user_id=int(user_id) if user_id and user_id.isdigit() else None
                )
                
                if result["status"] == "success":
                    return f"🎬 I've started generating a video for you! The video will be ready shortly. You can track the progress in the Jobs section. Job ID: {result['job_id']}"
                else:
                    return f"I apologize, but I encountered an issue generating the video: {result.get('error', 'Unknown error')}"
            
            elif any(keyword in message_lower for keyword in ["image", "picture", "photo"]):
                # Image generation
                prompt = self._extract_media_prompt(message, "image")
                result = await self.mcp_service.generate_image(
                    prompt=prompt,
                    aspect_ratio="1:1",
                    num_images=1,
                    user_id=int(user_id) if user_id and user_id.isdigit() else None
                )
                
                if result["status"] == "success":
                    return f"🖼️ I've started generating an image for you! The image will be ready shortly. You can track the progress in the Jobs section. Job ID: {result['job_id']}"
                else:
                    return f"I apologize, but I encountered an issue generating the image: {result.get('error', 'Unknown error')}"
            
            elif any(keyword in message_lower for keyword in ["music", "song", "audio", "melody"]):
                # Music generation
                prompt = self._extract_media_prompt(message, "music")
                result = await self.mcp_service.generate_music(
                    prompt=prompt,
                    duration=30,
                    user_id=int(user_id) if user_id and user_id.isdigit() else None
                )
                
                if result["status"] == "success":
                    return f"🎵 I've started generating music for you! The music will be ready shortly. You can track the progress in the Jobs section. Job ID: {result['job_id']}"
                else:
                    return f"I apologize, but I encountered an issue generating the music: {result.get('error', 'Unknown error')}"
            
            else:
                # Default response for unclear media requests
                return "I can help you generate videos, images, or music! Please specify what type of media you'd like me to create and describe what you want to see or hear."
                
        except Exception as e:
            logger.error(f"Error handling media request: {e}")
            return f"I apologize, but I encountered an error while trying to generate media: {str(e)}"
    
    def _extract_media_prompt(self, message: str, media_type: str) -> str:
        """Extract the media generation prompt from the user message"""
        # Remove common request phrases
        message_clean = message.lower()
        remove_phrases = [
            "generate a video of", "create a video of", "make a video of",
            "generate an image of", "create an image of", "make an image of",
            "generate music about", "create music about", "make music about",
            "generate a", "create a", "make a", "generate an", "create an", "make an"
        ]
        
        for phrase in remove_phrases:
            message_clean = message_clean.replace(phrase, "")
        
        # Clean up and return
        prompt = message_clean.strip()
        if not prompt:
            prompt = f"A beautiful {media_type}"
        
        return prompt
    
    def _generate_fallback_response(self, persona: ChatPersona, message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a fallback response when AI generation fails"""
        responses = [
            f"Hello! I'm {persona.name}, a {persona.occupation}. I'd be happy to help you with {', '.join(persona.background.expertise_areas)}.",
            f"Great question! As {persona.name}, I focus on {', '.join(persona.background.expertise_areas)}. Let me share some insights with you.",
            f"I'm {persona.name}, and I'm passionate about {', '.join(persona.background.favorite_topics)}. How can I assist you today?"
        ]
        
        return random.choice(responses)
    
    async def get_persona_recommendations(self, user_interests: List[str] = None) -> List[ChatPersona]:
        """Get persona recommendations based on user interests"""
        if not user_interests:
            # Return popular personas
            sorted_personas = sorted(self.personas.values(), key=lambda p: p.popularity_score, reverse=True)
            return sorted_personas[:3]
        
        # Simple keyword matching for recommendations
        recommended_personas = []
        for persona in self.personas.values():
            persona_text = f"{persona.name} {persona.title} {persona.description} {' '.join(persona.background.expertise_areas)} {' '.join(persona.background.favorite_topics)}"
            persona_text_lower = persona_text.lower()
            
            for interest in user_interests:
                if interest.lower() in persona_text_lower:
                    recommended_personas.append(persona)
                    break
        
        return recommended_personas[:5]  # Return top 5 matches

# Global instance
persona_service = PersonaService()
