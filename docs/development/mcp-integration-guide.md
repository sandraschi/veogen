# MCP Integration Guide: Adding New Servers

## Overview

This guide explains how to add new MCP (Model Context Protocol) integrations to your VeoGen project. You already have an excellent foundation with servers for filesystem, databases, web automation, and media generation.

## Your Current MCP Setup

Based on your `mcp.json`, you currently have:

### **Media & Generation**
- `veogen-media` - Custom media server
- `genmedia-studio` - Google AI generation
- `everart` - Image generation

### **Development Tools**
- `filesystem` - File system access
- `shell` - Command execution
- `docker` - Docker management
- `kubernetes` - K8s management

### **Databases**
- `postgres` - PostgreSQL access
- `sqlite` - SQLite access
- `memory` - Persistent memory

### **Web & Search**
- `playwright` - Web automation
- `puppeteer` - Browser control
- `brave-search` - Web search
- `fetch` - HTTP requests

### **Cloud Platforms**
- `aws` - Amazon Web Services
- `azure` - Microsoft Azure
- `github` - GitHub integration
- `google-drive` - Google Drive
- `google-maps` - Google Maps

### **Utilities**
- `time` - Time/date functions
- `sequential-thinking` - Advanced reasoning

## Adding New MCP Integrations

### **Method 1: Official NPX Packages**

Most MCP servers can be added using the `npx` method:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "API_KEY": "${YOUR_API_KEY}"
      }
    }
  }
}
```

### **Method 2: Custom/Third-Party Servers**

For specialized servers like Blender:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "BLENDER_PATH": "C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"
      }
    }
  }
}
```

### **Method 3: Local Development Servers**

```json
{
  "mcpServers": {
    "custom-server": {
      "command": "python",
      "args": ["path/to/your/server.py"],
      "cwd": "/path/to/server/directory",
      "env": {
        "DEBUG": "true"
      }
    }
  }
}
```

## Specific Integration Examples

### **1. Blender MCP Integration** 🎨

