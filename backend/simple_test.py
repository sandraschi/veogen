#!/usr/bin/env python3
print("Testing schema imports...")

try:
    from app.schemas import UserBase, MusicGenerationRequest, ImageGenerationRequest
    print("SUCCESS: All schemas imported correctly!")
    
    from app.main import app
    print("SUCCESS: Main app imported correctly!")
    
    print("READY: Backend should start without import errors!")
    
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
except Exception as e:
    print(f"ERROR: {e}")
