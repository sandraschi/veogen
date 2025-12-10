"""
MCP (Model Control Protocol) client implementation for VeoGen.
Automatically connects to all MCP servers from Claude Desktop configuration.
Follows FastMCP 2.11.3 standards.
"""
import json
import logging
import subprocess
import os
import platform
from typing import Any, Dict, List
import asyncio

logger = logging.getLogger(__name__)

# Default paths for Claude Desktop configuration
DEFAULT_CONFIG_PATHS = {
    'Windows': [
        r'C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json',  # Primary path
        os.path.expandvars(r'%APPDATA%\\Claude\\claude_desktop_config.json'),
        os.path.expandvars(r'%APPDATA%\\AnthropicClaude\\claude-desktop-config.json'),
        os.path.expandvars(r'%LOCALAPPDATA%\\AnthropicClaude\\claude-desktop-config.json'),
    ],
    'Darwin': [
        os.path.expanduser('~/Library/Application Support/Claude/claude_desktop_config.json'),
        os.path.expanduser('~/Library/Application Support/AnthropicClaude/claude-desktop-config.json'),
    ],
    'Linux': [
        os.path.expanduser('~/.config/Claude/claude_desktop_config.json'),
        os.path.expanduser('~/.config/AnthropicClaude/claude-desktop-config.json'),
    ]
}

