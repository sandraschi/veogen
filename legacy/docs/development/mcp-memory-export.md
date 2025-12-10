# Memory Export - Knowledge Graph

**Export Date:** 2025-01-17 12:00:00  
**Total Entities:** 11  
**Total Relations:** 10  
**Source:** MCP Knowledge Graph - VeoGen Project Memories

## Entities

### PowerShell Syntax Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589190: Never use Linux syntax in scripts or chats
- No && for chaining commands or similar Linux operators allowed
- Always use proper PowerShell syntax for Windows environment
- Use semicolons for command separation instead of &&

### Change Management Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589445: Never remove, rewrite, or break major functionality without explicit user instruction
- Always clarify and confirm before making changes that could disrupt workflows
- Provide explicit diffs and summaries for major edits so user can review before anything is lost

### Filesystem Safety Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589449: Never try to edit or create a file in a nonexistent directory
- Always check if the target directory exists before file operations
- If directory does not exist, create it first using PowerShell New-Item -ItemType Directory -Force
- This applies to all automated workflows

### Error Handling Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589454: All code must implement robust error handling
- Catch and handle exceptions at logical boundaries, never silently ignore errors
- Use logger service, not console (e.g. logger.error instead of console.error)
- Always provide clear, actionable error messages and fail safely, informing the user

### Transparency Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589460: For every automated action, provide a summary of what was done, why, and what rules were followed
- Allow the user to request a full activity or decision log at any time
- Record origin, version, and timestamp of imported code or data

### File Size Management Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589467: Avoid creating or maintaining source files so large that they cannot be safely edited
- When a file approaches system limits, proactively split it into smaller, logical modules
- Use chunked editing strategies when needed
- Never attempt single edit operations that risk failure due to size; prefer modularity and maintainability

### Security Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589469: Never log, display, or transmit sensitive information unless explicitly required and approved
- Always sanitize user input and validate external data sources
- Use environment variables for sensitive data, never hardcode credentials
- Passwords and API keys must never be logged

### Code Quality Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589472: All code must be readable and self-documenting
- Use meaningful variable and function names
- Keep functions small and focused (max 50 lines)
- Follow language-specific style guides
- Include comments for complex logic
- Maintain consistent indentation

### User Experience Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589477: Users should always see meaningful feedback, never blank screens
- Loading states must be implemented for all async operations
- Error messages must be user-friendly and actionable
- Always notify user of errors with clear summary and suggested next steps

### Backup Strategy Rules
**Type:** MemoryCategory

**Observations:**
- Memory ID 2589482: Before destructive or high-impact operations, create a backup or checkpoint
- Inform the user where the backup is stored and how to restore it
- Offer to help set up lightweight, auto-staged commits or other safety nets
- Prevent accidental loss of work and make rollbacks easy

### VeoGen Project Memories
**Type:** ProjectMemories

**Observations:**
- Converted from Windsurf .windsurf/rules/global_rules/ directory
- Contains development rules, safety protocols, and workflow preferences
- Created on current session for Sandra's VeoGen project
- Total memory categories: 10
- Source: rules1.md, rules2.md, rules3.md from Windsurf setup

## Relations

| From | Relation | To |
|------|----------|----| 
| VeoGen Project Memories | contains | PowerShell Syntax Rules |
| VeoGen Project Memories | contains | Change Management Rules |
| VeoGen Project Memories | contains | Filesystem Safety Rules |
| VeoGen Project Memories | contains | Error Handling Rules |
| VeoGen Project Memories | contains | Transparency Rules |
| VeoGen Project Memories | contains | File Size Management Rules |
| VeoGen Project Memories | contains | Security Rules |
| VeoGen Project Memories | contains | Code Quality Rules |
| VeoGen Project Memories | contains | User Experience Rules |
| VeoGen Project Memories | contains | Backup Strategy Rules |

## Memory Categories Overview

- **PowerShell Syntax Rules**: 4 rules
- **Change Management Rules**: 3 rules
- **Filesystem Safety Rules**: 4 rules
- **Error Handling Rules**: 4 rules
- **Transparency Rules**: 3 rules
- **File Size Management Rules**: 4 rules
- **Security Rules**: 4 rules
- **Code Quality Rules**: 6 rules
- **User Experience Rules**: 4 rules
- **Backup Strategy Rules**: 4 rules

## Usage Instructions

### Searching Memories
Use MCP memory search tools:
```python
# Search for specific topics
mcp_memory_search_nodes("PowerShell syntax")
mcp_memory_search_nodes("error handling")
mcp_memory_search_nodes("security rules")
```

### Accessing Specific Categories  
```python
# Open specific memory categories
mcp_memory_open_nodes(["PowerShell Syntax Rules", "Security Rules"])
```

### Adding New Memories
```python
# Add new observations to existing categories
mcp_memory_add_observations([{
    "entityName": "PowerShell Syntax Rules",
    "contents": ["New rule about PowerShell best practices"]
}])
```

### Restoring From Export
Use the provided Python script `memory-export-script.py` to restore this knowledge graph to a new MCP instance.

---
*This export contains all memories migrated from your Windsurf .windsurf/rules/global_rules/ setup* 