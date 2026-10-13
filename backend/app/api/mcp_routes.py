import asyncio
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.mcp import mcp_client

router = APIRouter()


class ToolExecutionRequest(BaseModel):
    server: str
    tool: str
    params: Dict[str, Any] = {}


@router.get("/servers")
async def get_mcp_servers() -> List[Dict[str, Any]]:
    """Get all available MCP servers and their tools"""
    try:
        servers = []

        # Get all server names
        for server_name in mcp_client.servers.keys():
            tools = []

            # Get tools for this server
            try:
                server_tools = await mcp_client.get_server_tools(server_name)
                for tool_name, tool_info in server_tools.items():
                    tools.append(
                        {
                            "name": tool_name,
                            "description": tool_info.get("description", ""),
                            "parameters": tool_info.get("parameters", {}),
                        }
                    )
            except Exception as e:
                print(f"Error getting tools for {server_name}: {str(e)}")
                continue

            servers.append({"name": server_name, "tools": tools, "status": "connected" if tools else "error"})

        return servers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting MCP servers: {str(e)}")


@router.post("/execute")
async def execute_tool(request: ToolExecutionRequest) -> Dict[str, Any]:
    """Execute a tool on an MCP server"""
    try:
        if request.server not in mcp_client.servers:
            raise HTTPException(status_code=404, detail=f"Server '{request.server}' not found")

        # Execute the tool with timeout
        try:
            result = await asyncio.wait_for(
                mcp_client.call_tool(request.server, request.tool, request.params),
                timeout=30,  # 30 second timeout
            )
            return {"status": "success", "result": result}

        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Tool execution timed out")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool: {str(e)}")


@router.get("/status")
async def get_mcp_status() -> Dict[str, Any]:
    """Get status of all MCP servers"""
    status = {"total_servers": len(mcp_client.servers), "connected_servers": 0, "servers": []}

    for server_name in mcp_client.servers:
        try:
            tools = await mcp_client.get_server_tools(server_name)
            status["servers"].append(
                {"name": server_name, "status": "connected", "tools_count": len(tools) if tools else 0}
            )
            status["connected_servers"] += 1
        except Exception:
            status["servers"].append({"name": server_name, "status": "error", "tools_count": 0})

    return status
