#!/usr/bin/env python3
"""
Fix persona chat by replacing Gemini CLI with direct API calls
"""

import os

# Read the original file
persona_service_path = r"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\backend\app\services\chat\persona_service.py"

with open(persona_service_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the complex gemini_service calls with simple direct API calls
fixed_content = content.replace(
    """# Generate background using Gemini CLI
            background_response = await self.gemini_service.generate_text(
                background_prompt,
                temperature=0.8,
                max_tokens=2000,
                db_session=db_session,
                user_id=user_id
            )""",
    """# Generate background using direct Gemini API
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-1.5-flash')
            background_response = model.generate_content(background_prompt).text"""
)

# Replace other generate_text calls
fixed_content = fixed_content.replace(
    """response = await self.gemini_service.generate_text(
                formatted_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                db_session=db_session,
                user_id=user_id
            )""",
    """import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(formatted_prompt).text"""
)

# Save the fixed file
with open(persona_service_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed persona service to use direct Gemini API calls")
