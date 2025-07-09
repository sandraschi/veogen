# 🔐 MCP Servers Authentication Setup

## Your Server Credentials

### 📸 Immich
- **Server URL**: http://localhost:2283
- **API Key**: yGKAUQMhgqcZpjIKMb5geToHFOAUsRtnj6fSKVtRE

### 📚 Calibre  
- **Server URL**: http://localhost:8099
- **Username**: sandraschipal@hotmail.com
- **Password**: Sec2000plex#

### 🎬 Plex
- **Server URL**: http://localhost:32400
- **Token**: [Need to obtain - see instructions below]

## Quick Setup Scripts

### Windows PowerShell Setup:
```powershell
# Set environment variables for current session
$env:IMMICH_SERVER_URL="http://localhost:2283"
$env:IMMICH_API_KEY="yGKAUQMhgqcZpjIKMb5geToHFOAUsRtnj6fSKVtRE"

$env:CALIBRE_SERVER_URL="http://localhost:8099"
$env:CALIBRE_USERNAME="sandraschipal@hotmail.com"
$env:CALIBRE_PASSWORD="Sec2000plex#"

$env:PLEX_SERVER_URL="http://localhost:32400"
# $env:PLEX_TOKEN="[GET_FROM_PLEX]"
```

### Linux/Mac Bash Setup:
```bash
# Set environment variables
export IMMICH_SERVER_URL="http://localhost:2283"
export IMMICH_API_KEY="yGKAUQMhgqcZpjIKMb5geToHFOAUsRtnj6fSKVtRE"

export CALIBRE_SERVER_URL="http://localhost:8099"
export CALIBRE_USERNAME="sandraschipal@hotmail.com"
export CALIBRE_PASSWORD="Sec2000plex#"

export PLEX_SERVER_URL="http://localhost:32400"
# export PLEX_TOKEN="[GET_FROM_PLEX]"
```

## .env File for Development:
```env
# ImmichMCP
IMMICH_SERVER_URL=http://localhost:2283
IMMICH_API_KEY=yGKAUQMhgqcZpjIKMb5geToHFOAUsRtnj6fSKVtRE

# CalibreMCP
CALIBRE_SERVER_URL=http://localhost:8099
CALIBRE_USERNAME=sandraschipal@hotmail.com
CALIBRE_PASSWORD=Sec2000plex#

# PlexMCP
PLEX_SERVER_URL=http://localhost:32400
# PLEX_TOKEN=[GET_FROM_PLEX]
```

## 🎬 How to Get Your Plex Token

### Method 1 - Browser Developer Tools:
1. Open http://localhost:32400/web in your browser
2. Log in to Plex
3. Press F12 to open Developer Tools
4. Go to Network tab
5. Refresh the page
6. Look for any request and find "X-Plex-Token" in the headers
7. Copy the token value

### Method 2 - From Plex URL:
1. In Plex web interface, right-click any movie/show
2. Select "Get Info" or similar
3. Look at the URL bar for "X-Plex-Token=abc123..."
4. Copy everything after the equals sign

### Method 3 - XML Method:
1. Go to: http://localhost:32400/?X-Plex-Token=
2. Try to access without token first to see if auth is needed
3. If you see XML response, Plex might not require token locally

## ✅ Test Your Connections

### Test Immich:
```bash
curl -H "X-API-Key: yGKAUQMhgqcZpjIKMb5geToHFOAUsRtnj6fSKVtRE" http://localhost:2283/api/server-info/ping
```

### Test Calibre:
```bash
curl -u "sandraschipal@hotmail.com:Sec2000plex#" http://localhost:8099/
```

### Test Plex:
```bash
curl "http://localhost:32400/?X-Plex-Token=YOUR_TOKEN_HERE"
```

## 🚀 Ready to Install MCP Servers

Once you have the Plex token, all three servers will be ready to install and test!
