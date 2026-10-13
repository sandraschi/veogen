# 🔧 Correct Docker MCP Configuration - PRESERVE ALL SERVERS

## ⚠️ IMPORTANT: Only ADD, Don't Replace!

Your current MCP servers that MUST be preserved:
- ✅ **basic-memory**: Working project memory
- ✅ **ImmichMCP**: Photo management (local compiled)  
- ✅ **CalibreMCP**: Ebook management (local compiled)
- ✅ **microsoft-365**: Office integration
- ✅ **veogen-voice-control**: Voice control system
- ✅ **desktop-commander**: Basic system commands

## 📋 SAFE Configuration Addition

**ONLY ADD this section to your existing mcpServers:**

```json
"docker-mcp": {
  "command": "uvx",
  "args": ["docker-mcp"]
}
```

## 🎯 Your Complete Config Should Look Like:

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "uvx",
      "args": ["basic-memory"],
      "env": {
        "BASIC_MEMORY_PROJECT": "veogen"
      }
    },
    "immich-mcp": {
      "command": "node",
      "args": ["C:\\Users\\sandr\\AppData\\Local\\AnthropicClaude\\app-0.11.6\\ImmichMCP\\dist\\index.js"],
      "env": {
        "IMMICH_API_URL": "http://localhost:2283",
        "IMMICH_API_KEY": "your-immich-api-key"
      }
    },
    "calibre-mcp": {
      "command": "node", 
      "args": ["C:\\Users\\sandr\\AppData\\Local\\AnthropicClaude\\app-0.11.6\\CalibreMCP\\dist\\index.js"],
      "env": {
        "CALIBRE_MODE": "auto"
      }
    },
    "docker-mcp": {
      "command": "uvx",
      "args": ["docker-mcp"]
    },
    "microsoft-365": {
      "command": "uvx",
      "args": ["mcp-server-microsoft365"]
    },
    "veogen-voice-control": {
      "command": "uvx",
      "args": ["veogen-voice-control"]
    },
    "desktop-commander": {
      "command": "uvx",
      "args": ["desktop-commander"]
    }
  }
}
```

## 🚨 CRITICAL STEPS:

1. **BACKUP your current config first!**
2. **Open**: `%APPDATA%\Claude\claude_desktop_config.json`
3. **Find the "mcpServers" section**
4. **ADD ONLY** the docker-mcp entry (with comma if needed)
5. **Save and restart Claude**

## ✅ What You'll Keep:
- All your working MCP servers
- ImmichMCP and CalibreMCP functionality
- Voice control capabilities
- Basic memory project context

## ➕ What You'll Gain:
- Powerful Docker container management
- VeoGen stack control via natural language
- Container log analysis
- Docker Compose orchestration

**Just add the docker-mcp section - DON'T replace everything!** 🎯
