#!/usr/bin/env python3
"""
🧪 Comprehensive MCP Server Test Suite
Tests CalibreMCP, ImmichMCP, and PlexMCP servers with full capability coverage
"""

import json
import subprocess
import sys
import time
import os
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MCPTestResult:
    server_name: str
    tool_name: str
    success: bool
    response: Any
    error: Optional[str]
    execution_time: float

class MCPServerTester:
    def __init__(self):
        self.results: List[MCPTestResult] = []
        self.base_path = Path("C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6")
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp and level."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def send_mcp_request(self, server_path: str, method: str, params: Dict = None) -> Dict:
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
                    "error": f"Invalid JSON response: {e}\nRaw output: {stdout}",
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

    def test_server_tools_list(self, server_name: str, server_path: Path) -> bool:
        """Test the tools/list method for a server."""
        self.log(f"🔍 Testing {server_name} tools list...")
        
        result = self.send_mcp_request(server_path, "tools/list")
        
        test_result = MCPTestResult(
            server_name=server_name,
            tool_name="tools/list",
            success=result["success"],
            response=result.get("response"),
            error=result.get("error"),
            execution_time=result["execution_time"]
        )
        self.results.append(test_result)
        
        if result["success"]:
            tools = result["response"].get("result", {}).get("tools", [])
            self.log(f"✅ {server_name} has {len(tools)} tools available")
            for tool in tools:
                self.log(f"   📋 {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            return True
        else:
            self.log(f"❌ {server_name} tools list failed: {result['error']}", "ERROR")
            return False

    def test_calibre_mcp(self) -> List[MCPTestResult]:
        """Test CalibreMCP server capabilities."""
        self.log("📚 Testing CalibreMCP Server...")
        server_path = self.base_path / "CalibreMCP" / "dist" / "index.js"
        
        if not server_path.exists():
            self.log(f"❌ CalibreMCP not found at {server_path}", "ERROR")
            return []
        
        # Test tools list
        if not self.test_server_tools_list("CalibreMCP", server_path):
            return self.results
        
        # Test book search
        self.log("🔍 Testing book search...")
        search_result = self.send_mcp_request(
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
        
        self.results.append(MCPTestResult(
            server_name="CalibreMCP",
            tool_name="calibre_search_books",
            success=search_result["success"],
            response=search_result.get("response"),
            error=search_result.get("error"),
            execution_time=search_result["execution_time"]
        ))
        
        if search_result["success"]:
            self.log("✅ Book search successful")
        else:
            self.log(f"❌ Book search failed: {search_result['error']}", "ERROR")
        
        # Test book details (if we have books)
        if search_result["success"]:
            try:
                books = search_result["response"].get("result", {}).get("content", [])
                if books and isinstance(books, list) and len(books) > 0:
                    first_book = books[0]
                    if isinstance(first_book, dict) and "id" in first_book:
                        self.log("📖 Testing book details...")
                        details_result = self.send_mcp_request(
                            server_path,
                            "tools/call",
                            {
                                "name": "calibre_get_book_details",
                                "arguments": {
                                    "book_id": first_book["id"]
                                }
                            }
                        )
                        
                        self.results.append(MCPTestResult(
                            server_name="CalibreMCP",
                            tool_name="calibre_get_book_details",
                            success=details_result["success"],
                            response=details_result.get("response"),
                            error=details_result.get("error"),
                            execution_time=details_result["execution_time"]
                        ))
                        
                        if details_result["success"]:
                            self.log("✅ Book details successful")
                        else:
                            self.log(f"❌ Book details failed: {details_result['error']}", "ERROR")
            except Exception as e:
                self.log(f"⚠️ Could not test book details: {e}", "WARN")
        
        return [r for r in self.results if r.server_name == "CalibreMCP"]

    def test_immich_mcp(self) -> List[MCPTestResult]:
        """Test ImmichMCP server capabilities."""
        self.log("📸 Testing ImmichMCP Server...")
        server_path = self.base_path / "ImmichMCP" / "dist" / "index.js"
        
        if not server_path.exists():
            self.log(f"❌ ImmichMCP not found at {server_path}", "ERROR")
            return []
        
        # Test tools list
        if not self.test_server_tools_list("ImmichMCP", server_path):
            return self.results
        
        # Test get albums
        self.log("📚 Testing get albums...")
        albums_result = self.send_mcp_request(
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
        
        self.results.append(MCPTestResult(
            server_name="ImmichMCP",
            tool_name="immich_get_albums",
            success=albums_result["success"],
            response=albums_result.get("response"),
            error=albums_result.get("error"),
            execution_time=albums_result["execution_time"]
        ))
        
        if albums_result["success"]:
            self.log("✅ Get albums successful")
        else:
            self.log(f"❌ Get albums failed: {albums_result['error']}", "ERROR")
        
        # Test search photos
        self.log("🔍 Testing photo search...")
        search_result = self.send_mcp_request(
            server_path,
            "tools/call",
            {
                "name": "immich_search_photos",
                "arguments": {
                    "query": "vacation",
                    "size": 10
                }
            }
        )
        
        self.results.append(MCPTestResult(
            server_name="ImmichMCP",
            tool_name="immich_search_photos",
            success=search_result["success"],
            response=search_result.get("response"),
            error=search_result.get("error"),
            execution_time=search_result["execution_time"]
        ))
        
        if search_result["success"]:
            self.log("✅ Photo search successful")
        else:
            self.log(f"❌ Photo search failed: {search_result['error']}", "ERROR")
        
        return [r for r in self.results if r.server_name == "ImmichMCP"]

    def test_plex_mcp(self) -> List[MCPTestResult]:
        """Test PlexMCP server capabilities."""
        self.log("🎬 Testing PlexMCP Server...")
        server_path = self.base_path / "PlexMCP" / "dist" / "index.js"
        
        if not server_path.exists():
            self.log(f"❌ PlexMCP not found at {server_path}", "ERROR")
            return []
        
        # Test tools list
        if not self.test_server_tools_list("PlexMCP", server_path):
            return self.results
        
        # Test get libraries
        self.log("📚 Testing get libraries...")
        libraries_result = self.send_mcp_request(
            server_path,
            "tools/call",
            {
                "name": "plex_get_libraries",
                "arguments": {
                    "includeDetails": True
                }
            }
        )
        
        self.results.append(MCPTestResult(
            server_name="PlexMCP",
            tool_name="plex_get_libraries",
            success=libraries_result["success"],
            response=libraries_result.get("response"),
            error=libraries_result.get("error"),
            execution_time=libraries_result["execution_time"]
        ))
        
        if libraries_result["success"]:
            self.log("✅ Get libraries successful")
        else:
            self.log(f"❌ Get libraries failed: {libraries_result['error']}", "ERROR")
        
        # Test server status
        self.log("📊 Testing server status...")
        status_result = self.send_mcp_request(
            server_path,
            "tools/call",
            {
                "name": "plex_get_server_status",
                "arguments": {
                    "includeVersion": True
                }
            }
        )
        
        self.results.append(MCPTestResult(
            server_name="PlexMCP",
            tool_name="plex_get_server_status",
            success=status_result["success"],
            response=status_result.get("response"),
            error=status_result.get("error"),
            execution_time=status_result["execution_time"]
        ))
        
        if status_result["success"]:
            self.log("✅ Server status successful")
        else:
            self.log(f"❌ Server status failed: {status_result['error']}", "ERROR")
        
        # Test media search
        self.log("🔍 Testing media search...")
        search_result = self.send_mcp_request(
            server_path,
            "tools/call",
            {
                "name": "plex_search_media",
                "arguments": {
                    "query": "action",
                    "type": "movie"
                }
            }
        )
        
        self.results.append(MCPTestResult(
            server_name="PlexMCP",
            tool_name="plex_search_media",
            success=search_result["success"],
            response=search_result.get("response"),
            error=search_result.get("error"),
            execution_time=search_result["execution_time"]
        ))
        
        if search_result["success"]:
            self.log("✅ Media search successful")
        else:
            self.log(f"❌ Media search failed: {search_result['error']}", "ERROR")
        
        return [r for r in self.results if r.server_name == "PlexMCP"]

    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Group results by server
        servers = {}
        for result in self.results:
            if result.server_name not in servers:
                servers[result.server_name] = []
            servers[result.server_name].append(result)
        
        report = []
        report.append("MCP Server Test Report")
        report.append("=" * 60)
        report.append(f"📊 Total Tests: {total_tests}")
        report.append(f"✅ Successful: {successful_tests}")
        report.append(f"❌ Failed: {failed_tests}")
        report.append(f"📈 Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "📈 Success Rate: 0%")
        report.append("")
        
        for server_name, results in servers.items():
            server_success = sum(1 for r in results if r.success)
            server_total = len(results)
            
            report.append(f"🔧 {server_name}")
            report.append("-" * 40)
            report.append(f"Status: {server_success}/{server_total} tests passed")
            
            for result in results:
                status = "✅" if result.success else "❌"
                time_str = f"{result.execution_time:.2f}s"
                report.append(f"  {status} {result.tool_name} ({time_str})")
                
                if not result.success and result.error:
                    # Truncate long error messages
                    error_msg = result.error[:100] + "..." if len(result.error) > 100 else result.error
                    report.append(f"      Error: {error_msg}")
            
            report.append("")
        
        # Performance analysis
        if self.results:
            avg_time = sum(r.execution_time for r in self.results) / len(self.results)
            max_time = max(r.execution_time for r in self.results)
            min_time = min(r.execution_time for r in self.results)
            
            report.append("⚡ Performance Summary")
            report.append("-" * 40)
            report.append(f"Average Response Time: {avg_time:.2f}s")
            report.append(f"Fastest Response: {min_time:.2f}s")
            report.append(f"Slowest Response: {max_time:.2f}s")
            report.append("")
        
        # Recommendations
        report.append("💡 Recommendations")
        report.append("-" * 40)
        
        if failed_tests > 0:
            report.append("🔧 Some tests failed. Check:")
            report.append("   - MCP server environment variables")
            report.append("   - External services (Calibre, Immich, Plex) are running")
            report.append("   - Network connectivity")
            report.append("   - API keys and authentication")
        else:
            report.append("🎉 All tests passed! MCP servers are working correctly.")
        
        if any(r.execution_time > 5 for r in self.results):
            report.append("⚠️ Some responses were slow (>5s). Consider:")
            report.append("   - Optimizing server configuration")
            report.append("   - Checking system resources")
            report.append("   - Reducing query complexity")
        
        report.append("")
        report.append(f"📅 Report generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(report)

    def run_all_tests(self) -> str:
        """Run all MCP server tests and return a report."""
        self.log("🚀 Starting comprehensive MCP server tests...")
        start_time = time.time()
        
        # Test each server
        self.test_calibre_mcp()
        self.test_immich_mcp()
        self.test_plex_mcp()
        
        total_time = time.time() - start_time
        self.log(f"🏁 All tests completed in {total_time:.2f} seconds")
        
        return self.generate_report()

def main():
    """Main entry point for the test suite."""
    print("MCP Server Test Suite v1.0")
    print("Testing CalibreMCP, ImmichMCP, and PlexMCP servers...")
    print()
    
    tester = MCPServerTester()
    
    try:
        report = tester.run_all_tests()
        
        # Print report to console
        print("\n" + report)
        
        # Save report to file
        report_path = Path("C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/mcp_test_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_path}")
        
        # Return appropriate exit code
        failed_tests = sum(1 for r in tester.results if not r.success)
        sys.exit(0 if failed_tests == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
