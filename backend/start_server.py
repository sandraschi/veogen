#!/usr/bin/env python3
import sys
import os
import subprocess

# Completely clear sys.path and set only what we need
sys.path = []

# Add only the current directory and standard library paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add standard library paths back
import site
sys.path.extend(site.getsitepackages())
sys.path.extend(site.getusersitepackages())

# Filter out any problematic paths
sys.path = [p for p in sys.path if p and 'homecontrol' not in p and 'ExperimentsInAI' not in p]

if __name__ == "__main__":
    try:
        print("Starting VeoGen backend server on port 7655...")
        print(f"Current directory: {current_dir}")
        print(f"Python path (first 3): {sys.path[:3]}")
        
        # Import and run the FastAPI app
        import uvicorn
        from app.main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=7655,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1) 