**Installation:**
```bash
# Install UV package manager first
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Add to mcp.json:**
```json
{
  "blender": {
    "command": "cmd",
    "args": ["/c", "uvx", "blender-mcp"],
    "env": {
      "BLENDER_PATH": "C:/Program Files/Blender Foundation/Blender 4.0/blender.exe",
      "BLENDER_SCRIPTS_PATH": "C:/Users/sandr/AppData/Roaming/Blender/4.0/scripts"
    }
  }
}
```

**Capabilities:**
- Create 3D objects and scenes
- Modify materials and textures
- Render images and animations
- Export models to various formats
- Script complex 3D workflows

### **2. Microsoft Office 365 MCP** 📊

```json
{
  "microsoft-365": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-microsoft365"],
    "env": {
      "MICROSOFT_CLIENT_ID": "${MS_CLIENT_ID}",
      "MICROSOFT_CLIENT_SECRET": "${MS_CLIENT_SECRET}",
      "MICROSOFT_TENANT_ID": "${MS_TENANT_ID}"
    }
  }
}
```

### **3. Microsoft Teams MCP** 💬

```json
{
  "microsoft-teams": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-teams"],
    "env": {
      "TEAMS_WEBHOOK_URL": "${TEAMS_WEBHOOK}",
      "TEAMS_BOT_TOKEN": "${TEAMS_BOT_TOKEN}"
    }
  }
}
```

### **4. SharePoint MCP** 📁

```json
{
  "sharepoint": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sharepoint"],
    "env": {
      "SHAREPOINT_SITE_URL": "${SHAREPOINT_URL}",
      "SHAREPOINT_CLIENT_ID": "${SP_CLIENT_ID}",
      "SHAREPOINT_CLIENT_SECRET": "${SP_CLIENT_SECRET}"
    }
  }
}
```

### **5. Power BI MCP** 📈

```json
{
  "powerbi": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-powerbi"],
    "env": {
      "POWERBI_CLIENT_ID": "${PBI_CLIENT_ID}",
      "POWERBI_CLIENT_SECRET": "${PBI_CLIENT_SECRET}",
      "POWERBI_TENANT_ID": "${PBI_TENANT_ID}"
    }
  }
}
```

### **6. Outlook MCP** 📧

```json
{
  "outlook": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-outlook"],
    "env": {
      "OUTLOOK_CLIENT_ID": "${OUTLOOK_CLIENT_ID}",
      "OUTLOOK_CLIENT_SECRET": "${OUTLOOK_CLIENT_SECRET}"
    }
  }
}
```

### **7. Slack MCP** 💬

```json
{
  "slack": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-slack"],
    "env": {
      "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
      "SLACK_USER_TOKEN": "${SLACK_USER_TOKEN}"
    }
  }
}
```

### **8. Notion MCP** 📝

```json
{
  "notion": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-notion"],
    "env": {
      "NOTION_API_KEY": "${NOTION_API_KEY}"
    }
  }
}
```

### **9. Jira MCP** 🎟️

```json
{
  "jira": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-jira"],
    "env": {
      "JIRA_URL": "${JIRA_URL}",
      "JIRA_USERNAME": "${JIRA_USERNAME}",
      "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
    }
  }
}
```

### **10. Discord MCP** 🎮

```json
{
  "discord": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-discord"],
    "env": {
      "DISCORD_BOT_TOKEN": "${DISCORD_BOT_TOKEN}",
      "DISCORD_CLIENT_ID": "${DISCORD_CLIENT_ID}"
    }
  }
}
```

## Advanced Integrations

### **QoS Monitoring with Grafana** 📊

```json
{
  "grafana": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-grafana"],
    "env": {
      "GRAFANA_URL": "http://localhost:3000",
      "GRAFANA_API_KEY": "${GRAFANA_API_KEY}"
    }
  }
}
```

### **Prometheus Metrics** 📈

```json
{
  "prometheus": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-prometheus"],
    "env": {
      "PROMETHEUS_URL": "http://localhost:9090"
    }
  }
}
```

### **Elasticsearch/OpenSearch** 🔍

```json
{
  "elasticsearch": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-elasticsearch"],
    "env": {
      "ELASTICSEARCH_URL": "http://localhost:9200",
      "ELASTICSEARCH_USERNAME": "${ES_USERNAME}",
      "ELASTICSEARCH_PASSWORD": "${ES_PASSWORD}"
    }
  }
}
```

### **Kafka Integration** 📡

```json
{
  "kafka": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-kafka"],
    "env": {
      "KAFKA_BROKERS": "localhost:9092",
      "KAFKA_CLIENT_ID": "mcp-client"
    }
  }
}
```

## Custom Server Development

### **Creating Your Own MCP Server**

**1. Python Example:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("VeoGen-Custom")

@mcp.tool()
def custom_veogen_function(param: str) -> str:
    """Custom VeoGen functionality"""
    return f"Processing: {param}"

if __name__ == "__main__":
    mcp.run()
```

**2. TypeScript Example:**
```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

const server = new Server({
  name: 'veogen-custom',
  version: '1.0.0'
});

server.addTool({
  name: 'custom_tool',
  description: 'Custom VeoGen tool',
  inputSchema: {
    type: 'object',
    properties: {
      input: { type: 'string' }
    }
  }
});
```

## Environment Variables Management

### **Recommended .env Structure:**

```bash
# Microsoft Integrations
MS_CLIENT_ID=your_microsoft_client_id
MS_CLIENT_SECRET=your_microsoft_client_secret
MS_TENANT_ID=your_microsoft_tenant_id

# Blender Integration
BLENDER_PATH=C:/Program Files/Blender Foundation/Blender 4.0/blender.exe

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_USER_TOKEN=xoxp-your-slack-user-token

# Notion Integration
NOTION_API_KEY=secret_your_notion_api_key

# Grafana Integration
GRAFANA_API_KEY=your_grafana_api_key

# GitHub (if not already set)
GITHUB_TOKEN=ghp_your_github_token

# Google Services (if not already set)
GDRIVE_CLIENT_ID=your_google_drive_client_id
GDRIVE_CLIENT_SECRET=your_google_drive_client_secret
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# EverArt (if not already set)
EVERART_API_KEY=your_everart_api_key

# Brave Search (if not already set)
BRAVE_API_KEY=your_brave_search_api_key
```

## Testing MCP Integrations

### **1. MCP Inspector Tool**
```bash
npx @modelcontextprotocol/inspector mcp.json
```

### **2. Manual Testing with Cursor**
1. Add server to `mcp.json`
2. Restart Cursor
3. Test with AI: "Use the [server-name] to [perform action]"

