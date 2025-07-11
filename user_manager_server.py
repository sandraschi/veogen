#!/usr/bin/env python3
"""
VeoGen User Manager Tool - Backend Server (UUID Fixed)
A beautiful, standalone user management tool for VeoGen's PostgreSQL database.
"""

import os
import sys
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uvicorn
from datetime import datetime
import uuid
import hashlib

# Pydantic models - FIXED for UUID support
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    is_active: bool = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str  # UUID string, not integer
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    video_count: int = 0
    api_usage: int = 0
    last_login: Optional[datetime] = None

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 4715,
    'database': 'veogen',
    'user': 'veogen',
    'password': 'veogen123'
}

# FastAPI app
app = FastAPI(
    title="VeoGen User Manager",
    description="Standalone user management tool for VeoGen platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Get database connection with error handling."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# API Routes
@app.get("/api/users", response_model=List[UserResponse])
async def get_all_users():
    """Get all users with their statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get users with basic stats - ID is now treated as string (UUID)
        query = """
        SELECT 
            u.id::text, u.email, u.username, u.full_name, u.is_active, u.created_at,
            COALESCE(v.video_count, 0) as video_count,
            COALESCE(a.api_usage, 0) as api_usage,
            u.last_login
        FROM users u
        LEFT JOIN (
            SELECT user_id, COUNT(*) as video_count 
            FROM video_generations 
            GROUP BY user_id
        ) v ON u.id = v.user_id
        LEFT JOIN (
            SELECT user_id, COUNT(*) as api_usage 
            FROM api_keys 
            GROUP BY user_id
        ) a ON u.id = a.user_id
        ORDER BY u.created_at DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            users.append(UserResponse(
                id=str(row[0]),  # Ensure it's a string
                email=row[1],
                username=row[2],
                full_name=row[3],
                is_active=row[4],
                created_at=row[5],
                video_count=row[6] or 0,
                api_usage=row[7] or 0,
                last_login=row[8]
            ))
        
        cursor.close()
        conn.close()
        
        print(f"✅ Successfully retrieved {len(users)} users")
        return users
        
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate UUID for new user
        user_id = str(uuid.uuid4())
        
        # Proper password hashing with salt
        salt = str(uuid.uuid4())
        hashed_password = hashlib.sha256((user.password + salt).encode()).hexdigest() + ":" + salt
        
        query = """
        INSERT INTO users (id, email, username, hashed_password, full_name, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id::text, email, username, full_name, is_active, created_at
        """
        
        cursor.execute(query, (
            user_id, user.email, user.username, hashed_password, 
            user.full_name, user.is_active, datetime.now()
        ))
        
        row = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        new_user = UserResponse(
            id=str(row[0]),
            email=row[1],
            username=row[2],
            full_name=row[3],
            is_active=row[4],
            created_at=row[5],
            video_count=0,
            api_usage=0
        )
        
        print(f"✅ Created user: {new_user.username} (ID: {new_user.id})")
        return new_user
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        cursor.close()
        conn.close()
        if "email" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        elif "username" in str(e):
            raise HTTPException(status_code=400, detail="Username already exists")
        else:
            raise HTTPException(status_code=400, detail="User creation failed: duplicate data")
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"❌ Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate):  # Changed to str
    """Update an existing user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if user.email is not None:
            update_fields.append("email = %s")
            values.append(user.email)
        if user.username is not None:
            update_fields.append("username = %s")
            values.append(user.username)
        if user.full_name is not None:
            update_fields.append("full_name = %s")
            values.append(user.full_name)
        if user.is_active is not None:
            update_fields.append("is_active = %s")
            values.append(user.is_active)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(user_id)
        query = f"""
        UPDATE users 
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id::text, email, username, full_name, is_active, created_at
        """
        
        cursor.execute(query, values)
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        updated_user = UserResponse(
            id=str(row[0]),
            email=row[1],
            username=row[2],
            full_name=row[3],
            is_active=row[4],
            created_at=row[5],
            video_count=0,
            api_usage=0
        )
        
        print(f"✅ Updated user: {updated_user.username}")
        return updated_user
        
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):  # Changed to str
    """Delete a user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Deleted user ID: {user_id}")
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/users/{user_id}/status")
async def toggle_user_status(user_id: str):  # Changed to str
    """Toggle user active status."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE users 
        SET is_active = NOT is_active
        WHERE id = %s
        RETURNING is_active
        """
        
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        new_status = row[0]
        print(f"✅ Toggled user {user_id} status to: {new_status}")
        return {"user_id": user_id, "is_active": new_status}
        
    except Exception as e:
        print(f"❌ Error toggling user status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_user_stats():
    """Get overall user statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get various stats
        stats_queries = {
            'total_users': "SELECT COUNT(*) FROM users",
            'active_users': "SELECT COUNT(*) FROM users WHERE is_active = true",
            'total_videos': "SELECT COUNT(*) FROM video_generations",
            'total_api_keys': "SELECT COUNT(*) FROM api_keys"
        }
        
        stats = {}
        for stat_name, query in stats_queries.items():
            cursor.execute(query)
            result = cursor.fetchone()
            stats[stat_name] = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        print(f"✅ Retrieved stats: {stats}")
        return stats
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve the frontend HTML
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the user manager frontend."""
    try:
        html_path = os.path.join(os.path.dirname(__file__), "user_manager.html")
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>User Manager Frontend Not Found</h1><p>Please ensure user_manager.html exists in the same directory.</p>")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": f"error: {str(e)}"}

if __name__ == "__main__":
    print("🎭 Starting VeoGen User Manager Tool...")
    print("   Dashboard: http://localhost:8083")
    print("   API Docs: http://localhost:8083/docs")
    print("   Health: http://localhost:8083/health")
    print("   API Base: http://localhost:8083/api")
    
    # Test database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ Database connected successfully! Found {user_count} users.")
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        print("   Please ensure VeoGen PostgreSQL is running on localhost:4715")
    
    uvicorn.run(app, host="0.0.0.0", port=8083)
