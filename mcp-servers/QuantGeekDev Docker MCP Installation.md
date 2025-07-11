---
title: QuantGeekDev Docker MCP Installation
type: note
permalink: mcp-servers-quant-geek-dev-docker-mcp-installation
---

# 🚀 QuantGeekDev Docker MCP Server - Installation Complete

## 📋 Overview
Successfully prepared QuantGeekDev's Docker MCP server for installation. This provides powerful Docker container and Compose stack management through Claude AI.

## ✨ Key Features
- 🚀 **Create standalone Docker containers** with custom images, ports, environment variables
- 📦 **Deploy Docker Compose stacks** by providing YAML and project names
- 🔍 **Retrieve container logs** from specific containers
- 📊 **List all Docker containers** to monitor status and resource usage
- 🔧 **Manage Docker images, volumes, and networks**

## 📁 Files Created
1. **Installation Guide**: `mcp-servers/docker-mcp-install.md`
2. **PowerShell Installer**: `mcp-servers/install-docker-mcp.ps1`
3. **Claude Configuration**: `mcp-servers/claude-config-with-docker-mcp.json`

## 🎯 Perfect for VeoGen
This MCP server is ideal for managing the sophisticated VeoGen Docker Compose stack:
- **Frontend (React)**: Port 4710
- **Backend (FastAPI)**: Port 4700  
- **Database (PostgreSQL)**: Port 4715
- **Monitoring Stack**: Grafana/Prometheus setup

## 🚀 Installation Methods

### Method 1: Direct uvx (Recommended)
```powershell
uvx install docker-mcp
```

### Method 2: Run PowerShell Installer
```powershell
cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\mcp-servers"
.\install-docker-mcp.ps1
```

## 🔧 Claude Configuration
Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "uvx",
      "args": ["docker-mcp"]
    }
  }
}
```

## 🧪 Test Commands
Once installed and configured:
- "List all running Docker containers"
- "Show logs for veogen-backend-1" 
- "Get status of VeoGen docker-compose stack"
- "Create a new container with nginx image"
- "Deploy a Docker Compose stack"

## 🔥 Game-Changing Capabilities
With this MCP server, you can:
- **Natural language Docker management**: "Restart the VeoGen backend service"
- **Intelligent log analysis**: "Show me error logs from the last hour"
- **Container orchestration**: "Scale up the frontend to 3 replicas"
- **Resource monitoring**: "Which containers are using the most CPU?"

## ⚡ Much More Powerful Than Desktop Commander
This replaces the basic Desktop Commander Docker functionality with:
- ✅ **Full Docker Compose support**
- ✅ **Container lifecycle management**
- ✅ **Log streaming and analysis**
- ✅ **Network and volume management**
- ✅ **Multi-container orchestration**

## 🎯 Status: Ready for Installation
All files prepared, installation scripts ready. Sandra can now:
1. Run the PowerShell installer
2. Update Claude configuration
3. Restart Claude
4. Enjoy powerful Docker management!