### **3. Claude Desktop Testing**
1. Add server to Claude Desktop MCP config
2. Restart Claude Desktop
3. Test functionality in chat

## Troubleshooting Common Issues

### **Server Not Starting**
```bash
# Check if command exists
npx @modelcontextprotocol/server-name --help

# Check environment variables
echo $API_KEY

# Test manual connection
node path/to/server.js
```

### **Authentication Issues**
- Verify API keys are correct
- Check token permissions
- Ensure environment variables are loaded

### **Performance Issues**
- Monitor server resource usage
- Implement connection pooling
- Add timeout configurations

## Best Practices

### **1. Security**
- Store sensitive keys in environment variables
- Use least-privilege access tokens
- Regularly rotate API keys
- Monitor access logs

### **2. Performance**
- Group related servers together
- Implement caching where appropriate
- Set reasonable timeouts
- Monitor server health

### **3. Maintenance**
- Keep servers updated
- Document custom configurations
- Test after updates
- Monitor for deprecated APIs

## Your Updated MCP Configuration

Here's how to add some key integrations to your existing setup:

```json
{
  "mcpServers": {
    // ... your existing servers ...
    
    "blender": {
      "command": "cmd",
      "args": ["/c", "uvx", "blender-mcp"],
      "env": {
        "BLENDER_PATH": "C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"
      }
    },
    "microsoft-365": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-microsoft365"],
      "env": {
        "MICROSOFT_CLIENT_ID": "${MS_CLIENT_ID}",
        "MICROSOFT_CLIENT_SECRET": "${MS_CLIENT_SECRET}",
        "MICROSOFT_TENANT_ID": "${MS_TENANT_ID}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
      }
    },
    "notion": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-notion"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    },
    "grafana": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-grafana"],
      "env": {
        "GRAFANA_URL": "http://localhost:3000",
        "GRAFANA_API_KEY": "${GRAFANA_API_KEY}"
      }
    }
  }
}
```

## MCP Registry and Discovery

