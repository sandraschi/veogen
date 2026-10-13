# MCP Memory System Guide

## Overview

The MCP (Model Context Protocol) memory system provides a **runtime knowledge graph** that stores entities and relationships. Unlike file-based systems, this memory lives in the MCP server and is managed through API calls, not direct file editing.

## How MCP Memory Works

### **Runtime vs File-Based**
- **Windsurf**: Rules stored in `.windsurf/rules/*.md` files (static)
- **MCP Memory**: Knowledge graph stored in MCP server (dynamic) 
- **Export Files**: Backup/documentation only, NOT the actual memory storage

### **Key Concept**
```
MCP Server Memory ←→ API Tools ←→ Export Files
     (actual)        (interface)    (backup)
```

## Current Status: POPULATED ✅

When I initially said "MCP memory system is empty" - that was the **starting state**. I then populated it using MCP tools. Let's verify current status:

### Check Current Memory State
```javascript
// This shows what's actually in MCP memory now
mcp_memory_read_graph("check_status")
```

**Result**: 11 entities + 10 relations from your Windsurf rules migration

## How to Fill MCP Memory

### **Method 1: Through MCP Tools (Recommended)**

#### Add New Memory Categories
```javascript
mcp_memory_create_entities([{
    "name": "New Category Name",
    "entityType": "MemoryCategory", 
    "observations": [
        "Rule 1: Description",
        "Rule 2: Description",
        "Rule 3: Description"
    ]
}])
```

#### Add to Existing Categories
```javascript
mcp_memory_add_observations([{
    "entityName": "PowerShell Syntax Rules",
    "contents": ["New rule: Always use proper parameter names"]
}])
```

#### Create Relationships
```javascript
mcp_memory_create_relations([{
    "from": "Parent Category",
    "to": "Child Category", 
    "relationType": "contains"
}])
```

### **Method 2: Batch Import from Code**

```python
# Example: Import multiple categories at once
def populate_mcp_memory():
    # Define your rules
    categories = [
        {
            "name": "Docker Rules",
            "entityType": "MemoryCategory",
            "observations": [
                "Use 'veogen' namespace for images",
                "Always include health checks",
                "Optimize layer caching"
            ]
        },
        {
            "name": "API Design Rules", 
            "entityType": "MemoryCategory",
            "observations": [
                "RESTful endpoints",
                "Consistent error responses",
                "Version all APIs"
            ]
        }
    ]
    
    # Use MCP tools to create
    for category in categories:
        mcp_memory_create_entities([category])
```

## Where is the "JSON to Edit"?

### **Important Clarification**

❌ **NOT Editable**: The JSON exports in `docs/development/mcp-memory-export.json`
- These are **snapshots** for backup/documentation
- Editing them does **NOT** change MCP memory
- They're like "save files" you can restore from

✅ **Actual Memory**: Lives in MCP server runtime
- No direct file to edit
- Managed through MCP API tools only  
- Persistent across sessions but server-managed

### **File Locations & Purposes**

```
docs/development/
├── mcp-memory-export.json      # 📄 BACKUP: Static snapshot
├── mcp-memory-export.md        # 📄 DOCUMENTATION: Human readable  
├── cursor-memories-export.md   # 📄 BACKUP: Conversational memories
├── memory-export-script.py     # 🔧 TOOL: Export automation
└── mcp-memory-system-guide.md  # 📖 GUIDE: This file
```

## Memory Population Workflow

### **1. Interactive Population**
```javascript
// Add new rules during conversation
"Remember this rule: Docker images should use multi-stage builds"
// Then convert to MCP memory:
mcp_memory_add_observations([{
    "entityName": "Docker Rules",
    "contents": ["Use multi-stage builds for size optimization"]
}])
```

### **2. Bulk Population** 
```javascript
// Import from your existing Windsurf rules (already done)
// Add project-specific rules
// Create new categories as needed
```

### **3. Maintenance Operations**

#### Search Existing Memory
```javascript
mcp_memory_search_nodes("Docker")
mcp_memory_search_nodes("PowerShell") 
mcp_memory_search_nodes("security")
```

#### Update Existing Rules
```javascript
// Add to existing category
mcp_memory_add_observations([{
    "entityName": "Security Rules",
    "contents": ["New security requirement: Use HTTPS only"]
}])
```

#### Remove Outdated Rules
```javascript
mcp_memory_delete_observations([{
    "entityName": "PowerShell Syntax Rules",
    "observations": ["Outdated rule to remove"]
}])
```

## Export and Backup Strategy

### **Regular Exports**
```bash
# Using the export script
python docs/development/memory-export-script.py --format all
```

### **Manual Export** 
```javascript
// Get current state
mcp_memory_read_graph("backup_export")
// Copy result to backup files
```

### **Restore Strategy**
```javascript
// If MCP memory is lost, recreate from exports:
// 1. Read export JSON files
// 2. Use mcp_memory_create_entities() with exported data
// 3. Use mcp_memory_create_relations() with exported relationships
```

## Best Practices

### **Memory Organization**
- **Categories**: Group related rules (Security, PowerShell, Docker, etc.)
- **Observations**: Specific, actionable rules within categories
- **Relations**: Link categories to parent projects or concepts

### **Naming Conventions**
- **Categories**: "[Topic] Rules" (e.g., "PowerShell Syntax Rules")
- **Projects**: "[Project] Memories" (e.g., "VeoGen Project Memories")
- **Relations**: Use clear verbs ("contains", "requires", "implements")

### **Maintenance Schedule**
- **Weekly**: Add new rules discovered during development
- **Monthly**: Review and clean up outdated rules  
- **Project End**: Full export for project documentation

## Troubleshooting

### **"Empty Memory" Issues**
```javascript
// Check if memory really empty
mcp_memory_read_graph("diagnostic")

// If empty, may need to re-populate
// Use backup files to restore
```

### **Search Not Finding Rules**
```javascript
// Try broader search terms
mcp_memory_search_nodes("syntax")  // instead of "PowerShell syntax rules"

// Or open specific nodes
mcp_memory_open_nodes(["PowerShell Syntax Rules"])
```

### **Lost Relationships**
```javascript
// Recreate key relationships
mcp_memory_create_relations([{
    "from": "VeoGen Project Memories",
    "to": "New Category",
    "relationType": "contains"
}])
```

## Integration with Conversational Memory

### **Dual System Strategy**
1. **Conversational Memory**: For immediate, context-specific rules
2. **MCP Memory**: For structured, searchable, exportable rules

### **Conversion Workflow**
```
User tells me rule → Conversational memory → Convert to MCP memory → Export backup
```

### **When to Use Which**
- **Conversational**: Quick preferences, session-specific context
- **MCP**: Project rules, technical standards, reusable knowledge

## Current VeoGen Memory State

✅ **Populated Categories**: 10 rule categories (40+ individual rules)
✅ **Relationships**: All categories linked to "VeoGen Project Memories"  
✅ **Searchable**: Can find rules by topic/keyword
✅ **Exportable**: JSON/Markdown backups available
✅ **Persistent**: Survives session restarts

**Next Steps**:
1. Add project-specific rules as we discover them
2. Create categories for new domains (Frontend, Database, etc.)
3. Regular exports for backup
4. Integration with project documentation

---

*The MCP memory system is NOW ACTIVE and populated with your Windsurf rules!* 