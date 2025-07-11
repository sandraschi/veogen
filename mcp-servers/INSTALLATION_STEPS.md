# 🚀 QuantGeekDev Docker MCP Installation Instructions

## 📋 Step-by-Step Installation

### Method 1: Direct uvx Installation (Easiest)

**Step 1**: Open PowerShell as Administrator
```powershell
# Open PowerShell and run:
uvx install docker-mcp
```

**Step 2**: If uvx is not installed, install it first:
```powershell
# Install uv/uvx first
pip install uv
```

Then try again:
```powershell
uvx install docker-mcp
```

### Method 2: Run the Prepared Installation Script

**Step 1**: Open PowerShell as Administrator

**Step 2**: Navigate to the script location:
```powershell
cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\mcp-servers"
```

**Step 3**: Run the installation script:
```powershell
.\install-docker-mcp.ps1
```

### Method 3: Manual Git Clone Installation

**Step 1**: Clone the repository:
```powershell
cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\mcp-servers"
git clone https://github.com/QuantGeekDev/docker-mcp.git
cd docker-mcp
```

**Step 2**: Install dependencies:
```powershell
pip install -r requirements.txt
```

## 🔧 Claude Configuration

After successful installation, add this to your Claude config:

**For uvx installation** (Method 1):
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

**For local installation** (Method 2/3):
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

## 📍 Configuration File Location
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## 🧪 Test Commands
After restarting Claude, try:
- "List all Docker containers"
- "Show me VeoGen container status"
- "Get logs from veogen-backend-1"

## 🎯 Ready to Execute!
Choose your preferred method and run the commands above in PowerShell!
