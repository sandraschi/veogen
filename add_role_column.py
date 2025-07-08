#!/usr/bin/env python3
"""
Add role column to users table and update existing users
Roles: admin, user, guest
"""

import psycopg2
from psycopg2.extras import DictCursor

DB_CONFIG = {
    'host': 'localhost',
    'port': 4715,
    'database': 'veogen',
    'user': 'veogen',
    'password': 'veogen123'
}

def add_role_column():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        print("=== Adding Role Column to Users Table ===\n")
        
        # Check if role column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'role'
        """)
        
        if cursor.fetchone():
            print("SUCCESS: Role column already exists!")
        else:
            # Add role column with default value
            print("ADDING: Role column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(20) DEFAULT 'user'
            """)
            print("SUCCESS: Role column added successfully!")
        
        # Update existing users based on current data
        print("\nUPDATING: Existing user roles...")
        
        # Set admin role for admin accounts
        cursor.execute("""
            UPDATE users 
            SET role = 'admin' 
            WHERE email IN ('admin@veogen.com', 'sandraschipal@hotmail.com') 
               OR username IN ('admin', 'sas13')
               OR plan = 'admin'
        """)
        admin_count = cursor.rowcount
        
        # Set user role for verified, active accounts
        cursor.execute("""
            UPDATE users 
            SET role = 'user' 
            WHERE role IS NULL 
               AND is_active = true 
               AND is_verified = true
        """)
        user_count = cursor.rowcount
        
        # Set guest role for unverified or inactive accounts
        cursor.execute("""
            UPDATE users 
            SET role = 'guest' 
            WHERE role IS NULL
        """)
        guest_count = cursor.rowcount
        
        # Commit changes
        conn.commit()
        
        print(f"SUCCESS: Updated {admin_count} admin users")
        print(f"SUCCESS: Updated {user_count} regular users") 
        print(f"SUCCESS: Updated {guest_count} guest users")
        
        # Show current role distribution
        print("\nCurrent Role Distribution:")
        cursor.execute("""
            SELECT role, COUNT(*) as count
            FROM users 
            GROUP BY role
            ORDER BY 
                CASE role 
                    WHEN 'admin' THEN 1
                    WHEN 'user' THEN 2  
                    WHEN 'guest' THEN 3
                    ELSE 4
                END
        """)
        
        for row in cursor.fetchall():
            print(f"  {row['role'].upper()}: {row['count']} users")
            
        # Show some example users
        print("\nExample Users by Role:")
        cursor.execute("""
            SELECT role, full_name, email, username
            FROM users 
            ORDER BY 
                CASE role 
                    WHEN 'admin' THEN 1
                    WHEN 'user' THEN 2
                    WHEN 'guest' THEN 3
                END,
                created_at
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"  {row['role'].upper()}: {row['full_name']} ({row['email']})")
            
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_role_column()
