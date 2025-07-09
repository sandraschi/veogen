# Cursor Memory System and Rule Handling Guide

This guide explains how to work with Claude's memory system in Cursor and how it differs from Windsurf's automatic rule reading.

## Memory System Overview

Unlike Windsurf which reads rules from `.windsurf/rules/` directories automatically, Cursor/Claude uses a conversational memory system that builds context through interaction.

### How Memories Work

**Memory Creation:**
- **Conversational**: Simply tell Claude "Remember that I prefer X"
- **Automatic**: Claude creates memories when you correct it or provide important context
- **Rule-based**: Ask Claude to "Remember this rule: [rule description]"

**Memory Usage:**
- Claude automatically uses relevant memories during conversations
- Memories are cited with format `[[memory:MEMORY_ID]]` when used
- You can see when Claude is applying a remembered preference or rule

**Memory Management:**
- **Update**: Correct Claude when it's wrong: "Actually, I prefer Y instead"
- **Delete**: Directly contradict: "That memory is incorrect, delete it"
- **Replace**: Provide new information: "The new rule is Z, not X"

## Rule Handling: Windsurf vs Cursor

### Windsurf Approach
```
.windsurf/
├── rules/
│   └── global_rules/
│       ├── rules1.md
│       ├── rules2.md
│       └── rules3.md
```
- **Automatic**: Rules read from files on startup
- **File-based**: Rules stored in markdown files
- **Persistent**: Always active across sessions

### Cursor Approach
```
Conversation → Memories → Applied Rules
```
- **Conversational**: Rules provided through chat
- **Memory-based**: Rules stored as memories
- **Contextual**: Applied when relevant to current task

## Migrating from Windsurf Rules

### Step 1: Extract Key Rules
Review your Windsurf rules and identify:
- Change management preferences
- Coding standards and practices
- Safety requirements
- Workflow patterns

### Step 2: Convert to Memories
Tell Claude to remember each important rule:

```
"Remember this rule: Never remove or break major functionality without explicit user instruction"
"Remember: I prefer complete responses over minimal ones" 
"Remember: Always use PowerShell syntax for Windows, never Linux commands"
```

### Step 3: Test and Refine
- Observe Claude's behavior in subsequent sessions
- Correct any misapplied rules
- Add new rules as needed

## Best Practices

### Creating Effective Memories

**Good Memory Requests:**
```
✅ "Remember that I prefer debugging to start by listing common causes"
✅ "Remember this rule: Always cd to correct directory before running commands"
✅ "Remember: Use 'veogen' namespace for Docker images"
```

**Poor Memory Requests:**
```
❌ "Remember everything in this file" (too broad)
❌ "Remember my preferences" (too vague)
❌ "Remember this complex 50-line rule set" (too detailed)
```

### Memory Maintenance

**Regular Review:**
- Periodically ask Claude what memories it has about your preferences
- Update outdated rules when workflows change
- Delete conflicting or obsolete memories

**Conflict Resolution:**
- When Claude applies incorrect rules, immediately correct it
- Be specific about what changed: "The new rule is X, not Y"
- Confirm the update: "Do you understand the new rule?"

## Common Rule Categories

### Development Practices
- Code style preferences
- Testing requirements
- Documentation standards
- Deployment procedures

### Environment Specifics
- OS-specific commands (PowerShell vs Bash)
- Directory structures
- Tool configurations
- Path conventions

### Workflow Preferences
- Communication style (complete vs minimal)
- Error handling approaches
- Debugging methodologies
- Change management policies

### Safety Rules
- Backup requirements
- Validation procedures
- Rollback strategies
- User confirmation needs

## Example Migration

### Original Windsurf Rule
```markdown
## Script syntax
- Never use linux syntax in windows shells, batch scripts or cascade commands
- No rmdir, mkdir or cd with linux-style parameters
- No && for chaining commands, use semicolon
```

### Converted Cursor Memory
```
"Remember: When running commands in Windows shell, always use PowerShell syntax. Never use Linux commands like rmdir, mkdir with Linux parameters, or chain commands with &&. Always use proper PowerShell equivalents."
```

## Troubleshooting

### Claude Not Following Rules
1. **Check Memory Citation**: Look for `[[memory:ID]]` references
2. **Clarify Rule**: Restate the rule more specifically
3. **Correct Immediately**: Don't let incorrect behavior persist

### Memory Conflicts
1. **Identify Conflict**: Claude mentions contradictory preferences
2. **Resolve Explicitly**: "Delete the old rule about X, the new rule is Y"
3. **Confirm Resolution**: Ask Claude to confirm the updated rule

### Lost Context
1. **Restate Key Rules**: In new sessions, remind Claude of critical rules
2. **Build Context**: Reference previous successful interactions
3. **Update Memories**: Add any missing preferences discovered during work

## Integration with VeoGen Workflow

### Project-Specific Rules
```
"Remember: For VeoGen project, backend uses gemini-cli as primary interface"
"Remember: Docker images should use 'veogen' namespace"
"Remember: Always check working directory before running backend/frontend tasks"
```

### Development Flow
1. Start session by mentioning key project context
2. Claude applies relevant memories automatically
3. Correct any misapplied rules immediately
4. Build new memories for discovered preferences

## Summary

The Cursor memory system provides flexible, contextual rule management through conversation rather than file-based configuration. While different from Windsurf's automatic rule reading, it offers dynamic adaptation and easier maintenance of development preferences.

Key advantages:
- **Contextual**: Rules applied when relevant
- **Adaptive**: Easy to update and refine
- **Conversational**: Natural interaction model
- **Persistent**: Memories carry across sessions

The system works best when rules are specific, actionable, and regularly maintained through ongoing conversation. 