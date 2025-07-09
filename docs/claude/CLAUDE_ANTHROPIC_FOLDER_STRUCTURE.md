# 📁 Complete Claude/Anthropic Folder Structure Documentation

**Created**: July 8, 2025  
**System**: Windows 11 - Sandra's Development Machine  
**Claude Version**: 0.11.6

---

## 🗂️ **Primary Claude Installation Locations**

### 1. 📂 Application Data (Roaming) - User Settings & Config
```
C:\Users\sandr\AppData\Roaming\Claude\
```
**Purpose**: User-specific settings, MCP configuration, preferences
**Persistence**: Survives Claude updates
**Backup Priority**: ⭐⭐⭐ CRITICAL

#### Key Files:
- `claude_desktop_config.json` - **🚨 MOST IMPORTANT** - MCP server configuration
- `config.json` - UI preferences (dark mode, scale, locale)
- `Preferences` - Application preferences (binary format)
- `window-state.json` - Window size/position settings
- `Local State` - Browser engine state
- `lockfile` - Prevents multiple instances

#### Subdirectories:
- `Cache/` - Browser cache data
- `IndexedDB/` - Local database storage
- `Local Storage/` - Web storage data
- `Session Storage/` - Temporary session data
- `logs/` - Application log files
- `GPUCache/` - Graphics cache
- `Code Cache/` - JavaScript compilation cache
- `Crashpad/` - Crash reporting data
- `sentry/` - Error tracking data

---

### 2. 📂 Application Installation (Local) - Program Files & Project Data
```
C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\
```
**Purpose**: Application binaries, your development projects, temporary files
**Persistence**: Gets replaced during Claude updates
**Backup Priority**: ⭐⭐ IMPORTANT (for project data)

#### Core Application Files:
- `claude.exe` - Main Claude executable
- `*.dll` - Application libraries (libEGL.dll, libGLESv2.dll, etc.)
- `*.pak` - Resource packages (chrome_100_percent.pak, resources.pak)
- `icudtl.dat` - Unicode data
- `v8_context_snapshot.bin` - JavaScript engine snapshot
- `LICENSE` - Software license
- `Squirrel-*.log` - Update system logs
- `squirrel.exe` - Update installer

#### Your Development Projects:
- `veogen/` - **🎯 VeoGen Project** - Main video generation platform
- `ImmichMCP/` - **📸 Immich MCP Server** - Photo management integration
- `CalibreMCP/` - **📚 Calibre MCP Server** - Ebook management integration  
- `PlexMCP/` - **🎬 Plex MCP Server** - Media server integration

#### Configuration & Backups:
- `mcp-config.json` - **⚠️ LEGACY** - Old MCP config (not used by Claude)
- `config-backups/` - **🛡️ NEW** - MCP configuration backups
  - `claude_desktop_config_2025-07-08_13-52.json` - Latest working backup
  - `claude_desktop_config_working_2025-07-08_13-51.json` - Previous backup

#### Temporary & Cache:
- `temp/` - Temporary files
- `uploads/` - File upload staging
- `outputs/` - Generated content output

#### Utility Directories:
- `resources/` - Application resources
- `locales/` - Language files
- `NVIDIA Corporation/` - GPU-related data

---

### 3. 📂 Global Claude Installation
```
C:\Users\sandr\AppData\Local\AnthropicClaude\
```
**Purpose**: Update system, global application data
**Persistence**: Survives updates
**Backup Priority**: ⭐ LOW

#### Files:
- `claude.exe` - Global launcher/updater
- `Update.exe` - Squirrel update system
- `app.ico` - Application icon
- `Squirrel-*.log` - Update logs

#### Subdirectories:
- `app-0.11.6/` - Current version (see section 2 above)
- `packages/` - Update packages

---

## 🔧 **Critical Configuration Files Deep Dive**

### 📋 **claude_desktop_config.json** (THE MOST IMPORTANT FILE)
**Location**: `C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json`
**Purpose**: Defines all MCP servers that Claude loads on startup
**Format**: JSON with `mcpServers` object

**Current Server Count**: 26 servers
**Key Servers**:
- `microsoft-365` - Office 365 integration (OneNote, Outlook, Teams)
- `basic-memory` - Persistent knowledge storage
- `desktop-commander` - File system operations
- `blender` - 3D modeling integration
- `playwright-mcp-server` - Browser automation

**Backup Strategy**: Auto-backup before changes, manual backup after successful configs

### 📋 **config.json** (UI Preferences)
**Location**: `C:\Users\sandr\AppData\Roaming\Claude\config.json`
**Purpose**: User interface settings
**Content**: Dark mode, scale factor, locale settings

### 📋 **mcp-config.json** (Legacy - NOT USED)
**Location**: `C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\mcp-config.json`
**Purpose**: Old MCP configuration format (obsolete)
**Status**: Only contains 3 servers (Immich, Calibre, Plex) - not actually used by Claude

---

## 🏗️ **VeoGen Project Structure** (Your Main Project)
```
C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\
```

