# 🚀 QuantGeekDev Docker MCP Server Installation

## 📋 Overview
QuantGeekDev's Docker MCP server provides powerful Docker container and Compose stack management through Claude AI.

## ✨ Features
- 🚀 Create standalone Docker containers
- 📦 Deploy Docker Compose stacks  
- 🔍 Retrieve container logs
- 📊 List all containers and their status
- 🔧 Manage images, volumes, and networks

## 📦 Installation Methods

### Method 1: Direct uvx Installation (Recommended)
```powershell
# Install via uvx (easier, no cloning needed)
uvx install docker-mcp
```

### Method 2: Local Installation
```powershell
# Clone repository
git clone https://github.com/QuantGeekDev/docker-mcp.git
cd docker-mcp

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Claude Configuration

### For uvx installation:
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

### For local installation:
```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\sandr\\AppData\\Local\\AnthropicClaude\\app-0.11.6\\veogen\\mcp-servers\\docker-mcp",
        "run",
        "docker-mcp"
      ]
    }
  }
}
```

## 🎯 VeoGen Integration Benefits

This MCP server will give you much more powerful Docker management for your VeoGen infrastructure:

### Current VeoGen Stack Management
- **Frontend (React)**: Port 4710
- **Backend (FastAPI)**: Port 4700  
- **Database (PostgreSQL)**: Port 4715
- **Monitoring Stack**: Grafana/Prometheus setup

### New Capabilities with Docker MCP
- **Natural language container management**: "Show me VeoGen container status"
- **Compose stack operations**: "Restart the VeoGen backend service"
- **Log analysis**: "Get logs from veogen-backend-1"
- **Resource monitoring**: "List all VeoGen containers with their resource usage"

## 🧪 Test Commands
Once installed, you can test with:
- "List all running Docker containers"
- "Show logs for veogen-backend-1"
- "Get status of VeoGen docker-compose stack"

## 🔒 Requirements
- Docker Desktop or Docker Engine installed
- Python 3.8+ 
- uvx package manager

## 📍 Configuration Location
Claude Desktop config file location:
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

## 🎯 Ready for Installation
This MCP server is perfect for your VeoGen project's sophisticated Docker setup!
