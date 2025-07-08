"""
Persona Chat API endpoints for real-time chat with AI personas
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from app.database import get_db, get_user_setting, set_user_setting
from app.models.user import User
from app.services.simple_persona_service import simple_persona_service
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class StartChatRequest(BaseModel):
    persona_id: str
    initial_message: str
    context: Optional[Dict[str, Any]] = None

class SendMessageRequest(BaseModel):
    message: str
    message_type: Optional[str] = "text"

class ChatResponse(BaseModel):
    conversation_id: str
    persona: Dict[str, Any]
    response: Dict[str, Any]
    status: str

class MessageResponse(BaseModel):
    conversation_id: str
    response: Dict[str, Any]
    status: str

class ConversationHistory(BaseModel):
    conversation_id: str
    persona: Dict[str, Any]
    messages: List[Dict[str, Any]]
    created_at: str
    last_activity: str
    message_count: int

class ConversationSummary(BaseModel):
    id: str
    persona: Dict[str, Any]
    last_message: str
    last_activity: str
    message_count: int

class PersonaInfo(BaseModel):
    id: str
    name: str
    description: str
    personality: str
    expertise: List[str]
    tools: List[str]

@router.get("/personas", response_model=List[PersonaInfo])
async def get_available_personas():
    """Get list of available chat personas"""
    try:
        personas = simple_persona_service.get_personas()
        return [
            PersonaInfo(
                id=p['id'],
                name=p['name'], 
                description=p['description'],
                personality="Helpful and knowledgeable",
                expertise=["General assistance"],
                tools=["Text generation"]
            )
            for p in personas
        ]
    except Exception as e:
        logger.error(f"Error getting personas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available personas"
        )

@router.post("/start", response_model=ChatResponse)
async def start_chat(
    request: StartChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new chat conversation with a persona"""
    try:
        logger.info(f"Starting chat with persona {request.persona_id} for user {current_user.email}")
        
        result = await simple_persona_service.start_conversation(
            persona_id=request.persona_id,
            initial_message=request.initial_message,
            user_id=str(current_user.id)
        )
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            persona=result["persona"],
            response=result["response"],
            status=result["status"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid chat start request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start chat conversation"
        )

@router.post("/{conversation_id}/message", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in an existing conversation"""
    try:
        logger.info(f"Sending message in conversation {conversation_id} for user {current_user.email}")
        
        result = await persona_chat_service.send_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            message=request.message,
            db_session=db,
            message_type=request.message_type
        )
        
        return MessageResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            status=result["status"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid message send request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )

@router.get("/{conversation_id}/history", response_model=ConversationHistory)
async def get_conversation_history(
    conversation_id: str,
    limit: Optional[int] = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    try:
        logger.info(f"Getting history for conversation {conversation_id} for user {current_user.email}")
        
        result = await persona_chat_service.get_conversation_history(
            conversation_id=conversation_id,
            user_id=current_user.id,
            db_session=db,
            limit=limit
        )
        
        return ConversationHistory(
            conversation_id=result["conversation_id"],
            persona=result["persona"],
            messages=result["messages"],
            created_at=result["created_at"],
            last_activity=result["last_activity"],
            message_count=result["message_count"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid conversation history request: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation history"
        )

@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all conversations for the current user"""
    try:
        logger.info(f"Listing conversations for user {current_user.email}")
        
        conversations = await persona_chat_service.list_user_conversations(
            user_id=current_user.id,
            db_session=db
        )
        
        return [
            ConversationSummary(
                id=conv["id"],
                persona=conv["persona"],
                last_message=conv["last_message"],
                last_activity=conv["last_activity"],
                message_count=conv["message_count"]
            )
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations"
        )

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    try:
        logger.info(f"Deleting conversation {conversation_id} for user {current_user.email}")
        
        # Remove from active conversations
        if conversation_id in persona_chat_service.active_conversations:
            conv = persona_chat_service.active_conversations[conversation_id]
            if conv["user_id"] == current_user.id:
                del persona_chat_service.active_conversations[conversation_id]
        
        # Remove from database
        conversations_data = get_user_setting(db, current_user.id, "chat_conversations", {})
        if conversation_id in conversations_data:
            del conversations_data[conversation_id]
            set_user_setting(db, current_user.id, "chat_conversations", conversations_data, "json")
        
        # Remove full conversation data
        conversation_key = f"chat_conversation_{conversation_id}"
        set_user_setting(db, current_user.id, conversation_key, None, "json")
        
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )

@router.get("/stats")
async def get_chat_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat statistics"""
    try:
        conversations_data = get_user_setting(db, current_user.id, "chat_conversations", {})
        
        # Calculate stats
        total_conversations = len(conversations_data)
        total_messages = sum(conv.get("message_count", 0) for conv in conversations_data.values())
        
        # Most used persona
        persona_counts = {}
        for conv in conversations_data.values():
            persona_id = conv.get("persona_id")
            if persona_id:
                persona_counts[persona_id] = persona_counts.get(persona_id, 0) + 1
        
        most_used_persona = max(persona_counts.items(), key=lambda x: x[1]) if persona_counts else None
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "most_used_persona": {
                "id": most_used_persona[0],
                "usage_count": most_used_persona[1]
            } if most_used_persona else None,
            "persona_usage": persona_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting chat stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat statistics"
        )