### Core Components:
- `backend/` - FastAPI Python backend (port 4700)
- `frontend/` - React frontend (port 4710)
- `docker-compose.yml` - Container orchestration
- `CLAUDE_RESTART_GUIDE.md` - **🎯 THIS DOCUMENT'S HOME**

### Documentation Files:
- `README.md` - Project overview
- `AUTHENTICATION_SUCCESS.md` - Auth system documentation
- `AUTH_FIX_SUMMARY.md` - Recent fixes
- `USER_MANAGER_PROGRESS_REPORT.md` - User management tool status

### Utility Scripts:
- `test_final_auth.py` - Authentication testing
- `user_manager_server.py` - Standalone user management tool
- `backup_mcp_config.ps1` - **🛡️ MCP backup script**

---

## 🔌 **MCP Servers Structure**

### 📸 **ImmichMCP** - Photo Management
```
C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\ImmichMCP\
```
- `src/` - TypeScript source code
- `dist/` - Compiled JavaScript (what Claude actually runs)
- `package.json` - NPM configuration
- `tsconfig.json` - TypeScript configuration
- `README.md` - Setup and usage documentation

### 📚 **CalibreMCP** - Ebook Management
```
C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\CalibreMCP\
```
- `src/` - TypeScript source code
- `dist/` - Compiled JavaScript (what Claude actually runs)
- `package.json` - NPM configuration
- **Dual Mode**: Local database + server API support

### 🎬 **PlexMCP** - Media Server
```
C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\PlexMCP\
```
- `src/` - TypeScript source code
- `dist/` - Compiled JavaScript
- `package.json` - NPM configuration

---

## 🛡️ **Backup Strategy & File Importance**

### 🚨 **CRITICAL** (Must backup before any changes)
1. `C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json`
2. `C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\` (entire folder)
3. `C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\*MCP\` (all MCP projects)

### ⚠️ **IMPORTANT** (Backup periodically)
1. `C:\Users\sandr\AppData\Roaming\Claude\config.json`
2. `C:\Users\sandr\AppData\Roaming\Claude\Preferences`
3. Project documentation files

### ℹ️ **OPTIONAL** (Can be regenerated)
1. Cache directories
2. Temporary files
3. Log files
4. `node_modules/` directories

---

## 🔄 **File Lifecycle & Update Behavior**

### **Survives Claude Updates**:
- `AppData\Roaming\Claude\*` - All user settings and MCP config
- Your development projects in `app-0.11.6\`
- Custom documentation and scripts

### **Gets Replaced During Updates**:
- Core application files (*.exe, *.dll, *.pak)
- System resources and locales
- May create new `app-X.X.X\` folder

### **Temporary/Ephemeral**:
- Cache directories
- Log files (rotated)
- Crash dumps
- Session storage

---

## 🚀 **Quick File Access Commands**

### Open Key Directories:
```powershell
# Open MCP config directory
explorer "C:\Users\sandr\AppData\Roaming\Claude"

# Open development projects
explorer "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6"

# Open VeoGen project
explorer "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"

# Open config backups
explorer "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\config-backups"
```

### Backup Commands:
```powershell
# Run automated backup
powershell -ExecutionPolicy Bypass -File "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\backup_mcp_config.ps1"

# Manual backup with timestamp
copy "C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json" "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\config-backups\manual_backup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm').json"
```

---

## 🔍 **Troubleshooting File Issues**

### **MCP Servers Not Loading**:
1. Check: `C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json`
2. Validate JSON syntax
3. Verify package names and paths
4. Restore from backup if corrupted

### **Projects Missing After Update**:
1. Check if new `app-X.X.X\` folder was created
2. Copy projects from old version folder
3. Update paths in documentation

### **Performance Issues**:
1. Clear cache: `AppData\Roaming\Claude\Cache\`
2. Clear IndexedDB: `AppData\Roaming\Claude\IndexedDB\`
3. Restart Claude

### **Config Corruption**:
1. Restore from: `config-backups\claude_desktop_config_*.json`
2. Validate restored config
3. Restart Claude
4. Re-authenticate MCP servers if needed

---

## 📊 **File Size & Space Usage**

### Typical Space Usage:
- **Core Application**: ~200-300 MB
- **VeoGen Project**: ~500 MB - 1 GB (with Docker images)
- **MCP Projects**: ~50-100 MB each
- **Cache Data**: ~100-500 MB
- **Total Claude Installation**: ~1-2 GB

### Cleanup Recommendations:
- **Weekly**: Clear cache directories
- **Monthly**: Clean old log files
- **Updates**: Remove old `app-X.X.X\` folders after successful migration

---

## 🎯 **Summary**

**Most Critical File**: `C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json`  
**Backup Location**: `C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\config-backups\`  
**Main Projects**: VeoGen, ImmichMCP, CalibreMCP, PlexMCP  
**Documentation Hub**: This file location

**Remember**: Always backup the MCP config before making changes, and keep your development projects in the `app-0.11.6\` folder where they're easily accessible and backed up!
