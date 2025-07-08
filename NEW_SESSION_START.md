# 🚀 VeoGen - New Claude Session Quick Start

## 🎯 For New Claude Sessions

When you run out of context or start a new chat, use this guide to quickly get back up to speed on the VeoGen project.

## ⚡ Ultra-Quick Start (30 seconds)

### Step 0: Read Developer Rulebook
```bash
# ALWAYS read this first in new Claude sessions
read_file("CLAUDE_DEV_RULEBOOK.md")
```

### Step 1: Run the Onboarding Script
```bash
# Navigate to project and run quick assessment
cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"
python claude_onboard.py
```

### Step 2: Read the Context
```bash
# In Claude, run these commands:
read_file("CLAUDE_RESTART_GUIDE.md")
read_file("AUTHENTICATION_SUCCESS.md")
```

### Step 3: Verify System Health
```bash
# In Claude, run:
execute_command("python test_final_auth.py", 30000)
```

## 📋 What You'll Find

### ✅ Project Status (July 2025)
- **Authentication**: ✅ FULLY FUNCTIONAL
- **Frontend**: ✅ React app on port 4710
- **Backend**: ✅ FastAPI on port 4700
- **Database**: ✅ PostgreSQL working
- **Monitoring**: ✅ Full Grafana/Prometheus stack
- **Docker**: ✅ All services healthy

### 🧪 Test Credentials
- **URL**: http://localhost:4710
- **Email**: `valid@test.com`
- **Password**: `Test123!`

### 📚 Key Documentation Files
- `CLAUDE_RESTART_GUIDE.md` - Complete restart instructions
- `AUTHENTICATION_SUCCESS.md` - Recent work summary
- `AUTH_FIX_SUMMARY.md` - Technical fixes applied
- `claude_onboard.py` - Quick health check script
- `test_final_auth.py` - Authentication system tester

## 🔧 If Services Are Down

```bash
# Start the stack
docker-compose up -d

# Wait for services to start
sleep 30

# Verify health
python claude_onboard.py
```

## 🧰 Available Tools

### MCP Servers Ready
- **Desktop Commander**: File operations, Docker management  
- **Basic Memory**: Knowledge management
- **Blender**: 3D modeling (if needed)
- **Playwright**: Browser automation (requires restart)

### Common Commands
```bash
# File operations
read_file("path/to/file")
list_directory("path/to/dir")
search_code("pattern", "path")

# Docker management
execute_command("docker-compose ps", 10000)
execute_command("docker-compose logs backend", 10000)

# Testing
execute_command("python test_final_auth.py", 30000)
execute_command("python claude_onboard.py", 30000)
```

## 🎯 Current State Summary

**VeoGen is a production-ready AI video generation platform** with:
- ✅ Complete user authentication system (login, registration, JWT)
- ✅ User management (profiles, settings, API keys)
- ✅ Video generation capabilities with Google Veo AI
- ✅ Movie Maker with AI script generation
- ✅ Enterprise monitoring stack (Grafana, Prometheus, Loki)
- ✅ Docker containerized deployment
- ✅ Full API documentation

**Recent Major Work**: Fixed authentication system completely - all login/logout flows working perfectly.

**Previous Session**: User promised a beer for browser automation demo (Playwright installed, needs restart).

## 🍺 Beer Status
Authentication system fully fixed! User owes Claude a beer for the successful fix. Playwright browser automation is installed and ready for demo after restart.

---

**⚡ Quick Commands for New Claude:**
```bash
# Essential commands to run first
read_file("CLAUDE_DEV_RULEBOOK.md")      # ALWAYS FIRST!
read_file("CLAUDE_RESTART_GUIDE.md")
execute_command("python claude_onboard.py", 30000)
execute_command("python test_final_auth.py", 30000)
```

**🚀 VeoGen is ready to rock!**
