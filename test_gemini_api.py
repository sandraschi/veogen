#!/usr/bin/env python3
"""
Test Gemini API Key - Make sure it works before integrating
"""

import os
import sys
import asyncio
import google.generativeai as genai

async def test_gemini_api_key():
    print("=== Gemini API Key Test ===")
    
    # Get API key from user input
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return False
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test different models in order of preference
        models_to_test = [
            'gemini-1.5-flash',
            'gemini-1.5-pro', 
            'gemini-pro',
            'gemini-2.0-flash-exp'
        ]
        
        working_model = None
        
        for model_name in models_to_test:
            try:
                print(f"🧪 Testing {model_name}...")
                
                model = genai.GenerativeModel(model_name)
                response = await asyncio.to_thread(
                    model.generate_content,
                    "Hello! Please respond with 'SUCCESS' if you can understand this message."
                )
                
                if response and response.text:
                    print(f"✅ {model_name} works!")
                    print(f"Response: {response.text.strip()}")
                    working_model = model_name
                    break
                    
            except Exception as e:
                print(f"❌ {model_name} failed: {e}")
                continue
        
        if working_model:
            print(f"\n🎉 SUCCESS! Working model: {working_model}")
            print(f"✅ API Key is valid: {api_key[:10]}...")
            
            # Save to env file
            save_to_env = input("\nSave this API key to .env file? (y/n): ").strip().lower()
            if save_to_env == 'y':
                update_env_file(api_key, working_model)
            
            return True
        else:
            print("\n❌ No working models found. Check your API key.")
            return False
            
    except Exception as e:
        print(f"❌ API Key test failed: {e}")
        return False

def update_env_file(api_key, model_name):
    """Update the .env file with working API key and model"""
    try:
        env_path = ".env"
        
        # Read current .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update relevant lines
        updated_lines = []
        found_gemini_key = False
        found_google_key = False
        found_model = False
        
        for line in lines:
            if line.startswith('GEMINI_API_KEY='):
                updated_lines.append(f'GEMINI_API_KEY={api_key}\n')
                found_gemini_key = True
            elif line.startswith('GOOGLE_API_KEY='):
                updated_lines.append(f'GOOGLE_API_KEY={api_key}\n')
                found_google_key = True
            elif line.startswith('GEMINI_MODEL='):
                updated_lines.append(f'GEMINI_MODEL={model_name}\n')
                found_model = True
            else:
                updated_lines.append(line)
        
        # Add missing entries
        if not found_gemini_key:
            updated_lines.append(f'GEMINI_API_KEY={api_key}\n')
        if not found_google_key:
            updated_lines.append(f'GOOGLE_API_KEY={api_key}\n')
        if not found_model:
            updated_lines.append(f'GEMINI_MODEL={model_name}\n')
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"✅ Updated .env file with API key and model: {model_name}")
        print("🔄 Restart the backend to use the new key!")
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        print(f"💡 Manual update needed:")
        print(f"   GEMINI_API_KEY={api_key}")
        print(f"   GOOGLE_API_KEY={api_key}")
        print(f"   GEMINI_MODEL={model_name}")

if __name__ == "__main__":
    success = asyncio.run(test_gemini_api_key())
    
    if success:
        print("\n🚀 Ready to test VeoGen chat with real AI!")
        print("Next steps:")
        print("1. docker-compose restart backend")
        print("2. python test_chat_quick.py")
    else:
        print("\n💔 API key setup failed. Please try again.")
