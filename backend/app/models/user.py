# User Model

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True
    plan: str = "free"  # free, pro, studio
    
    class Config:
        from_attributes = True
