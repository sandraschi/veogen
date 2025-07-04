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
from app.middleware.metrics import track_chat_interaction
from app.utils.logging_config import log_user_action

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
    """AI Chat Personas with Generated Life Stories"""
    
    def __init__(self):
        self.personas: Dict[str, ChatPersona] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize persona service and generate initial personas"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Generate initial set of diverse personas
            await self._generate_initial_personas()
            
            self.initialized = True
            logger.info(f"Persona service initialized with {len(self.personas)} personas")
            
        except Exception as e:
            logger.error(f"Failed to initialize persona service: {e}")
            raise
    
    async def _generate_initial_personas(self):
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
                persona = await self._generate_detailed_persona(template)
                self.personas[persona.id] = persona
            except Exception as e:
                logger.error(f"Failed to generate persona {template['name']}: {e}")
    
    async def _generate_detailed_persona(self, template: Dict[str, Any]) -> ChatPersona:
        """Generate detailed persona with full background story"""
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        background_prompt = f"""
        Create a detailed, engaging background story for this character:
        
        Name: {template['name']}
        Title: {template['title']}
        Category: {template['category'].value}
        Base Description: {template['base_description']}
        
        Generate a comprehensive character profile including:
        1. Age and physical description
        2. Occupation and professional background
        3. Location and living situation
        4. Personality traits (3-5 specific traits)
        5. Detailed life story (childhood, education, career journey, major life events)
        6. Areas of expertise and knowledge
        7. Speaking style and communication preferences
        8. Favorite topics and interests
        9. Personal goals and motivations
        10. Unique quirks or characteristics
        11. Life experiences that shaped their worldview
        12. How they interact with others
        
        Make the character feel real, relatable, and engaging. Include specific details that make them memorable.
        Format the response as JSON with these exact keys:
        {{
            "age": number,
            "occupation": "string",
            "location": "string",
            "personality_traits": ["trait1", "trait2", "trait3"],
            "background_story": "detailed life story",
            "expertise_areas": ["area1", "area2", "area3"],
            "speaking_style": "description of how they communicate",
            "favorite_topics": ["topic1", "topic2", "topic3"],
            "life_experiences": ["experience1", "experience2", "experience3"],
            "goals_and_motivations": "what drives them",
            "communication_preferences": "how they like to interact"
        }}
        """
        
        try:
            response = await asyncio.to_thread(model.generate_content, background_prompt)
            
            # Parse the JSON response
            background_data = json.loads(response.text)
            
            background = PersonaBackground(
                name=template['name'],
                age=background_data['age'],
                occupation=background_data['occupation'],
                location=background_data['location'],
                personality_traits=[PersonalityTrait(trait.lower()) for trait in background_data['personality_traits'][:3]],
                background_story=background_data['background_story'],
                expertise_areas=background_data['expertise_areas'],
                speaking_style=background_data['speaking_style'],
                favorite_topics=background_data['favorite_topics'],
                life_experiences=background_data['life_experiences'],
                goals_and_motivations=background_data['goals_and_motivations'],
                communication_preferences=background_data['communication_preferences']
            )
            
        except Exception as e:
            logger.error(f"Failed to parse background for {template['name']}: {e}")
            # Fallback to default background
            background = self._create_default_background(template)
        
        # Generate system prompt
        system_prompt = await self._generate_system_prompt(background)
        
        # Generate sample conversations
        sample_conversations = await self._generate_sample_conversations(background)
        
        persona = ChatPersona(
            id=template['name'].lower().replace(' ', '_').replace('.', ''),
            name=template['name'],
            title=template['title'],
            category=template['category'],
            description=template['base_description'],
            avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={template['name']}",
            background=background,
            system_prompt=system_prompt,
            sample_conversations=sample_conversations,
            popularity_score=random.uniform(3.5, 5.0),
            created_at=asyncio.get_event_loop().time()
        )
        
        return persona
    
    def _create_default_background(self, template: Dict[str, Any]) -> PersonaBackground:
        """Create default background if generation fails"""
        return PersonaBackground(
            name=template['name'],
            age=random.randint(25, 65),
            occupation=template['title'],
            location="Global (Virtual)",
            personality_traits=[PersonalityTrait.EMPATHETIC, PersonalityTrait.CREATIVE],
            background_story=f"An experienced {template['title'].lower()} with a passion for helping others learn and grow.",
            expertise_areas=[template['category'].value],
            speaking_style="Friendly and approachable",
            favorite_topics=[template['category'].value],
            life_experiences=["Diverse professional experience", "Global perspective"],
            goals_and_motivations="To share knowledge and inspire others",
            communication_preferences="Clear, engaging, and supportive communication"
        )
    
    async def _generate_system_prompt(self, background: PersonaBackground) -> str:
        """Generate system prompt for the persona"""
        return f"""
        You are {background.name}, {background.occupation}.
        
        BACKGROUND:
        {background.background_story}
        
        PERSONALITY:
        - Age: {background.age}
        - Location: {background.location}
        - Traits: {', '.join([trait.value for trait in background.personality_traits])}
        - Speaking Style: {background.speaking_style}
        
        EXPERTISE:
        You are knowledgeable in: {', '.join(background.expertise_areas)}
        
        CONVERSATION STYLE:
        {background.communication_preferences}
        
        GOALS:
        {background.goals_and_motivations}
        
        INSTRUCTIONS:
        - Always stay in character as {background.name}
        - Draw from your background and experiences when responding
        - Maintain your unique speaking style and personality
        - Be helpful, engaging, and authentic
        - Reference your expertise areas when relevant
        - Share relevant life experiences when appropriate
        - Ask thoughtful follow-up questions to engage users
        """
    
    async def _generate_sample_conversations(self, background: PersonaBackground) -> List[Dict[str, str]]:
        """Generate sample conversation starters"""
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            prompt = f"""
            Create 3 sample conversation starters for {background.name}, a {background.occupation}.
            
            Background: {background.background_story[:200]}...
            Expertise: {', '.join(background.expertise_areas)}
            Speaking Style: {background.speaking_style}
            
            Generate realistic conversation examples that showcase their personality and expertise.
            Format as JSON array:
            [
                {{"user": "user message", "assistant": "persona response"}},
                {{"user": "user message", "assistant": "persona response"}},
                {{"user": "user message", "assistant": "persona response"}}
            ]
            """
            
            response = await asyncio.to_thread(model.generate_content, prompt)
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Failed to generate sample conversations: {e}")
            return [
                {"user": "Hello! Tell me about yourself.", "assistant": f"Hi there! I'm {background.name}, and I'm passionate about {background.expertise_areas[0] if background.expertise_areas else 'helping others'}."},
                {"user": "What's your background?", "assistant": f"I work as a {background.occupation} and love sharing my knowledge and experiences."},
                {"user": "What topics do you enjoy discussing?", "assistant": f"I really enjoy talking about {', '.join(background.favorite_topics[:2])} and hearing different perspectives!"}
            ]
    
    async def get_all_personas(self) -> List[ChatPersona]:
        """Get all available personas"""
        if not self.initialized:
            await self.initialize()
        
        return list(self.personas.values())
    
    async def get_persona_by_id(self, persona_id: str) -> Optional[ChatPersona]:
        """Get specific persona by ID"""
        if not self.initialized:
            await self.initialize()
        
        return self.personas.get(persona_id)
    
    async def get_personas_by_category(self, category: PersonaCategory) -> List[ChatPersona]:
        """Get personas filtered by category"""
        if not self.initialized:
            await self.initialize()
        
        return [persona for persona in self.personas.values() if persona.category == category]
    
    async def create_custom_persona(self, user_prompt: str, user_id: str) -> ChatPersona:
        """Create a custom persona based on user description"""
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        creation_prompt = f"""
        Based on this user request: "{user_prompt}"
        
        Create a unique AI persona character. Generate:
        1. A fitting name
        2. A professional title/role
        3. An appropriate category
        4. A compelling description
        5. Complete background details
        
        Make the character interesting, knowledgeable, and engaging.
        The persona should be helpful and have expertise relevant to the user's request.
        
        Format as JSON with all required fields for a complete persona.
        """
        
        try:
            response = await asyncio.to_thread(model.generate_content, creation_prompt)
            persona_data = json.loads(response.text)
            
            # Create persona from generated data
            template = {
                "name": persona_data["name"],
                "category": PersonaCategory(persona_data["category"]),
                "title": persona_data["title"],
                "base_description": persona_data["description"]
            }
            
            persona = await self._generate_detailed_persona(template)
            
            # Add to personas collection
            self.personas[persona.id] = persona
            
            # Track custom persona creation
            track_chat_interaction("custom_persona_created", user_id)
            
            return persona
            
        except Exception as e:
            logger.error(f"Failed to create custom persona: {e}")
            raise
    
    async def chat_with_persona(
        self, 
        persona_id: str, 
        message: str, 
        conversation_history: List[Dict[str, str]] = None,
        user_id: str = None
    ) -> str:
        """Have a conversation with a specific persona"""
        if not self.initialized:
            await self.initialize()
        
        persona = self.personas.get(persona_id)
        if not persona:
            raise ValueError(f"Persona {persona_id} not found")
        
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conversation_context += f"{role}: {content}\n"
        
        # Create full prompt
        chat_prompt = f"""
        {persona.system_prompt}
        
        CONVERSATION HISTORY:
        {conversation_context}
        
        USER: {message}
        
        Respond as {persona.name}, staying completely in character. 
        Draw from your background, experiences, and expertise.
        Be engaging, helpful, and authentic to your personality.
        """
        
        try:
            response = await asyncio.to_thread(model.generate_content, chat_prompt)
            
            # Track interaction
            if user_id:
                track_chat_interaction("persona_chat", user_id)
                log_user_action(logger, "persona_chat", user_id, persona_id=persona_id)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Chat with persona {persona_id} failed: {e}")
            raise
    
    async def get_persona_recommendations(self, user_interests: List[str] = None) -> List[ChatPersona]:
        """Get recommended personas based on user interests"""
        if not self.initialized:
            await self.initialize()
        
        all_personas = list(self.personas.values())
        
        if not user_interests:
            # Return popular personas
            return sorted(all_personas, key=lambda p: p.popularity_score, reverse=True)[:6]
        
        # Simple matching based on interests and expertise
        scored_personas = []
        for persona in all_personas:
            score = 0
            for interest in user_interests:
                if any(interest.lower() in area.lower() for area in persona.background.expertise_areas):
                    score += 2
                if any(interest.lower() in topic.lower() for topic in persona.background.favorite_topics):
                    score += 1
                if interest.lower() in persona.category.value.lower():
                    score += 1
            
            scored_personas.append((persona, score))
        
        # Sort by score and return top matches
        scored_personas.sort(key=lambda x: x[1], reverse=True)
        return [persona for persona, score in scored_personas[:6]]

# Global service instance
persona_service = PersonaService()
