#!/usr/bin/env python3
"""
Test documentation endpoint specifically
"""

import requests

def test_documentation():
    try:
        response = requests.get("http://localhost:4700/documentation/")
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        print(f"Content preview: {response.text[:500]}...")
        
        if response.status_code == 200:
            content = response.text.lower()
            checks = [
                ("HTML", "<html" in content),
                ("VeoGen", "veogen" in content),
                ("Docsify", "docsify" in content),
                ("Documentation", "documentation" in content),
            ]
            
            for name, check in checks:
                print(f"{name}: {'FOUND' if check else 'NOT FOUND'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_documentation()
