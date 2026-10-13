#!/usr/bin/env python3
import psycopg2
import bcrypt

# Database connection
DB_URL = "postgresql://veogen:veogen123@localhost:4715/veogen"

def create_valid_user():
    try:
        # Connect to database
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Create password hash for 'Test123!' (meets all requirements)
        password = 'Test123!'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        # Insert valid test user
        cursor.execute("""
            INSERT INTO users (id, email, username, hashed_password, is_active, is_verified, plan, full_name) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (email) DO UPDATE SET 
                hashed_password = EXCLUDED.hashed_password,
                is_active = EXCLUDED.is_active
        """, (
            'valid_user',
            'valid@test.com', 
            'validuser',
            hashed,
            True,
            True,
            'admin',
            'Valid Test User'
        ))
        
        conn.commit()
        print("SUCCESS: Created valid test user:")
        print("   Email: valid@test.com")
        print(f"   Password: {password}")
        print("   Password meets all requirements: 8+ chars, uppercase, lowercase, digit, special char")
        
        # Verify the user was created
        cursor.execute("SELECT email, username, is_active FROM users WHERE email = 'valid@test.com'")
        user = cursor.fetchone()
        if user:
            print(f"SUCCESS: User verified in database: {user}")
        else:
            print("ERROR: User not found in database")
            
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Error creating valid user: {e}")

if __name__ == "__main__":
    create_valid_user() 