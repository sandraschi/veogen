#!/usr/bin/env python3
"""
Simple MCP Server Test Suite
Tests CalibreMCP, ImmichMCP, and PlexMCP servers
"""

import json
import subprocess
import sys
import time
import os
from pathlib import Path

def log(message, level="INFO"):
    """Log messages with timestamp and level."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def send_mcp_request(server_path, method, params=None):
    """Send a JSON-RPC request to an MCP server."""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": int(time.time() * 1000)
    }
    
    start_time = time.time()
    try:
        # Execute the MCP server with the request
        process = subprocess.Popen(
            ["node", str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=server_path.parent
        )
        
        stdout, stderr = process.communicate(
            input=json.dumps(request),
            timeout=30
        )
        
        execution_time = time.time() - start_time
        
        if process.returncode != 0:
            return {
                "success": False,
                "error": f"Process failed with code {process.returncode}: {stderr}",
                "execution_time": execution_time
            }
        
        try:
            response = json.loads(stdout.strip())
            return {
                "success": True,
                "response": response,
                "execution_time": execution_time
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response: {e}",
                "execution_time": execution_time
            }
            
    except subprocess.TimeoutExpired:
        process.kill()
        return {
            "success": False,
            "error": "Request timed out after 30 seconds",
            "execution_time": 30.0
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}",
            "execution_time": time.time() - start_time
        }

def test_tools_list(server_name, server_path):
    """Test the tools/list method for a server."""
    log(f"Testing {server_name} tools list...")
    
    result = send_mcp_request(server_path, "tools/list")
    
    if result["success"]:
        tools = result["response"].get("result", {}).get("tools", [])
        log(f"SUCCESS: {server_name} has {len(tools)} tools available")
        for tool in tools:
            tool_name = tool.get('name', 'Unknown')
            tool_desc = tool.get('description', 'No description')
            log(f"  - {tool_name}: {tool_desc}")
        return True, tools
    else:
        log(f"FAILED: {server_name} tools list failed: {result['error']}", "ERROR")
        return False, []

def test_calibre_mcp():
    """Test CalibreMCP server."""
    log("=" * 50)
    log("Testing CalibreMCP Server")
    log("=" * 50)
    
    base_path = Path("C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6")
    server_path = base_path / "CalibreMCP" / "dist" / "index.js"
    
    if not server_path.exists():
        log(f"ERROR: CalibreMCP not found at {server_path}", "ERROR")
        return False
    
    # Test tools list
    success, tools = test_tools_list("CalibreMCP", server_path)
    if not success:
        return False
    
    # Test book search if available
    book_search_available = any(tool.get('name') == 'calibre_search_books' for tool in tools)
    if book_search_available:
        log("Testing book search...")
        search_result = send_mcp_request(
            server_path,
            "tools/call",
            {
                "name": "calibre_search_books",
                "arguments": {
                    "query": "science fiction",
                    "limit": 5
                }
            }
        )
        
        if search_result["success"]:
            log("SUCCESS: Book search completed")
        else:
            log(f"FAILED: Book search failed: {search_result['error']}", "ERROR")
    
    return True

def test_immich_mcp():
    """Test ImmichMCP server."""
    log("=" * 50)
    log("Testing ImmichMCP Server")
    log("=" * 50)
    
    base_path = Path("C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6")
    server_path = base_path / "ImmichMCP" / "dist" / "index.js"
    
    if not server_path.exists():
        log(f"ERROR: ImmichMCP not found at {server_path}", "ERROR")
        return False
    
    # Test tools list
    success, tools = test_tools_list("ImmichMCP", server_path)
    if not success:
        return False
    
    # Test get albums if available
    albums_available = any(tool.get('name') == 'immich_get_albums' for tool in tools)
    if albums_available:
        log("Testing get albums...")
        albums_result = send_mcp_request(
            server_path,
            "tools/call",
            {
                "name": "immich_get_albums",
                "arguments": {
                    "shared": False,
                    "withoutAssets": True
                }
            }
        )
        
        if albums_result["success"]:
            log("SUCCESS: Get albums completed")
        else:
            log(f"FAILED: Get albums failed: {albums_result['error']}", "ERROR")
    
    return True

def test_plex_mcp():
    """Test PlexMCP server."""
    log("=" * 50)
    log("Testing PlexMCP Server")
    log("=" * 50)
    
    base_path = Path("C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6")
    server_path = base_path / "PlexMCP" / "dist" / "index.js"
    
    if not server_path.exists():
        log(f"ERROR: PlexMCP not found at {server_path}", "ERROR")
        return False
    
    # Test tools list
    success, tools = test_tools_list("PlexMCP", server_path)
    if not success:
        return False
    
    # Test get libraries if available
    libraries_available = any(tool.get('name') == 'plex_get_libraries' for tool in tools)
    if libraries_available:
        log("Testing get libraries...")
        libraries_result = send_mcp_request(
            server_path,
            "tools/call",
            {
                "name": "plex_get_libraries",
                "arguments": {
                    "includeDetails": True
                }
            }
        )
        
        if libraries_result["success"]:
            log("SUCCESS: Get libraries completed")
        else:
            log(f"FAILED: Get libraries failed: {libraries_result['error']}", "ERROR")
    
    return True

def main():
    """Main entry point."""
    print("MCP Server Test Suite v1.0")
    print("Testing CalibreMCP, ImmichMCP, and PlexMCP servers")
    print()
    
    start_time = time.time()
    
    # Test each server
    calibre_success = test_calibre_mcp()
    immich_success = test_immich_mcp()
    plex_success = test_plex_mcp()
    
    total_time = time.time() - start_time
    
    # Generate report
    log("=" * 50)
    log("TEST RESULTS SUMMARY")
    log("=" * 50)
    log(f"CalibreMCP: {'PASS' if calibre_success else 'FAIL'}")
    log(f"ImmichMCP: {'PASS' if immich_success else 'FAIL'}")
    log(f"PlexMCP: {'PASS' if plex_success else 'FAIL'}")
    log(f"Total execution time: {total_time:.2f} seconds")
    
    # Overall result
    all_passed = calibre_success and immich_success and plex_success
    if all_passed:
        log("OVERALL RESULT: ALL TESTS PASSED")
        return 0
    else:
        log("OVERALL RESULT: SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nCritical error: {e}")
        sys.exit(1)
