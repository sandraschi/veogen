#!/usr/bin/env python3
"""
VeoGen User Manager Backend - FastAPI server for user management
Fixed to work with actual VeoGen database schema
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import DictCursor
import os
from datetime import datetime
import hashlib
import uuid
import uvicorn

app = FastAPI(title="VeoGen User Manager", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 4715,
    'database': 'veogen',
    'user': 'veogen',
    'password': 'veogen123'
}

# Pydantic models
class UserResponse(BaseModel):
    id: str
    full_name: str
    username: str
    email: str
    plan: str
    is_active: bool
    created_at: str
    last_login: Optional[str]
    video_count: int
    api_usage: int

class UserCreate(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    plan: str = "free"
    is_active: bool = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None

class UserStatusUpdate(BaseModel):
    is_active: bool

def get_db_connection():
    """Get database connection using psycopg2"""
    return psycopg2.connect(**DB_CONFIG)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/api/users", response_model=List[UserResponse])
async def get_users():
    """Get all users with corrected schema"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Get users with video counts and API usage using correct table names
        query = """
        SELECT 
            u.id,
            u.full_name,
            u.username,
            u.email,
            u.plan,
            u.is_active,
            u.created_at,
            u.last_login,
            COALESCE(COUNT(DISTINCT vg.id), 0) as video_count,
            COALESCE(COUNT(DISTINCT au.id), 0) as api_usage_count
        FROM users u
        LEFT JOIN video_generations vg ON u.id = vg.user_id
        LEFT JOIN api_usage au ON u.id = au.user_id
        GROUP BY u.id, u.full_name, u.username, u.email, u.plan, u.is_active, u.created_at, u.last_login
        ORDER BY u.created_at DESC
        """
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        result = []
        for user in users:
            result.append({
                "id": str(user['id']),
                "full_name": user['full_name'] or '',
                "username": user['username'] or '',
                "email": user['email'] or '',
                "plan": user['plan'] or 'free',
                "is_active": user['is_active'] if user['is_active'] is not None else True,
                "created_at": user['created_at'].isoformat() if user['created_at'] else '',
                "last_login": user['last_login'].isoformat() if user['last_login'] else None,
                "video_count": user['video_count'] or 0,
                "api_usage": user['api_usage_count'] or 0
            })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.post("/api/users", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Create new user with correct schema"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", 
                      (user_data.email, user_data.username))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User with this email or username already exists")
        
        # Create new user with correct field names
        user_id = str(uuid.uuid4())
        password_hash = hash_password(user_data.password)
        
        cursor.execute("""
            INSERT INTO users (id, full_name, username, email, hashed_password, plan, is_active, created_at, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            user_id,
            user_data.full_name,
            user_data.username,
            user_data.email,
            password_hash,
            user_data.plan,
            user_data.is_active,
            datetime.utcnow(),
            True  # Set as verified for manually created users
        ))
        
        new_user = cursor.fetchone()
        conn.commit()
        
        return {
            "id": str(new_user['id']),
            "full_name": new_user['full_name'],
            "username": new_user['username'],
            "email": new_user['email'],
            "plan": new_user['plan'],
            "is_active": new_user['is_active'],
            "created_at": new_user['created_at'].isoformat(),
            "last_login": None,
            "video_count": 0,
            "api_usage": 0
        }
    
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate):
    """Update user with correct schema"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        existing_user = cursor.fetchone()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if user_data.full_name is not None:
            update_fields.append("full_name = %s")
            update_values.append(user_data.full_name)
        
        if user_data.username is not None:
            update_fields.append("username = %s")
            update_values.append(user_data.username)
        
        if user_data.email is not None:
            update_fields.append("email = %s")
            update_values.append(user_data.email)
        
        if user_data.password is not None:
            update_fields.append("hashed_password = %s")  # Corrected field name
            update_values.append(hash_password(user_data.password))
        
        if user_data.plan is not None:
            update_fields.append("plan = %s")
            update_values.append(user_data.plan)
        
        if user_data.is_active is not None:
            update_fields.append("is_active = %s")
            update_values.append(user_data.is_active)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Add updated_at
        update_fields.append("updated_at = %s")
        update_values.append(datetime.utcnow())
        update_values.append(user_id)
        
        cursor.execute(f"""
            UPDATE users SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
        """, update_values)
        
        updated_user = cursor.fetchone()
        conn.commit()
        
        return {
            "id": str(updated_user['id']),
            "full_name": updated_user['full_name'],
            "username": updated_user['username'],
            "email": updated_user['email'],
            "plan": updated_user['plan'],
            "is_active": updated_user['is_active'],
            "created_at": updated_user['created_at'].isoformat(),
            "last_login": updated_user['last_login'].isoformat() if updated_user['last_login'] else None,
            "video_count": 0,  # Would need separate query to get actual count
            "api_usage": 0     # Would need separate query to get actual count
        }
    
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        
        return {"message": "User deleted successfully"}
    
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.patch("/api/users/{user_id}/status")
async def toggle_user_status(user_id: str, status_data: UserStatusUpdate):
    """Toggle user status"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Update user status
        cursor.execute("""
            UPDATE users SET is_active = %s, updated_at = %s
            WHERE id = %s
            RETURNING *
        """, (status_data.is_active, datetime.utcnow(), user_id))
        
        updated_user = cursor.fetchone()
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        
        return dict(updated_user)
    
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get dashboard analytics with correct schema"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Get basic user statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(*) FILTER (WHERE is_active = true) as active_users,
                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE) as new_users_today
            FROM users
        """)
        user_stats = cursor.fetchone()
        
        # Get video and API stats with correct table names
        cursor.execute("SELECT COUNT(*) FROM video_generations")
        total_videos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM api_usage")
        total_api_calls = cursor.fetchone()[0]
        
        return {
            "total_users": user_stats['total_users'],
            "active_users": user_stats['active_users'],
            "new_users_today": user_stats['new_users_today'],
            "total_videos": total_videos,
            "total_api_calls": total_api_calls
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    print("Starting VeoGen User Manager...")
    print("Frontend: http://localhost:8101")
    print("API Docs: http://localhost:8101/docs")
    uvicorn.run(app, host="0.0.0.0", port=8101)
