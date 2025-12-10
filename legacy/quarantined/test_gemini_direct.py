#!/usr/bin/env python3
"""
Test Gemini API directly
"""

import google.generativeai as genai
import os

def test_gemini():
    try:
        # Use the same API key as the container
        api_key = "AIzaSyC_LBvMeiRdQ8GVhcYt1egAruaGXSYx2oY"
        genai.configure(api_key=api_key)
        
        # Try different models
        models_to_test = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-2.0-flash-exp'
        ]
        
        for model_name in models_to_test:
            try:
                print(f"Testing {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say hello")
                print(f"  SUCCESS: {response.text[:50]}...")
                return True
            except Exception as e:
                print(f"  FAILED: {e}")
                continue
        
        print("All models failed")
        return False
        
    except Exception as e:
        print(f"Setup error: {e}")
        return False

if __name__ == "__main__":
    test_gemini()
