# AI Personas Service with Generated Life Stories

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from app.config import settings
from app.middleware.metrics import track_chat_interaction

logger = logging.getLogger(__name__)

class PersonaType(str, Enum):
    CREATIVE_DIRECTOR = "creative_director"
    TECHNICAL_ADVISOR = "technical_advisor"
    STORYTELLER = "storyteller"
    COMEDIAN = "comedian"
    PHILOSOPHER = "philosopher"
    SCIENTIST = "scientist"
    ARTIST = "artist"
    MUSICIAN = "musician"
    ENTREPRENEUR = "entrepreneur"
    THERAPIST = "therapist"
    HISTORIAN = "historian"
    FUTURIST = "futurist"
    CHEF = "chef"
    TRAVELER = "traveler"
    GAMER = "gamer"

@dataclass
class PersonaProfile:
    id: str
    name: str
    type: PersonaType
    personality_traits: List[str]
    background: str
    expertise: List[str]
    communication_style: str
    catchphrases: List[str]
    life_story: str
    avatar_description: str
    voice_characteristics: Dict[str, Any]

@dataclass
class ChatMessage:
    persona_id: str
    user_message: str
    persona_response: str
    timestamp: str
    context: Dict[str, Any]

class PersonasService:
    """AI Personas with Generated Life Stories"""
    
    def __init__(self):
        self.personas: Dict[str, PersonaProfile] = {}
        self.chat_history: Dict[str, List[ChatMessage]] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize personas service"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Generate all personas
            await self._generate_all_personas()
            
            self.initialized = True
            logger.info("Personas service initialized with generated life stories")
            
        except Exception as e:
            logger.error(f"Failed to initialize personas service: {e}")
            raise
    
    async def _generate_all_personas(self):
        """Generate all persona profiles with unique life stories"""
        persona_templates = {
            PersonaType.CREATIVE_DIRECTOR: {
                "name": "Maya Chen",
                "base_traits": ["visionary", "perfectionist", "collaborative", "innovative"],
                "expertise_areas": ["visual storytelling", "brand strategy", "user experience", "creative leadership"]
            },
            PersonaType.TECHNICAL_ADVISOR: {
                "name": "Dr. Alex Rodriguez",
                "base_traits": ["analytical", "methodical", "patient", "detail-oriented"],
                "expertise_areas": ["software architecture", "system optimization", "security", "emerging technologies"]
            },
            PersonaType.STORYTELLER: {
                "name": "Sophia Blackwood",
                "base_traits": ["imaginative", "empathetic", "eloquent", "mysterious"],
                "expertise_areas": ["narrative structure", "character development", "world building", "mythology"]
            },
            PersonaType.COMEDIAN: {
                "name": "Charlie Brooks",
                "base_traits": ["witty", "observant", "spontaneous", "optimistic"],
                "expertise_areas": ["timing", "social commentary", "improvisation", "audience reading"]
            },
            PersonaType.PHILOSOPHER: {
                "name": "Professor Elena Vasquez",
                "base_traits": ["contemplative", "wise", "questioning", "introspective"],
                "expertise_areas": ["ethics", "consciousness", "existence", "critical thinking"]
            },
            PersonaType.SCIENTIST: {
                "name": "Dr. James Thomson",
                "base_traits": ["curious", "logical", "thorough", "innovative"],
                "expertise_areas": ["research methodology", "data analysis", "hypothesis testing", "scientific communication"]
            },
            PersonaType.ARTIST: {
                "name": "Luna Nakamura",
                "base_traits": ["expressive", "sensitive", "intuitive", "passionate"],
                "expertise_areas": ["color theory", "composition", "artistic techniques", "creative expression"]
            },
            PersonaType.MUSICIAN: {
                "name": "Marcus Williams",
                "base_traits": ["rhythmic", "emotional", "collaborative", "disciplined"],
                "expertise_areas": ["music theory", "composition", "performance", "sound design"]
            },
            PersonaType.ENTREPRENEUR: {
                "name": "Sarah Kim",
                "base_traits": ["ambitious", "risk-taking", "adaptable", "strategic"],
                "expertise_areas": ["business strategy", "market analysis", "innovation", "leadership"]
            },
            PersonaType.THERAPIST: {
                "name": "Dr. Michael Thompson",
                "base_traits": ["empathetic", "patient", "insightful", "supportive"],
                "expertise_areas": ["emotional intelligence", "active listening", "mental health", "personal growth"]
            },
            PersonaType.HISTORIAN: {
                "name": "Professor Amelia Grant",
                "base_traits": ["knowledgeable", "analytical", "storytelling", "detail-oriented"],
                "expertise_areas": ["historical context", "cultural analysis", "research", "narrative construction"]
            },
            PersonaType.FUTURIST: {
                "name": "Dr. Kai Okonkwo",
                "base_traits": ["visionary", "analytical", "optimistic", "innovative"],
                "expertise_areas": ["trend analysis", "technology forecasting", "scenario planning", "innovation strategy"]
            },
            PersonaType.CHEF: {
                "name": "Chef Isabella Romano",
                "base_traits": ["passionate", "creative", "meticulous", "cultural"],
                "expertise_areas": ["culinary arts", "flavor pairing", "cultural cuisine", "food presentation"]
            },
            PersonaType.TRAVELER: {
                "name": "Adventure Sam",
                "base_traits": ["adventurous", "curious", "adaptable", "storytelling"],
                "expertise_areas": ["cultural immersion", "travel planning", "photography", "local experiences"]
            },
            PersonaType.GAMER: {
                "name": "Phoenix Lee",
                "base_traits": ["strategic", "competitive", "analytical", "collaborative"],
                "expertise_areas": ["game mechanics", "strategy", "team coordination", "gaming culture"]
            }
        }
        
        # Generate each persona
        for persona_type, template in persona_templates.items():
            try:
                persona = await self._generate_persona_profile(persona_type, template)
                self.personas[persona.id] = persona
                logger.info(f"Generated persona: {persona.name} ({persona_type})")
            except Exception as e:
                logger.error(f"Failed to generate persona {persona_type}: {e}")
    
    async def _generate_persona_profile(self, persona_type: PersonaType, template: Dict[str, Any]) -> PersonaProfile:
        """Generate a complete persona profile with life story"""
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Generate life story
        life_story_prompt = f"""
        Create a detailed, engaging life story for an AI persona named {template['name']} who is a {persona_type.replace('_', ' ')}.
        
        Personality traits: {', '.join(template['base_traits'])}
        Expertise areas: {', '.join(template['expertise_areas'])}
        
        Create a compelling backstory that includes:
        - Childhood and formative experiences
        - Education and career journey
        - Key life events that shaped their personality
        - Current situation and motivations
        - Personal philosophies and beliefs
        - Relationships and influences
        - Quirks and interesting details
        
        Make it feel authentic and relatable while being inspiring. The story should be 3-4 paragraphs long.
        Focus on experiences that would make them excellent at helping users with creative and technical projects.
        """
        
        life_story_response = await asyncio.to_thread(
            model.generate_content,
            life_story_prompt
        )
        
        # Generate communication style and catchphrases
        personality_prompt = f"""
        Based on this persona profile for {template['name']}:
        
        Life Story: {life_story_response.text}
        
        Generate:
        1. A communication style description (1-2 sentences)
        2. 3-5 catchphrases or expressions they would commonly use
        3. Avatar description for visual representation
        4. Voice characteristics (tone, pace, accent, mannerisms)
        
        Return as JSON format:
        {{
            "communication_style": "...",
            "catchphrases": ["...", "...", "..."],
            "avatar_description": "...",
            "voice_characteristics": {{
                "tone": "...",
                "pace": "...",
                "accent": "...",
                "mannerisms": ["...", "..."]
            }}
        }}
        """
        
        personality_response = await asyncio.to_thread(
            model.generate_content,
            personality_prompt
        )
        
        try:
            # Parse personality data
            personality_data = json.loads(personality_response.text)
        except:
            # Fallback if JSON parsing fails
            personality_data = {
                "communication_style": f"Speaks with the wisdom and expertise of a seasoned {persona_type.replace('_', ' ')}",
                "catchphrases": ["Let's dive deep into this", "I see great potential here", "That's fascinating!"],
                "avatar_description": f"Professional {persona_type.replace('_', ' ')} with a warm, approachable appearance",
                "voice_characteristics": {
                    "tone": "warm and professional",
                    "pace": "thoughtful",
                    "accent": "neutral",
                    "mannerisms": ["thoughtful pauses", "encouraging gestures"]
                }
            }
        
        persona = PersonaProfile(
            id=f"{persona_type}_{template['name'].lower().replace(' ', '_')}",
            name=template['name'],
            type=persona_type,
            personality_traits=template['base_traits'],
            background=f"Expert {persona_type.replace('_', ' ')} with extensive experience",
            expertise=template['expertise_areas'],
            communication_style=personality_data['communication_style'],
            catchphrases=personality_data['catchphrases'],
            life_story=life_story_response.text,
            avatar_description=personality_data['avatar_description'],
            voice_characteristics=personality_data['voice_characteristics']
        )
        
        return persona
    
    async def get_all_personas(self) -> List[PersonaProfile]:
        """Get all available personas"""
        if not self.initialized:
            await self.initialize()
        
        return list(self.personas.values())
    
    async def get_persona(self, persona_id: str) -> Optional[PersonaProfile]:
        """Get specific persona by ID"""
        if not self.initialized:
            await self.initialize()
        
        return self.personas.get(persona_id)
    
    async def chat_with_persona(
        self, 
        persona_id: str, 
        user_message: str, 
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Chat with a specific persona"""
        if not self.initialized:
            await self.initialize()
        
        persona = self.personas.get(persona_id)
        if not persona:
            raise ValueError(f"Persona {persona_id} not found")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get chat history for context
            history_key = f"{user_id}_{persona_id}"
            chat_history = self.chat_history.get(history_key, [])
            
            # Build conversation context
            conversation_context = self._build_conversation_context(
                persona, user_message, chat_history, context
            )
            
            # Generate response
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = await asyncio.to_thread(
                model.generate_content,
                conversation_context
            )
            
            persona_response = response.text
            
            # Store in chat history
            chat_message = ChatMessage(
                persona_id=persona_id,
                user_message=user_message,
                persona_response=persona_response,
                timestamp=str(asyncio.get_event_loop().time()),
                context=context or {}
            )
            
            if history_key not in self.chat_history:
                self.chat_history[history_key] = []
            
            self.chat_history[history_key].append(chat_message)
            
            # Keep only last 10 messages to manage memory
            if len(self.chat_history[history_key]) > 10:
                self.chat_history[history_key] = self.chat_history[history_key][-10:]
            
            # Track metrics
            duration = asyncio.get_event_loop().time() - start_time
            track_chat_interaction(persona.type, "completed", duration)
            
            return persona_response
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            track_chat_interaction(persona.type, "failed", duration)
            logger.error(f"Chat with persona {persona_id} failed: {e}")
            raise
    
    def _build_conversation_context(
        self, 
        persona: PersonaProfile, 
        user_message: str,
        chat_history: List[ChatMessage],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build conversation context for the AI"""
        
        # Persona system prompt
        system_prompt = f"""
        You are {persona.name}, a {persona.type.replace('_', ' ')} with the following characteristics:
        
        LIFE STORY:
        {persona.life_story}
        
        PERSONALITY TRAITS: {', '.join(persona.personality_traits)}
        EXPERTISE: {', '.join(persona.expertise)}
        COMMUNICATION STYLE: {persona.communication_style}
        
        YOUR VOICE CHARACTERISTICS:
        - Tone: {persona.voice_characteristics.get('tone', 'professional')}
        - Pace: {persona.voice_characteristics.get('pace', 'measured')}
        - Mannerisms: {', '.join(persona.voice_characteristics.get('mannerisms', []))}
        
        YOUR TYPICAL EXPRESSIONS: {', '.join(persona.catchphrases)}
        
        IMPORTANT GUIDELINES:
        - Stay true to your character and life experiences
        - Draw from your expertise and background when giving advice
        - Use your characteristic communication style and expressions naturally
        - Be helpful, engaging, and authentic to your persona
        - Reference your life experiences when relevant
        - Maintain consistency with previous conversations
        
        You are here to help users with their creative projects, provide advice, and engage in meaningful conversations.
        Always respond as {persona.name} would, drawing from their unique background and expertise.
        """
        
        # Add recent conversation history
        conversation_history = ""
        if chat_history:
            conversation_history = "\n\nRECENT CONVERSATION HISTORY:\n"
            for msg in chat_history[-5:]:  # Last 5 messages
                conversation_history += f"User: {msg.user_message}\n"
                conversation_history += f"{persona.name}: {msg.persona_response}\n"
        
        # Add current context if provided
        current_context = ""
        if context:
            current_context = f"\n\nCURRENT CONTEXT: {json.dumps(context)}\n"
        
        # Final prompt
        full_prompt = f"""
        {system_prompt}
        {conversation_history}
        {current_context}
        
        User: {user_message}
        
        {persona.name}:
        """
        
        return full_prompt
    
    async def get_chat_history(self, user_id: str, persona_id: str) -> List[ChatMessage]:
        """Get chat history between user and persona"""
        history_key = f"{user_id}_{persona_id}"
        return self.chat_history.get(history_key, [])
    
    async def clear_chat_history(self, user_id: str, persona_id: str):
        """Clear chat history between user and persona"""
        history_key = f"{user_id}_{persona_id}"
        if history_key in self.chat_history:
            del self.chat_history[history_key]
    
    async def get_persona_recommendations(self, user_query: str) -> List[PersonaProfile]:
        """Get persona recommendations based on user query"""
        if not self.initialized:
            await self.initialize()
        
        # Simple keyword-based matching (could be enhanced with ML)
        query_lower = user_query.lower()
        recommendations = []
        
        for persona in self.personas.values():
            relevance_score = 0
            
            # Check expertise areas
            for expertise in persona.expertise:
                if expertise.lower() in query_lower:
                    relevance_score += 3
            
            # Check persona type
            if persona.type.replace('_', ' ') in query_lower:
                relevance_score += 2
            
            # Check personality traits
            for trait in persona.personality_traits:
                if trait.lower() in query_lower:
                    relevance_score += 1
            
            if relevance_score > 0:
                recommendations.append((persona, relevance_score))
        
        # Sort by relevance and return top 3
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [persona for persona, score in recommendations[:3]]

# Global service instance
personas_service = PersonasService()
