#!/usr/bin/env python3
"""
Server runner script that manages Python path to avoid conflicts
"""

import sys
import os
import subprocess

# Clear any problematic paths from sys.path
sys.path = [p for p in sys.path if 'homecontrol' not in p and 'ExperimentsInAI' not in p]

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    try:
        import uvicorn
        from app.main import app
        
        print("Starting VeoGen backend server on port 7655...")
        print("Python path:", sys.path[:3])  # Show first 3 paths
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=7655,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc() 