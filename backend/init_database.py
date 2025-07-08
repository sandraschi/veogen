#!/usr/bin/env python3
"""
Database initialization and migration script for VeoGen
Ensures PostgreSQL is properly set up with all required tables and default data
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base, init_db
from app.models.user import User, UserSettings
from app.services.auth_service import AuthService
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_postgresql_connection():
    """Check if PostgreSQL connection is working"""
    try:
        database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
        if not database_url or not database_url.startswith("postgresql"):
            logger.error("❌ DATABASE_URL must be set to a valid PostgreSQL URL")
            logger.error(f"Current URL: {database_url}")
            return False
            
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ PostgreSQL connection successful: {version}")
            return True
            
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False

def create_default_admin():
    """Create default admin user if it doesn't exist"""
    try:
        database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        auth = AuthService()
        
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        
        if not admin:
            logger.info("Creating default admin user...")
            
            # Create admin user
            admin = User(
                id="admin",
                email="admin@admin.com",
                username="admin",
                hashed_password=auth.hash_password("admin"),
                is_active=True,
                is_verified=True,
                plan="admin",
                created_at=datetime.utcnow(),
                full_name="System Administrator"
            )
            
            db.add(admin)
            db.commit()
            
            # Set admin settings
            admin_settings = [
                ("theme", "dark", "string"),
                ("api_access", True, "boolean"),
                ("admin_panel", True, "boolean"),
                ("unlimited_generations", True, "boolean"),
                ("google_api_key", "", "string"),
                ("gemini_api_key", "", "string"),
                ("google_cloud_project", "", "string")
            ]
            
            for key, value, value_type in admin_settings:
                setting = UserSettings(
                    user_id="admin",
                    setting_key=key,
                    setting_value=str(value) if value_type != "boolean" else str(value).lower(),
                    setting_type=value_type
                )
                db.add(setting)
            
            db.commit()
            logger.info("✅ Default admin user created: admin@admin.com / admin")
        else:
            logger.info("✅ Admin user already exists")
            
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")
        return False

def migrate_from_sqlite():
    """Migrate data from SQLite to PostgreSQL if needed"""
    try:
        sqlite_path = "veogen.db"
        if not os.path.exists(sqlite_path):
            logger.info("No SQLite database found, skipping migration")
            return True
            
        logger.info("SQLite database found, checking for migration...")
        
        # Check if PostgreSQL already has data
        database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        user_count = db.query(User).count()
        db.close()
        
        if user_count > 1:  # More than just admin
            logger.info("PostgreSQL already has user data, skipping migration")
            return True
            
        # TODO: Implement actual migration logic here if needed
        # For now, we'll just log that SQLite exists
        logger.info("📝 SQLite migration would happen here if needed")
        logger.info("💡 For now, starting fresh with PostgreSQL")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration check failed: {e}")
        return False

def main():
    """Main initialization function"""
    logger.info("🚀 Initializing VeoGen database...")
    
    # Step 1: Check PostgreSQL connection
    logger.info("1️⃣ Checking PostgreSQL connection...")
    if not check_postgresql_connection():
        logger.error("❌ Database initialization failed")
        sys.exit(1)
    
    # Step 2: Check for SQLite migration
    logger.info("2️⃣ Checking for data migration...")
    if not migrate_from_sqlite():
        logger.error("❌ Migration check failed")
        sys.exit(1)
    
    # Step 3: Create database tables
    logger.info("3️⃣ Creating database tables...")
    try:
        init_db()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        sys.exit(1)
    
    # Step 4: Create default admin user
    logger.info("4️⃣ Setting up default admin user...")
    if not create_default_admin():
        logger.error("❌ Failed to create admin user")
        sys.exit(1)
    
    logger.info("✅ Database initialization completed successfully!")
    logger.info("📌 Default admin credentials: admin@admin.com / admin")
    logger.info("⚠️  Please change the admin password after first login!")

if __name__ == "__main__":
    main()
