# MCP Integration for VeoGen

This document outlines the MCP (Model Control Protocol) integration for VeoGen, following FastMCP 2.11.3 standards.

## Overview

VeoGen uses MCP to communicate with external services like Office 365 and local LLMs. The MCP client handles communication with these services through a standardized protocol.

## Configuration

Edit `mcp_config.json` to configure MCP servers. Example:

```json
{
  "servers": {
    "office365-mcp": {
      "command": "node",
      "args": ["path/to/office365-mcp/dist/index.js"],
      "env": {
        "OFFICE365_CLIENT_ID": "your-client-id",
        "OFFICE365_TENANT_ID": "your-tenant-id"
      }
    }
  }
}
```

## Using the MCP Client

```python
from app.services.mcp import mcp_client

# Call a tool
result = await mcp_client.call_tool(
    "office365-mcp", 
    "send_email", 
    {"to": "user@example.com", "subject": "Test", "body": "Hello"}
)

# Discover available tools
tools = await mcp_client.discover_tools("office365-mcp")
```

## Email Service

```python
from app.services.mcp.email_service import mcp_email_service

# Send an email
result = await mcp_email_service.send_email(
    to="user@example.com",
    subject="Test Email",
    body="This is a test email",
    html="<p>This is a <strong>test</strong> email</p>"
)
```

## Development

1. Install dependencies:
   ```bash
   pip install aiofiles
   ```

2. Run tests:
   ```bash
   python -m pytest tests/mcp/
   ```

## Security

- Store sensitive data in environment variables
- Use HTTPS for all external connections
- Regularly update MCP server implementations