class MCPClient:
    """MCP client for discovering and connecting to all available MCP servers."""
    
    def __init__(self, config_path: str = None):
        """Initialize MCP client with optional config path or auto-discover from Claude Desktop."""
        self.servers: Dict[str, Dict] = {}
        self.processes: Dict[str, Any] = {}
        self.available_tools: Dict[str, List[Dict[str, Any]]] = {}
        
        # Try to load from explicit path first, then auto-discover
        if config_path:
            self.load_config(config_path)
        else:
            self.auto_discover_servers()
            
        # Start all auto-start servers
        asyncio.create_task(self.start_auto_servers())
        
    def auto_discover_servers(self) -> bool:
        """Auto-discover MCP servers from Claude Desktop configuration."""
        system = platform.system()
        config_paths = DEFAULT_CONFIG_PATHS.get(system, [])
        
        for path in config_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        
                    # Handle different config formats
                    if 'mcpServers' in config:
                        self.servers = config['mcpServers']
                        logger.info(f"Loaded {len(self.servers)} MCP servers from {path}")
                        
                        # Filter out disabled servers
                        self.servers = {
                            name: config 
                            for name, config in self.servers.items() 
                            if not config.get('disabled', False)
                        }
                        
                        # Log enabled servers
                        if self.servers:
                            logger.info(f"Enabled MCP servers: {', '.join(self.servers.keys())}")
                        
                        return True
                    else:
                        logger.warning(f"No 'mcpServers' key found in {path}")
                        
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file {path}: {e}")
            except Exception as e:
                logger.warning(f"Error loading MCP config from {path}: {e}", exc_info=True)
                
        logger.warning("No valid MCP configuration found in default locations")
        return False

    def load_config(self, config_path: str) -> None:
        """Load MCP server configurations from config file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Support both direct mcpServers and nested servers format
                if 'mcpServers' in config:
                    self.servers = config['mcpServers']
                elif 'servers' in config:
                    self.servers = config['servers']
                else:
                    self.servers = {}
                    
                logger.info(f"Loaded {len(self.servers)} MCP servers from {config_path}")
                
        except FileNotFoundError:
            logger.warning(f"MCP config file not found: {config_path}")
            self.servers = {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid MCP config file {config_path}: {e}")
            self.servers = {}

    async def start_auto_servers(self) -> None:
        """Start all servers with autoStart=true."""
        for server_name, config in self.servers.items():
            if not config.get('disabled', False) and config.get('autoStart', True):
                await self.start_server(server_name)
                
    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server by name."""
        if server_name in self.processes:
            return True  # Already running
            
        if server_name not in self.servers:
            logger.error(f"Unknown MCP server: {server_name}")
            return False
            
        server_config = self.servers[server_name]
        
        if server_config.get('disabled', False):
            logger.info(f"Skipping disabled MCP server: {server_name}")
            return False
            
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(server_config.get('env', {}))
            
            # Handle command as list or string
            command = server_config['command']
            args = server_config.get('args', [])
            
            if isinstance(args, str):
                import shlex
                args = shlex.split(args)
                
            # Start the process
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=server_config.get('cwd')
            )
            
            self.processes[server_name] = process
            logger.info(f"Started MCP server: {server_name}")
            
            # Discover tools after startup
            await self.discover_server_tools(server_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server {server_name}: {e}", exc_info=True)
            return False

    async def stop_server(self, server_name: str) -> bool:
        """Stop a running MCP server."""
        if server_name not in self.processes:
            return True
            
        process = self.processes[server_name]
        try:
            process.terminate()
            await process.wait()
            del self.processes[server_name]
            return True
        except Exception as e:
            logger.error(f"Error stopping MCP server {server_name}: {e}")
            return False

    async def discover_server_tools(self, server_name: str) -> bool:
        """Discover and cache tools from an MCP server."""
        try:
            tools = await self.call_tool(server_name, "mcp.discover", {})
            if isinstance(tools, dict) and 'result' in tools:
                self.available_tools[server_name] = tools['result'].get('tools', [])
                logger.info(f"Discovered {len(self.available_tools[server_name])} tools from {server_name}")
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to discover tools from {server_name}: {e}")
            return False
            
    def get_available_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available tools from all connected servers."""
        return self.available_tools
        
    def find_tool(self, tool_name: str) -> List[Dict[str, Any]]:
        """Find tools by name across all servers."""
        results = []
        for server, tools in self.available_tools.items():
            for tool in tools:
                if tool.get('name') == tool_name:
                    results.append({
                        'server': server,
                        'tool': tool
                    })
        return results
        
    async def call_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        params: Dict[str, Any],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Call a tool on an MCP server.
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            params: Parameters for the tool
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with the result or error information
        """
        if server_name not in self.processes:
            started = await self.start_server(server_name)
            if not started:
                return {"error": f"Failed to start MCP server: {server_name}"}
                
        process = self.processes[server_name]
        
        # Generate a unique request ID
        import uuid
        request_id = str(uuid.uuid4())
        
        # Prepare the MCP request
        request = {
            "jsonrpc": "2.0",
            "method": tool_name,
            "params": params,
            "id": request_id
        }
        
        try:
            # Send request
            request_str = json.dumps(request) + "\n"
            process.stdin.write(request_str.encode('utf-8'))
            await process.stdin.drain()
            
            # Read response with timeout
            try:
                response_str = await asyncio.wait_for(
                    process.stdout.readline(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout calling {server_name}.{tool_name}")
                return {"error": f"Timeout calling {server_name}.{tool_name}"}
                
            if not response_str:
                return {"error": f"Empty response from {server_name}.{tool_name}"}
                
            response = json.loads(response_str)
            
            # Handle error responses
            if 'error' in response:
                logger.error(f"MCP error from {server_name}.{tool_name}: {response['error']}")
            elif response.get('id') != request_id:
                logger.warning(f"Mismatched response ID from {server_name}.{tool_name}")
                
            return response
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from {server_name}.{tool_name}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"Error calling {server_name}.{tool_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}

    async def discover_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Discover tools provided by an MCP server.
        
        Args:
            server_name: Name of the MCP server
            
        Returns:
            List of available tools and their schemas
        """
        if server_name in self.available_tools:
            return self.available_tools[server_name]
            
        await self.discover_server_tools(server_name)
        return self.available_tools.get(server_name, [])

    async def stop_all_servers(self) -> None:
        """Stop all running MCP servers."""
        for server_name in list(self.processes.keys()):
            await self.stop_server(server_name)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_all_servers()


# Global MCP client instance that auto-discovers servers
mcp_client = MCPClient()

# Example usage:
if __name__ == "__main__":
    async def main():
        async with MCPClient() as client:
            print("\nAvailable MCP Servers:")
            for server_name in client.servers:
                print(f"- {server_name}")
                
            print("\nAvailable Tools:")
            for server_name, tools in client.get_available_tools().items():
                print(f"\n{server_name}:")
                for tool in tools:
                    print(f"  - {tool.get('name')}: {tool.get('description', 'No description')}"
                          f" (params: {', '.join(tool.get('parameters', {}).get('properties', {}).keys())})")
            
            # Example: Find a specific tool across all servers
            # print("\nSearching for 'send_email' tool:")
            # email_tools = client.find_tool('send_email')
            # pprint.pprint(email_tools)
            
            # Example: Call a tool
            # result = await client.call_tool("microsoft-365", "mcp.discover", {})
            # print("\nMicrosoft 365 MCP tools:")
            # pprint.pprint(result)
    
    asyncio.run(main())
