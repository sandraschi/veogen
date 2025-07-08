#!/usr/bin/env python3
"""Test database connection for User Manager"""

import psycopg2
from psycopg2.extras import DictCursor

# Different connection attempts
configs = [
    {
        'name': 'Config 1 - veogen123',
        'host': 'localhost',
        'port': 4715,
        'database': 'veogen',
        'user': 'veogen',
        'password': 'veogen123'
    },
    {
        'name': 'Config 2 - veogen_password',
        'host': 'localhost',
        'port': 4715,
        'database': 'veogen',
        'user': 'veogen',
        'password': 'veogen_password'
    },
    {
        'name': 'Config 3 - no password',
        'host': 'localhost',
        'port': 4715,
        'database': 'veogen',
        'user': 'veogen',
        'password': ''
    }
]

for config in configs:
    print(f"\nTrying {config['name']}...")
    try:
        conn = psycopg2.connect(**{k: v for k, v in config.items() if k != 'name'})
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Test query
        cursor.execute("SELECT COUNT(*) as user_count FROM users;")
        result = cursor.fetchone()
        print(f"SUCCESS: Connected! Found {result['user_count']} users")
        
        # Get first few users
        cursor.execute("SELECT id, email, full_name, is_active FROM users LIMIT 3;")
        users = cursor.fetchall()
        for user in users:
            print(f"  - {user['email']} ({user['full_name']}) - Active: {user['is_active']}")
        
        conn.close()
        print(f"✅ {config['name']} works!")
        break
        
    except Exception as e:
        print(f"❌ Failed: {e}")

print("\nDone testing database connections.")
