import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.database import APIKey, User


class APIKeyService:
    def __init__(self):
        self.salt_length = 32
        self.hash_algorithm = "sha256"
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key for secure storage"""
        # For now, using a simple encryption. In production, use proper encryption
        # This is a placeholder - replace with proper encryption library
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def store_api_key(
        self, 
        db: Session, 
        user_id: str, 
        service_name: str, 
        key_name: str, 
        api_key: str
    ) -> APIKey:
        """Store a new API key for a user"""
        # Check if key name already exists for this user and service
        existing_key = db.query(APIKey).filter(
            and_(
                APIKey.user_id == user_id,
                APIKey.service_name == service_name,
                APIKey.key_name == key_name
            )
        ).first()
        
        if existing_key:
            raise ValueError(f"API key with name '{key_name}' already exists for service '{service_name}'")
        
        # Encrypt the API key
        encrypted_key = self._encrypt_api_key(api_key)
        
        # Create new API key record
        db_api_key = APIKey(
            user_id=user_id,
            service_name=service_name,
            key_name=key_name,
            encrypted_key=encrypted_key,
            is_active=True,
            created_at=datetime.utcnow(),
            last_used=None,
            usage_count=0
        )
        
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        
        return db_api_key
    
    def list_api_keys(self, db: Session, user_id: str) -> List[APIKey]:
        """List all API keys for a user"""
        return db.query(APIKey).filter(APIKey.user_id == user_id).all()
    
    def get_service_keys(self, db: Session, user_id: str, service_name: str) -> List[APIKey]:
        """Get all API keys for a specific service and user"""
        return db.query(APIKey).filter(
            and_(
                APIKey.user_id == user_id,
                APIKey.service_name == service_name
            )
        ).all()
    
    def get_api_key_by_id(self, db: Session, user_id: str, key_id: int) -> Optional[APIKey]:
        """Get a specific API key by ID for a user"""
        return db.query(APIKey).filter(
            and_(
                APIKey.id == key_id,
                APIKey.user_id == user_id
            )
        ).first()
    
    def update_api_key(
        self, 
        db: Session, 
        user_id: str, 
        key_id: int, 
        service_name: str, 
        key_name: str, 
        api_key: str
    ) -> bool:
        """Update an existing API key"""
        db_api_key = self.get_api_key_by_id(db, user_id, key_id)
        if not db_api_key:
            return False
        
        # Check if new key name conflicts with existing keys
        existing_key = db.query(APIKey).filter(
            and_(
                APIKey.user_id == user_id,
                APIKey.service_name == service_name,
                APIKey.key_name == key_name,
                APIKey.id != key_id
            )
        ).first()
        
        if existing_key:
            raise ValueError(f"API key with name '{key_name}' already exists for service '{service_name}'")
        
        # Encrypt the new API key
        encrypted_key = self._encrypt_api_key(api_key)
        
        # Update the API key
        db_api_key.service_name = service_name
        db_api_key.key_name = key_name
        db_api_key.encrypted_key = encrypted_key
        
        db.commit()
        return True
    
    def delete_api_key(self, db: Session, user_id: str, key_id: int) -> bool:
        """Delete an API key"""
        db_api_key = self.get_api_key_by_id(db, user_id, key_id)
        if not db_api_key:
            return False
        
        db.delete(db_api_key)
        db.commit()
        return True
    
    def deactivate_api_key(self, db: Session, user_id: str, key_id: int) -> bool:
        """Deactivate an API key"""
        db_api_key = self.get_api_key_by_id(db, user_id, key_id)
        if not db_api_key:
            return False
        
        db_api_key.is_active = False
        db_api_key.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    def activate_api_key(self, db: Session, user_id: str, key_id: int) -> bool:
        """Activate an API key"""
        db_api_key = self.get_api_key_by_id(db, user_id, key_id)
        if not db_api_key:
            return False
        
        db_api_key.is_active = True
        db_api_key.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    def validate_api_key(self, db: Session, user_id: str, service_name: str, api_key: str) -> Optional[APIKey]:
        """Validate an API key for a user and service"""
        api_keys = self.get_service_keys(db, user_id, service_name)
        
        for db_api_key in api_keys:
            if not db_api_key.is_active:
                continue
            
            # Encrypt the provided API key
            encrypted_key = self._encrypt_api_key(api_key)
            
            # Compare with stored encrypted key
            if encrypted_key == db_api_key.encrypted_key:
                # Update usage statistics
                db_api_key.last_used = datetime.utcnow()
                db_api_key.usage_count += 1
                db.commit()
                return db_api_key
        
        return None
    
    def get_api_key_usage_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for API keys"""
        # Get total API keys
        total_keys = db.query(func.count(APIKey.id)).filter(APIKey.user_id == user_id).scalar()
        
        # Get active API keys
        active_keys = db.query(func.count(APIKey.id)).filter(
            and_(APIKey.user_id == user_id, APIKey.is_active == True)
        ).scalar()
        
        # Get total usage count
        total_usage = db.query(func.sum(APIKey.usage_count)).filter(APIKey.user_id == user_id).scalar() or 0
        
        # Get keys by service
        service_stats = db.query(
            APIKey.service_name,
            func.count(APIKey.id).label('count'),
            func.sum(APIKey.usage_count).label('usage')
        ).filter(APIKey.user_id == user_id).group_by(APIKey.service_name).all()
        
        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "total_usage": total_usage,
            "service_breakdown": [
                {
                    "service_name": stat.service_name,
                    "key_count": stat.count,
                    "usage_count": stat.usage or 0
                }
                for stat in service_stats
            ]
        }
    
    def cleanup_expired_keys(self, db: Session, days_old: int = 90) -> int:
        """Clean up API keys that haven't been used for specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        expired_keys = db.query(APIKey).filter(
            and_(
                APIKey.last_used < cutoff_date,
                APIKey.is_active == False
            )
        ).all()
        
        count = len(expired_keys)
        for key in expired_keys:
            db.delete(key)
        
        db.commit()
        return count


# Create singleton instance
api_key_service = APIKeyService() 