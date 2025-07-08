import os
import sys
import asyncio

# Add backend to path
sys.path.append('backend')

# Set environment variables directly
os.environ['GEMINI_API_KEY'] = 'AIzaSyCokmGkNRF67OgFFX4iki5gPE_BkazivfM'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCokmGkNRF67OgFFX4iki5gPE_BkazivfM'
os.environ['GOOGLE_CLOUD_PROJECT'] = '899454364898'
os.environ['GEMINI_MODEL'] = 'gemini-1.5-flash'

import google.generativeai as genai

async def test_api():
    print("Testing Gemini API...")
    
    api_key = "AIzaSyCokmGkNRF67OgFFX4iki5gPE_BkazivfM"
    
    try:
        genai.configure(api_key=api_key)
        print(f"API Key configured: {api_key[:10]}...")
        
        models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        for model_name in models:
            try:
                print(f"Testing {model_name}...")
                
                model = genai.GenerativeModel(model_name)
                response = await asyncio.to_thread(
                    model.generate_content,
                    "Hello! Please respond with 'SUCCESS - I am working!' if you understand this."
                )
                
                if response and response.text:
                    print(f"SUCCESS! {model_name} works!")
                    print(f"Response: {response.text.strip()}")
                    
                    # Update .env file
                    update_env_file(api_key, model_name)
                    return True
                    
            except Exception as e:
                print(f"FAILED: {model_name} - {e}")
                continue
        
        print("No working models found")
        return False
        
    except Exception as e:
        print(f"API test failed: {e}")
        return False

def update_env_file(api_key, model_name):
    """Update .env file"""
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        updated_lines = []
        keys_found = set()
        
        for line in lines:
            if line.startswith('GEMINI_API_KEY='):
                updated_lines.append(f'GEMINI_API_KEY={api_key}\n')
                keys_found.add('GEMINI_API_KEY')
            elif line.startswith('GOOGLE_API_KEY='):
                updated_lines.append(f'GOOGLE_API_KEY={api_key}\n')
                keys_found.add('GOOGLE_API_KEY')
            elif line.startswith('GEMINI_MODEL='):
                updated_lines.append(f'GEMINI_MODEL={model_name}\n')
                keys_found.add('GEMINI_MODEL')
            elif line.startswith('GOOGLE_CLOUD_PROJECT='):
                updated_lines.append(f'GOOGLE_CLOUD_PROJECT=899454364898\n')
                keys_found.add('GOOGLE_CLOUD_PROJECT')
            else:
                updated_lines.append(line)
        
        # Add missing keys
        if 'GEMINI_API_KEY' not in keys_found:
            updated_lines.append(f'GEMINI_API_KEY={api_key}\n')
        if 'GOOGLE_API_KEY' not in keys_found:
            updated_lines.append(f'GOOGLE_API_KEY={api_key}\n')
        if 'GEMINI_MODEL' not in keys_found:
            updated_lines.append(f'GEMINI_MODEL={model_name}\n')
        if 'GOOGLE_CLOUD_PROJECT' not in keys_found:
            updated_lines.append(f'GOOGLE_CLOUD_PROJECT=899454364898\n')
        
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        print(f"Updated .env with {model_name}")
        
    except Exception as e:
        print(f"Failed to update .env: {e}")

if __name__ == "__main__":
    success = asyncio.run(test_api())
    
    if success:
        print("\nSUCCESS! API key is working!")
        print("Next steps:")
        print("1. docker-compose restart backend")
        print("2. python test_chat_quick.py")
    else:
        print("\nFAILED! Check your API key")
