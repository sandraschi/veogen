# API Dependencies

from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal

# Mock User model for now
class User:
    def __init__(self, id: str = "user-1", email: str = "test@example.com"):
        self.id = id
        self.email = email

async def get_db() -> Generator[AsyncSession, None, None]:
    """Get database session"""
    # For now, return a mock session
    # In production, this would create a real database session
    yield None

async def get_current_user() -> User:
    """Get current authenticated user"""
    # For now, return a mock user
    # In production, this would validate JWT token and return real user
    return User()
