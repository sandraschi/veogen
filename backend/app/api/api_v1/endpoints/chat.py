from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db, User
from app.api.deps import get_current_user, get_current_user_optional
from app.services.chat.persona_service import persona_service
from app.services.personas.personas_service import PersonasService

router = APIRouter()

# Pydantic models for request/response
class ChatMessageRequest(BaseModel):
    message: str
    persona: str
    conversation_history: Optional[List[Dict[str, Any]]] = None

class ChatMessageResponse(BaseModel):
    response: str
    persona: str
    timestamp: str
    conversation_id: Optional[str] = None

class PersonaInfo(BaseModel):
    id: str
    name: str
    description: str
    expertise: List[str]
    personality: str
    system_prompt: str

class ConversationCreate(BaseModel):
    persona_id: str
    title: Optional[str] = None

class ConversationInfo(BaseModel):
    id: str
    persona_id: str
    title: str
    created_at: str
    last_message_at: Optional[str] = None
    message_count: int

class MessageInfo(BaseModel):
    id: str
    conversation_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    persona_id: Optional[str] = None

# Initialize services
personas_service = PersonasService()

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    message_data: ChatMessageRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Send a message to a specific persona and get a response"""
    try:
        user_id = current_user.id if current_user else "anonymous"
        
        # Use the persona service to get a response
        response = await persona_service.chat_with_persona(
            persona_id=message_data.persona,
            message=message_data.message,
            conversation_history=message_data.conversation_history,
            user_id=user_id
        )
        
        return ChatMessageResponse(
            response=response,
            persona=message_data.persona,
            timestamp=datetime.utcnow().isoformat(),
            conversation_id=None  # Will be implemented with conversation management
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/personas", response_model=List[PersonaInfo])
async def get_personas():
    """Get all available personas"""
    try:
        # Initialize persona service if not already initialized
        if not persona_service.initialized:
            await persona_service.initialize()
        
        personas = []
        for persona_id, persona in persona_service.personas.items():
            personas.append(PersonaInfo(
                id=persona_id,
                name=persona.name,
                description=persona.description,
                expertise=persona.background.expertise_areas,
                personality=persona.background.personality_traits[0] if persona.background.personality_traits else "Friendly",
                system_prompt=persona.system_prompt
            ))
        return personas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve personas"
        )

@router.get("/personas/{persona_id}", response_model=PersonaInfo)
async def get_persona(persona_id: str):
    """Get a specific persona by ID"""
    try:
        # Initialize persona service if not already initialized
        if not persona_service.initialized:
            await persona_service.initialize()
        
        persona = persona_service.personas.get(persona_id)
        if not persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona not found"
            )
        
        return PersonaInfo(
            id=persona_id,
            name=persona.name,
            description=persona.description,
            expertise=persona.background.expertise_areas,
            personality=persona.background.personality_traits[0] if persona.background.personality_traits else "Friendly",
            system_prompt=persona.system_prompt
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve persona"
        )

@router.post("/conversations", response_model=ConversationInfo)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Create a new conversation with a persona"""
    try:
        # For now, return a mock conversation
        # TODO: Implement actual conversation storage in database
        conversation_id = f"conv_{datetime.utcnow().timestamp()}"
        
        return ConversationInfo(
            id=conversation_id,
            persona_id=conversation_data.persona_id,
            title=conversation_data.title or f"Chat with {conversation_data.persona_id}",
            created_at=datetime.utcnow().isoformat(),
            last_message_at=None,
            message_count=0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

@router.get("/conversations", response_model=List[ConversationInfo])
async def get_conversations(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user"""
    try:
        # For now, return empty list
        # TODO: Implement actual conversation retrieval from database
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageInfo])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation"""
    try:
        # For now, return empty list
        # TODO: Implement actual message retrieval from database
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation messages"
        )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    try:
        # TODO: Implement actual conversation deletion from database
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )

@router.patch("/conversations/{conversation_id}")
async def update_conversation_title(
    conversation_id: str,
    title_data: Dict[str, str],
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    try:
        # TODO: Implement actual conversation title update in database
        return {"message": "Conversation title updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation title"
        )

@router.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = "json",
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Export conversation in specified format"""
    try:
        # TODO: Implement actual conversation export
        if format == "json":
            return {"conversation_id": conversation_id, "messages": []}
        elif format == "txt":
            return "Conversation export not yet implemented"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported export format"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export conversation"
        )

@router.post("/conversations/{conversation_id}/messages/{message_id}/regenerate")
async def regenerate_response(
    conversation_id: str,
    message_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Regenerate a specific message response"""
    try:
        # TODO: Implement actual message regeneration
        return {"message": "Message regeneration not yet implemented"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate message"
        ) 