#!/usr/bin/env python3
"""
Check FastAPI routes
"""

import requests
import json

def check_routes():
    """Check what routes are available"""
    try:
        # Check OpenAPI docs
        response = requests.get("http://localhost:4700/openapi.json")
        
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            print("Available API paths:")
            print("=" * 50)
            
            for path in sorted(paths.keys()):
                methods = list(paths[path].keys())
                print(f"  {path} - {', '.join(methods).upper()}")
                
            # Check specifically for logs paths
            logs_paths = [path for path in paths.keys() if 'logs' in path.lower()]
            print(f"\nLogs-related paths: {logs_paths}")
            
        else:
            print(f"Failed to get OpenAPI spec: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_routes()