The MCP ecosystem is rapidly growing. Check these resources for new servers:
- [MCP Official Registry](https://modelcontextprotocol.io/servers)
- [GitHub MCP Topic](https://github.com/topics/mcp)
- [Community MCP Servers](https://github.com/modelcontextprotocol)

## MCP Server Verification & Cleanup 🔍

### **How to Identify Bogus MCP Servers**

Before adding any MCP server, **ALWAYS** verify its legitimacy:

#### **✅ LEGITIMATE Sources:**
1. **Official MCP Servers**: `@modelcontextprotocol/server-*` (verified on NPM)
2. **Custom/Local Servers**: Your own servers or from trusted sources
3. **Documented Third-Party**: Well-documented servers with active repositories

#### **❌ BOGUS Server Warning Signs:**
- Generic names like `mcp-server`, `mcp-teams`, `mcp-onenote` (without official namespace)
- Abandoned repositories with no recent commits
- Missing or poor documentation
- No official backing from Microsoft, Google, etc.
- Suspiciously broad claims ("supports everything")

### **Current Official MCP Servers (Verified 2025)**

Based on NPM registry verification, these are legitimate:

```bash
# Core Functionality
@modelcontextprotocol/server-filesystem
@modelcontextprotocol/server-memory
@modelcontextprotocol/server-fetch
@modelcontextprotocol/server-shell
@modelcontextprotocol/server-time

# Databases
@modelcontextprotocol/server-postgres
@modelcontextprotocol/server-sqlite

# Web Automation  
@modelcontextprotocol/server-playwright
@modelcontextprotocol/server-puppeteer

# Search & APIs
@modelcontextprotocol/server-brave-search
@modelcontextprotocol/server-github

# Cloud Platforms
@modelcontextprotocol/server-aws
@modelcontextprotocol/server-azure
@modelcontextprotocol/server-docker
@modelcontextprotocol/server-kubernetes

# Google Services
@modelcontextprotocol/server-gdrive
@modelcontextprotocol/server-google-maps

# Media & Generation
@modelcontextprotocol/server-everart
@modelcontextprotocol/server-sequential-thinking
```

### **❌ Known Bogus Servers to Avoid:**

```bash
# These DO NOT exist or are abandoned:
mcp-server-teams          # No official Microsoft MCP server yet
mcp-server-onenote        # No official Microsoft MCP server yet  
mcp-server-sharepoint     # No official Microsoft MCP server yet
mcp-server                # Generic, often abandoned/fishy
mcp-teams                 # Not from official source
mcp-office365             # Not from official source
```

### **MCP Server Verification Tool**

Create this script to verify your MCP servers:

```bash
# verify-mcp-servers.ps1
function Test-MCPServer {
    param(
        [string]$ServerName,
        [string]$Package
    )
    
    Write-Host "Verifying: $ServerName" -ForegroundColor Yellow
    
    if ($Package.StartsWith("@modelcontextprotocol/")) {
        $result = npm view $Package --json 2>$null | ConvertFrom-Json
        if ($result) {
            Write-Host "  ✅ Official MCP server - VERIFIED" -ForegroundColor Green
            Write-Host "  📦 Latest version: $($result.version)" -ForegroundColor Cyan
            return $true
        } else {
            Write-Host "  ❌ Package not found on NPM!" -ForegroundColor Red
            return $false
        }
    } elseif ($Package -eq "node" -or $Package -eq "python" -or $Package -eq "uvx") {
        Write-Host "  📝 Custom/Local server - Manual verification needed" -ForegroundColor Blue
        return $true
    } else {
        Write-Host "  ⚠️  Third-party server - Please verify manually" -ForegroundColor Magenta
        return $true
    }
}

# Read and verify mcp.json
if (Test-Path "mcp.json") {
    $mcpConfig = Get-Content "mcp.json" | ConvertFrom-Json
    
    Write-Host "`n🔍 MCP Server Verification Report" -ForegroundColor White -BackgroundColor DarkBlue
    Write-Host "=================================" -ForegroundColor White -BackgroundColor DarkBlue
    
    $verified = 0
    $total = 0
    
    foreach ($server in $mcpConfig.mcpServers.PSObject.Properties) {
        $total++
        $serverName = $server.Name
        $command = $server.Value.command
        
        if ($command -eq "npx" -and $server.Value.args[1]) {
            $package = $server.Value.args[1]
        } else {
            $package = $command
        }
        
        if (Test-MCPServer -ServerName $serverName -Package $package) {
            $verified++
        }
    }
    
    Write-Host "`n📊 Summary: $verified/$total servers verified" -ForegroundColor White
    
    if ($verified -eq $total) {
        Write-Host "🎉 All servers look good!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some servers need attention" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ mcp.json not found!" -ForegroundColor Red
}
```

### **Your Current MCP Setup Status** ✅

Your `mcp.json` is actually **EXCELLENT**! All servers are legitimate:

```json
{
  "mcpServers": {
    // ✅ Your custom servers - GOOD
    "veogen-media": { /* custom */ },
    "genmedia-studio": { /* custom */ },
    
    // ✅ All official @modelcontextprotocol/ servers - VERIFIED
    "filesystem": "@modelcontextprotocol/server-filesystem",
    "playwright": "@modelcontextprotocol/server-playwright", 
    "puppeteer": "@modelcontextprotocol/server-puppeteer",
    "brave-search": "@modelcontextprotocol/server-brave-search",
    "github": "@modelcontextprotocol/server-github",
    "postgres": "@modelcontextprotocol/server-postgres",
    "sqlite": "@modelcontextprotocol/server-sqlite",
    "google-drive": "@modelcontextprotocol/server-gdrive",
    "google-maps": "@modelcontextprotocol/server-google-maps",
    "memory": "@modelcontextprotocol/server-memory",
    "time": "@modelcontextprotocol/server-time",
    "everart": "@modelcontextprotocol/server-everart",
    "fetch": "@modelcontextprotocol/server-fetch",
    "shell": "@modelcontextprotocol/server-shell",
    "docker": "@modelcontextprotocol/server-docker",
    "kubernetes": "@modelcontextprotocol/server-kubernetes",
    "aws": "@modelcontextprotocol/server-aws",
    "azure": "@modelcontextprotocol/server-azure",
    "sequential-thinking": "@modelcontextprotocol/server-sequential-thinking"
  }
}
```

**No cleanup needed** - you already removed the bogus ones! 🎉

---

Your MCP setup is already impressive! Adding Blender and Microsoft tools will make it even more powerful for creative and productivity workflows. 