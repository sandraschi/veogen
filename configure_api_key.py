#!/usr/bin/env python3
"""
Direct API key configuration with your key
"""

import os
import sys
import asyncio
import google.generativeai as genai

async def test_and_configure_api():
    print("=== Testing Your Gemini API Key ===")
    
    # Your API key
    api_key = "AIzaSyCokmGkNRF67OgFFX4iki5gPE_BkazivfM"
    project_id = "899454364898"
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        print(f"✅ API Key configured: {api_key[:10]}...")
        
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
                    "Hello! Please respond with 'SUCCESS - I am working!' if you can understand this message."
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
            update_env_file(api_key, working_model, project_id)
            return True
        else:
            print("\n❌ No working models found.")
            return False
            
    except Exception as e:
        print(f"❌ API Key test failed: {e}")
        return False

def update_env_file(api_key, model_name, project_id):
    """Update the .env file with working API key and model"""
    try:
        env_path = ".env"
        
        # Read current .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update relevant lines
        updated_lines = []
        keys_updated = {
            'GEMINI_API_KEY': False,
            'GOOGLE_API_KEY': False,
            'GEMINI_MODEL': False,
            'GOOGLE_CLOUD_PROJECT': False
        }
        
        for line in lines:
            if line.startswith('GEMINI_API_KEY='):
                updated_lines.append(f'GEMINI_API_KEY={api_key}\n')
                keys_updated['GEMINI_API_KEY'] = True
            elif line.startswith('GOOGLE_API_KEY='):
                updated_lines.append(f'GOOGLE_API_KEY={api_key}\n')
                keys_updated['GOOGLE_API_KEY'] = True
            elif line.startswith('GEMINI_MODEL='):
                updated_lines.append(f'GEMINI_MODEL={model_name}\n')
                keys_updated['GEMINI_MODEL'] = True
            elif line.startswith('GOOGLE_CLOUD_PROJECT='):
                updated_lines.append(f'GOOGLE_CLOUD_PROJECT={project_id}\n')
                keys_updated['GOOGLE_CLOUD_PROJECT'] = True
            else:
                updated_lines.append(line)
        
        # Add missing entries
        for key, updated in keys_updated.items():
            if not updated:
                if key == 'GEMINI_API_KEY':
                    updated_lines.append(f'GEMINI_API_KEY={api_key}\n')
                elif key == 'GOOGLE_API_KEY':
                    updated_lines.append(f'GOOGLE_API_KEY={api_key}\n')
                elif key == 'GEMINI_MODEL':
                    updated_lines.append(f'GEMINI_MODEL={model_name}\n')
                elif key == 'GOOGLE_CLOUD_PROJECT':
                    updated_lines.append(f'GOOGLE_CLOUD_PROJECT={project_id}\n')
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"✅ Updated .env file:")
        print(f"   GEMINI_API_KEY={api_key[:10]}...")
        print(f"   GOOGLE_API_KEY={api_key[:10]}...")
        print(f"   GEMINI_MODEL={model_name}")
        print(f"   GOOGLE_CLOUD_PROJECT={project_id}")
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")

if __name__ == "__main__":
    success = asyncio.run(test_and_configure_api())
    
    if success:
        print("\n🚀 API Key configured successfully!")
        print("Next steps:")
        print("1. docker-compose restart backend")
        print("2. python test_chat_quick.py")
        print("3. Test real AI chat at http://localhost:4710/chat")
    else:
        print("\n💔 API key setup failed.")
