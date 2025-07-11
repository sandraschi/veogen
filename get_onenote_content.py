#!/usr/bin/env python3
"""
Script to get OneNote content that returns HTML instead of JSON
This works around the MCP tool limitation that expects JSON responses.
"""

import requests
import re
import sys

def get_access_token():
    """
    In a real implementation, this would get the access token from Microsoft 365 auth
    For now, this is a template showing how to handle the HTML response
    """
    # This would need to be implemented with proper OAuth flow
    # or by extracting the token from the existing Microsoft 365 session
    print("⚠️  Access token needed - would get from Microsoft 365 auth")
    return None

def extract_phone_from_html(html_content, person_name="Reini"):
    """Extract phone number from OneNote HTML content"""
    
    # Strip HTML tags
    text = re.sub(r'<[^>]*>', ' ', html_content)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    print(f"Extracted text: {text[:200]}...")
    
    # Look for person name followed by phone number
    patterns = [
        rf'{person_name}[:\s]*0\d{{3}}\s?\d{{7}}',      # Reini: 0660 1234567
        rf'{person_name}[:\s]*0\d{{3}}\s?\d{{3}}\s?\d{{4}}',  # Reini: 0660 123 4567
        rf'{person_name}[:\s]*\d{{4}}\s?\d{{7}}',       # Reini 0660 1234567
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            print(f"Found match: {match.group()}")
            # Extract just the phone number part
            phone_match = re.search(r'0\d{3}\s?\d{3,4}\s?\d{3,4}', match.group())
            if phone_match:
                return phone_match.group()
    
    return None

def get_onenote_content():
    """
    Get OneNote page content - template for actual implementation
    """
    url = "https://graph.microsoft.com/v1.0/users/sandraschipal@hotmail.com/onenote/pages/0-36fe7419a99d360a12adca9ba92af7be!1-449F68AAD06F2DA5!398025/content"
    
    # This would need proper authentication
    token = get_access_token()
    if not token:
        print("❌ Cannot get access token")
        return None
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'text/html',  # Explicitly accept HTML
        'Content-Type': 'text/html'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🔍 OneNote Content Extractor")
    print("============================")
    
    # Test with sample HTML (since we can't get real token here)
    sample_html = '''
    <html xmlns="https://www.w3.org/1999/xhtml" lang="en-US">
    <head><title>Phone Numbers</title></head>
    <body data-absolute-enabled="true" style="font-family:Calibri;font-size:11px">
    <div data-id="_default" style="position:absolute;left:48px;top:120px;width:624px">
    <p>Phone Numbers</p>
    <p>Sandra 0664 987654</p>
    <p>Reini 0660 1234567</p>
    <p>Dr Mueller 01 4567890</p>
    </div>
    </body>
    </html>
    '''
    
    print("Testing with sample HTML...")
    phone = extract_phone_from_html(sample_html, "Reini")
    
    if phone:
        print(f"🎯 SUCCESS: Reini's phone number is: {phone}")
    else:
        print("❌ Could not find Reini's phone number")
    
    print("\n✅ Solution ready for real OneNote content!")
    print("Next: Get access token and apply to actual OneNote page")
