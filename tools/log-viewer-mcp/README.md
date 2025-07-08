# 📊 VeoGen Log Viewer MCP

[![npm version](https://badge.fury.io/js/%40veogen%2Flog-viewer-mcp.svg)](https://badge.fury.io/js/%40veogen%2Flog-viewer-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Model Context Protocol (MCP) server that provides natural language access to VeoGen's logging system. Debug your applications using conversational AI instead of complex command-line tools.

## 🎯 **What This Does**

Transform this complex debugging workflow:
```bash
# Old way - multiple commands, manual parsing
curl "http://localhost:8200/api/logs/read/backend/app.log?level=ERROR&lines=50" | jq
grep -r "database" /var/logs/veogen/ | tail -20
docker logs veogen-backend-1 --tail 100 | grep WARNING
```

Into this simple conversation:
```
💬 "Show me the last 20 database errors from today"
💬 "What's causing the authentication failures?"  
💬 "Are there any performance issues in the backend logs?"
💬 "Summarize all warnings from the last hour"
```
## 🚀 **Features**

### 🔍 **Intelligent Log Analysis**
- **Natural language queries** - Ask questions in plain English
- **Multi-source aggregation** - Combine logs from files, Docker, system logs
- **Smart filtering** - Automatic relevance ranking and deduplication
- **Context awareness** - Remembers previous queries and builds on them

### 📊 **Advanced Log Operations**
- **Real-time tailing** - Monitor logs as they update
- **Pattern recognition** - Automatically detect common error patterns
- **Time-based filtering** - "Show errors from the last 30 minutes"
- **Cross-reference analysis** - Connect related log entries across services

### 🎛️ **VeoGen Integration**
- **Service-aware** - Understands VeoGen's architecture (backend, frontend, database)
- **Error categorization** - Groups errors by type (auth, database, API, etc.)
- **Performance metrics** - Extracts timing and performance data
- **Health monitoring** - Quick system health checks

## 📦 **Installation**

### Method 1: NPM (Recommended)
```bash
npm install -g @veogen/log-viewer-mcp
```

### Method 2: From Source
```bash
git clone https://github.com/veogen/veogen.git
cd veogen/tools/log-viewer-mcp
npm install
npm run build
npm link
```

## ⚙️ **Configuration**

### Add to Claude Desktop

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "veogen-log-viewer": {
      "command": "veogen-log-viewer-mcp",
      "args": [],
      "env": {
        "VEOGEN_LOG_PATHS": "/path/to/veogen/logs,/var/logs/veogen",
        "VEOGEN_DOCKER_ENABLED": "true",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```
