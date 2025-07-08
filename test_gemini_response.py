#!/usr/bin/env python3
"""
Test Gemini API response for specific prompt
"""

import os
import sys
import asyncio

# Set environment with your API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyCokmGkNRF67OgFFX4iki5gPE_BkazivfM'

import google.generativeai as genai

async def test_gemini_response():
    print("=== Testing Gemini Response ===")
    
    api_key = "AIzaSyCokmGkNRF67OgFFX4iki5gPE_BkazivfM"
    prompt = "what is the dzungar genocide"
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Use working model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print(f"Prompt: {prompt}")
        print("-" * 50)
        
        # Generate response
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        if response and response.text:
            print("Gemini Response:")
            print(response.text)
            print("-" * 50)
            print(f"Response length: {len(response.text)} characters")
            return True
        else:
            print("No response received")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_response())
    
    if success:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed!")
