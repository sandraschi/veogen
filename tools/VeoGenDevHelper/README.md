# 🎛️ VeoGen Dev Helper v2.1

> Environment control center for VeoGen development with service monitoring and quick navigation

## 🎯 Overview

VeoGen Dev Helper is your command center for VeoGen development. It provides real-time service monitoring, quick access to all VeoGen components, and embedded path intelligence to eliminate the "Schnitzeljagd" (treasure hunt) across development sessions.

## ✨ Key Features

- 🚀 **Service Status Monitoring**: Real-time checking of all VeoGen services
- ⚡ **Quick Actions**: Direct links to VeoGen app, API docs, Grafana, and more
- 📍 **Path Intelligence**: All VeoGen folder locations embedded - no more searching!
- 🛡️ **Anti-Guillotine Protection**: v2.1 with enhanced corruption resistance
- 💻 **Command Output**: Real-time logging and session management
- 🔐 **Authentication Testing**: Quick auth system verification
- 📊 **System Statistics**: Health monitoring and usage metrics

## 🚀 Quick Start

### Method 1: Batch Launcher (Easiest)
Double-click `VeoGenDevHelper.bat` to launch instantly.

### Method 2: PowerShell
```powershell
.\VeoGenDevHelper.ps1 -Start
```

### Method 3: Direct HTML
Open `VeoGenDevHelper.html` in your web browser.

## 📋 Management Commands

```powershell
# Launch the web interface
.\VeoGenDevHelper.ps1 -Start

# Show system status and paths
.\VeoGenDevHelper.ps1 -Status

# Display help information
.\VeoGenDevHelper.ps1 -Help
```

## 📍 VeoGen Path Intelligence

No more Schnitzeljagd! All essential VeoGen paths are embedded:

- **Root**: `C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen`
- **Tools**: `...\veogen\tools`
- **Backend**: `...\veogen\backend`
- **Frontend**: `...\veogen\frontend`
- **Incidents**: `...\veogen\incidents`
- **Docs**: `...\veogen\docs`

## 🌐 Quick Access Links

The Dev Helper provides instant access to:
- **VeoGen App**: http://localhost:4710
- **API Documentation**: http://localhost:4700/docs
- **Grafana Monitoring**: http://localhost:4725
- **Prometheus**: http://localhost:4740
- **User Manager**: http://localhost:8083

## 🛡️ Anti-Guillotine Protection v2.1

Enhanced protection against all guillotine types:
- **Guill1**: Timeout guillotine resistance
- **Guill2**: Forced restart protection
- **Guill3**: Continue button corruption prevention
- Compact file structure for faster operations
- Built-in recovery procedures

## 🚀 Service Monitoring

Real-time monitoring of VeoGen services:
- ✅ Frontend (React) - Port 4710
- ✅ Backend (FastAPI) - Port 4700
- ✅ PostgreSQL Database - Port 4715
- ✅ Grafana Monitoring - Port 4725
- 🔄 User Manager - Port 8083

## 💡 Development Workflow Integration

The Dev Helper eliminates common development friction:
- **No path hunting**: All locations embedded
- **Quick service checks**: Instant status verification
- **Fast navigation**: One-click access to any component
- **Session logging**: Track your development activities
- **Error recovery**: Built-in anti-guillotine protection

## 🔧 Technical Specifications

- **Version**: 2.1.0
- **Platform**: Windows (PowerShell 5.1+)
- **Browser Support**: Chrome, Firefox, Edge, Safari
- **Dependencies**: None (self-contained)
- **VeoGen Integration**: Full path awareness
- **Protection Level**: Anti-guillotine v2.1

## 📊 Features Overview

### Service Management
- Real-time service status checking
- Quick start/stop operations
- Health monitoring dashboard
- Log output display

### Quick Navigation
- Embedded VeoGen path intelligence
- One-click access to all components
- No more folder searching
- Context-aware operations

### Development Support
- Authentication testing
- API endpoint verification
- Docker service management
- Incident tracking integration

## 🔍 Troubleshooting

### Common Issues

**Dev Helper won't start**
- Check PowerShell execution policy
- Verify all files are present
- Run `.\VeoGenDevHelper.ps1 -Status` for diagnostics

**Services showing as stopped**
- Run `docker-compose ps` in VeoGen root
- Use "Start All" button in the interface
- Check Docker Desktop is running

### Getting Help

1. Run `.\VeoGenDevHelper.ps1 -Help` for options
2. Check the web interface for real-time status
3. Review logs in the command output panel

## 📝 Development Notes

- **Created**: Enhanced for v2.1 anti-guillotine protection
- **Purpose**: Eliminate development session friction
- **Integration**: Full VeoGen ecosystem awareness
- **Protection**: Guill3-resistant file structure

## 🎉 Success Metrics

- ⚡ **Instant access**: No more searching for folders
- 🔄 **Quick status**: Real-time service monitoring
- 🛡️ **Reliable operation**: Anti-guillotine protection
- 📈 **Improved workflow**: Measurable efficiency gains

---

*VeoGen Dev Helper v2.1 - Your anti-guillotine protected environment control center*

**No more Schnitzeljagd!** 🎯