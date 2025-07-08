#!/usr/bin/env python3
"""
Quick test to fix Gemini API model issue
"""

import os
import sys
import asyncio
import logging

# Add the backend to the path
sys.path.append('backend')

from app.services.gemini_cli import gemini_service

async def test_gemini_fix():
    print("=== Testing Gemini API Fix ===")
    
    try:
        # Test with a simple prompt
        response = await gemini_service.generate_text(
            prompt="Hello! Please respond with 'Working!' if you can understand this.",
            temperature=0.7
        )
        
        print(f"✅ Gemini response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_fix())
    if success:
        print("\n🎉 Gemini API is working!")
    else:
        print("\n💔 Gemini API needs fixing")
