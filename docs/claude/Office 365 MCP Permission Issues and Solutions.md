---
title: Office 365 MCP Permission Issues and Solutions
type: note
permalink: docs-claude-office-365-mcp-permission-issues-and-solutions
---

# Office 365 MCP Permission Issues and Solutions

## Problem Summary
The Microsoft 365 MCP server in Claude Desktop has limited Graph API permissions, preventing:
- **Teams chat messaging** (missing Chat.ReadWrite, ChatMessage.Send scopes)
- **OneNote content reading** (HTML parsing errors, missing Notes.ReadWrite.All)

## Current Status
- ✅ Basic authentication working (logged in as Sandra Schipal)
- ✅ Can access OneNote notebooks and sections list
- ❌ Cannot send Teams messages (403 Forbidden - missing authorization)
- ❌ Cannot read OneNote page content (HTML parsing error)

## Teams Messaging Solution

### Required Permissions
- `Chat.ReadWrite` - Read/write 1-on-1 or group chat messages
- `ChatMessage.Send` - Send chat messages
- `Chat.ReadBasic` - List and find chats

### Configuration Fix
**File to edit:** `C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json`

**Add scopes to Microsoft 365 MCP config:**
```json
{
  "mcpServers": {
    "microsoft-365": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server-microsoft365"],
      "env": {
        "MICROSOFT365_CLIENT_ID": "your-existing-id",
        "MICROSOFT365_CLIENT_SECRET": "your-existing-secret",
        "MICROSOFT365_TENANT_ID": "your-existing-tenant",
        "MICROSOFT365_SCOPES": "https://graph.microsoft.com/User.Read https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/Contacts.ReadWrite https://graph.microsoft.com/Chat.ReadWrite https://graph.microsoft.com/ChatMessage.Send https://graph.microsoft.com/Chat.ReadBasic https://graph.microsoft.com/Notes.ReadWrite.All"
      }
    }
  }
}
```

### Steps
1. Edit claude_desktop_config.json
2. Add MICROSOFT365_SCOPES environment variable
3. Restart Claude Desktop
4. Re-authenticate if prompted
5. Test with `listChats()` and `sendChatMessage()`

## OneNote HTML Parsing Solution

### Problem
OneNote content returns as HTML but MCP expects JSON, causing:
```
"Unexpected token '<', "<html lang"... is not valid JSON"
```

### Solution 1: HTML Content Extractor
Created `OneNoteExtractor` class to:
- Parse HTML content using DOMParser
- Extract clean text while preserving structure
- Convert to markdown format
- Handle tables, lists, links, formatting

### Solution 2: Claude-Assisted Processing
```javascript
const cleanContent = await window.claude.complete(`
Extract clean text content from this OneNote HTML, preserving structure:
${htmlContent}

Return as clean markdown.
`);
```

### Solution 3: Playwright HTML Processing
Use Playwright tools to parse complex HTML content if needed.

## Azure App Registration (If Needed)
If MCP was set up with limited scopes:
1. Azure Portal → App Registrations
2. Find MCP app (likely "Claude MCP" or "Microsoft365-MCP")
3. API Permissions → Add permissions → Microsoft Graph → Delegated
4. Add required permissions
5. Grant admin consent

## Testing Plan
After configuration update:
1. **Teams**: Try sending message to Noriko "see you at 2pm. claude ai has entered the chat"
2. **OneNote**: Test HTML extraction with existing AI section pages
3. **Verification**: Confirm all Office 365 functions work properly

## Workarounds (Temporary)
- **Teams**: Use Outlook email instead of chat
- **OneNote**: Use HTML extractor code for content processing
- **Calendar**: Create meeting invites for coordination

## Related Tools Available
- ✅ Outlook email (working)
- ✅ Calendar events (working)  
- ✅ Contacts (working)
- ✅ OneDrive files (working)
- ❌ Teams chat (needs permissions)
- ❌ OneNote content (needs HTML parsing)

## Implementation Priority
1. **High**: Update MCP configuration with new scopes
2. **Medium**: Test Teams messaging functionality
3. **Medium**: Implement OneNote HTML extractor
4. **Low**: Explore advanced Azure app permissions if needed