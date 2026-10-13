# API Dependencies

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService

security = HTTPBearer()
auth_service = AuthService()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    import logging

    logger = logging.getLogger(__name__)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        logger.info(f"Attempting to authenticate with token: {credentials.credentials[:20]}...")

        # Verify JWT token
        payload = auth_service.verify_token(credentials.credentials)
        if payload is None:
            logger.warning("Token verification failed")
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("No user_id in token payload")
            raise credentials_exception

        logger.info(f"Token valid for user_id: {user_id}")

    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        logger.warning(f"User not found or inactive: {user_id}")
        raise credentials_exception

    logger.info(f"Successfully authenticated user: {user.email}")
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current authenticated user (optional - returns None if not authenticated)"""
    if not credentials:
        return None

    try:
        # Verify JWT token
        payload = auth_service.verify_token(credentials.credentials)
        if payload is None:
            return None

        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            return None

        return user

    except Exception:
        return None
