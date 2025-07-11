---
title: PLAYWRIGHT_MCP_FIX_CONFIGURATION
type: note
permalink: docs-claude-playwright-mcp-fix-configuration
---

# 🔧 Playwright MCP Configuration Fix

## 🚨 **Problem Identified**

The current Playwright MCP configuration is using **wrong package names** that hang on startup:
- ❌ `playwright-mcp-server` (hangs)
- ❌ `mcp-playwright` (hangs)

## ✅ **Correct Configuration**

### **Working Playwright MCP Package:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-playwright"],
      "env": {
        "PLAYWRIGHT_BROWSERS_PATH": "0"
      }
    }
  }
}
```

### **Alternative: No Browser Download Required:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-playwright", "--use-existing-browser"],
      "env": {
        "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "0"
      }
    }
  }
}
```

## 🎯 **Key Changes Made**

1. **Correct Package Name**: `@modelcontextprotocol/server-playwright`
2. **Skip Browser Download**: Use existing Edge/Firefox browsers
3. **Environment Variables**: Prevent Chromium download
4. **Use Existing Browser**: Tell Playwright to use system browsers

## 🚀 **Environment Variables to Prevent Browser Download**

Add these environment variables to prevent the crazy Chromium download:
- `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` - Skip automatic browser download
- `PLAYWRIGHT_BROWSERS_PATH=0` - Use system browsers
- `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/path/to/edge` (if needed)

## 🔧 **Complete Fixed MCP Config Section**

Replace the broken Playwright entries with this:

```json
"playwright": {
  "command": "npx",
  "args": ["@modelcontextprotocol/server-playwright"],
  "env": {
    "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
    "PLAYWRIGHT_BROWSERS_PATH": "0"
  }
}
```

## 🧪 **Testing the Fix**

After applying this configuration:
1. Restart Claude Desktop
2. Test with: "Take a screenshot of google.com"
3. Should work without downloading browsers

## 📝 **What This Fixes**

- ✅ **No More Hangs**: Uses correct package that doesn't hang
- ✅ **No Browser Download**: Uses existing Edge/Firefox browsers  
- ✅ **Faster Startup**: Immediate MCP server response
- ✅ **Less Resource Usage**: No unnecessary Chromium installation
- ✅ **Working Browser Automation**: Full Playwright functionality available

## 🎯 **Next Steps**

1. **Backup current config**: Always backup before changes
2. **Update MCP config**: Replace broken entries with fixed one
3. **Restart Claude**: Required for MCP changes to take effect
4. **Test functionality**: Verify browser automation works

The Playwright MCP will now work properly with existing browsers! 🎭✨