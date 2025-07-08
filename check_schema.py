#!/usr/bin/env python3
"""Check VeoGen database schema to understand table structure"""

import psycopg2
from psycopg2.extras import DictCursor

DB_CONFIG = {
    'host': 'localhost',
    'port': 4715,
    'database': 'veogen',
    'user': 'veogen',
    'password': 'veogen123'
}

def check_database_schema():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    print("=== VeoGen Database Schema Analysis ===\n")
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    print("Available Tables:")
    for table in tables:
        print(f"  - {table['table_name']}")
    
    print("\n" + "="*50)
    
    # Check users table structure
    if any(t['table_name'] == 'users' for t in tables):
        print("\nUSERS Table Structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} {'(nullable)' if col['is_nullable'] == 'YES' else '(not null)'}")
    
    # Check for video-related tables
    video_tables = [t['table_name'] for t in tables if 'video' in t['table_name'].lower()]
    if video_tables:
        print(f"\nVideo-related tables: {video_tables}")
        
        for table_name in video_tables[:2]:  # Limit to first 2 tables
            print(f"\n{table_name.upper()} Table Structure:")
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
    
    # Check for API-related tables
    api_tables = [t['table_name'] for t in tables if 'api' in t['table_name'].lower() or 'call' in t['table_name'].lower()]
    if api_tables:
        print(f"\nAPI-related tables: {api_tables}")
    
    conn.close()

if __name__ == "__main__":
    check_database_schema()
