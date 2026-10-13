# VeoGen MCP Servers Installation Guide

## Quick Installation for Claude

### 1. Log Viewer MCP Server

Add to your Claude MCP configuration:

```json
{
  "mcpServers": {
    "veogen-log-viewer": {
      "command": "node",
      "args": ["C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/tools/log-viewer-mcp/dist/index.js"]
    }
  }
}
```

### 2. User Manager MCP Server

Add to your Claude MCP configuration:

```json
{
  "mcpServers": {
    "veogen-user-manager": {
      "command": "node",
      "args": ["C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/tools/user-manager-mcp/dist/index.js"]
    }
  }
}
```

### 3. Combined Configuration

```json
{
  "mcpServers": {
    "veogen-log-viewer": {
      "command": "node",
      "args": ["C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/tools/log-viewer-mcp/dist/index.js"]
    },
    "veogen-user-manager": {
      "command": "node",
      "args": ["C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/tools/user-manager-mcp/dist/index.js"]
    }
  }
}
```

## Environment Variables (Optional)

Set these environment variables for custom configuration:

### Log Viewer MCP
```bash
VEOGEN_LOG_PATHS=./logs,/var/logs/veogen
VEOGEN_DOCKER_ENABLED=true
MAX_LOG_LINES=1000
```

### User Manager MCP
```bash
VEOGEN_DB_HOST=localhost
VEOGEN_DB_PORT=4715
VEOGEN_DB_NAME=veogen
VEOGEN_DB_USER=veogen
VEOGEN_DB_PASSWORD=veogen123
```

## Testing the MCP Servers

### Test Commands for Claude:

**Log Viewer:**
- "Debug VeoGen system health"
- "Show me recent error logs"
- "Search logs for authentication issues"
- "Get log statistics for the last 24 hours"

**User Manager:**
- "List all users"
- "Search for users with email containing @test.com"
- "Get user statistics"
- "Show me details for user sandraschipal@hotmail.com"

## Manual Testing

### Test Log Viewer MCP:
```bash
cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\tools\log-viewer-mcp"
echo '{"method": "tools/list"}' | node dist/index.js
```

### Test User Manager MCP:
```bash
cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\tools\user-manager-mcp"
echo '{"method": "tools/list"}' | node dist/index.js
```

## Prerequisites

1. VeoGen main system must be running (docker-compose up)
2. PostgreSQL database accessible on port 4715
3. Node.js installed and available in PATH
4. MCP servers built successfully (npm run build)

## Troubleshooting

### Common Issues:

1. **Database Connection Failed**
   - Check VeoGen PostgreSQL is running on port 4715
   - Verify credentials (veogen/veogen123)

2. **Docker Commands Not Found**
   - Log viewer requires Docker to be accessible via command line
   - Check Docker is installed and in PATH

3. **Permission Errors**
   - Ensure Claude has permission to execute Node.js
   - Check file permissions on MCP server files

### Debug Mode:

Add this to your environment for detailed logging:
```bash
NODE_ENV=development
DEBUG=*
```