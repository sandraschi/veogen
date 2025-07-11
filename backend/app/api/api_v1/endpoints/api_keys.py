from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter()

# For now, we'll use a simple in-memory structure until we create the database model
# This allows the frontend to work immediately while we implement proper persistence

class APIKeyCreate(BaseModel):
    service_name: str
    key_name: str
    api_key: str

class APIKeyUpdate(BaseModel):
    service_name: Optional[str] = None
    key_name: Optional[str] = None
    api_key: Optional[str] = None

class APIKeyResponse(BaseModel):
    id: str
    service_name: str
    key_name: str
    api_key: str  # In production, this should be masked
    status: str
    created_at: str
    last_used: Optional[str] = None

    class Config:
        from_attributes = True

# Temporary in-memory storage (replace with database later)
_api_keys_storage = {}

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's API keys"""
    try:
        user_keys = _api_keys_storage.get(str(current_user.id), [])
        return user_keys
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve API keys: {str(e)}"
        )

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    try:
        # Create new API key
        new_key = APIKeyResponse(
            id=str(uuid.uuid4()),
            service_name=key_data.service_name,
            key_name=key_data.key_name,
            api_key=key_data.api_key,  # In production, encrypt this
            status="active",
            created_at=datetime.utcnow().isoformat(),
            last_used=None
        )
        
        # Store in temporary storage
        user_id = str(current_user.id)
        if user_id not in _api_keys_storage:
            _api_keys_storage[user_id] = []
        
        _api_keys_storage[user_id].append(new_key)
        
        return new_key
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )

@router.put("/api-keys/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str,
    key_data: APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing API key"""
    try:
        user_id = str(current_user.id)
        user_keys = _api_keys_storage.get(user_id, [])
        
        # Find the key to update
        key_to_update = None
        key_index = None
        for i, key in enumerate(user_keys):
            if key.id == key_id:
                key_to_update = key
                key_index = i
                break
        
        if not key_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Update fields
        if key_data.service_name is not None:
            key_to_update.service_name = key_data.service_name
        if key_data.key_name is not None:
            key_to_update.key_name = key_data.key_name
        if key_data.api_key is not None:
            key_to_update.api_key = key_data.api_key
            
        # Update in storage
        _api_keys_storage[user_id][key_index] = key_to_update
        
        return key_to_update
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update API key: {str(e)}"
        )

@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    try:
        user_id = str(current_user.id)
        user_keys = _api_keys_storage.get(user_id, [])
        
        # Find and remove the key
        original_count = len(user_keys)
        _api_keys_storage[user_id] = [key for key in user_keys if key.id != key_id]
        
        if len(_api_keys_storage[user_id]) == original_count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        return {"message": "API key deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete API key: {str(e)}"
        )
