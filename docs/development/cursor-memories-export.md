# Cursor Memories Export

This file documents the memories created for Claude in Cursor, converted from Windsurf rules.

## Current Active Memories

### PowerShell Syntax Rules
**Memory ID**: 2589190
**Title**: Windows PowerShell Syntax Only - No Linux Commands
**Content**: Never use Linux syntax in scripts or chats. No && for chaining commands or similar Linux operators allowed. Always use proper PowerShell syntax for Windows environment. Use semicolons for command separation instead of &&.

### Change Management
**Memory ID**: 2589445
**Title**: Change Management - Never Break Major Functionality
**Content**: Never remove, rewrite, or break major functionality (backend support, critical features, user workflows) without explicit user instruction. Always clarify and confirm before making changes that could disrupt workflows or compatibility. Provide explicit diffs and summaries for major edits so user can review before anything is lost.

### Filesystem Safety
**Memory ID**: 2589449
**Title**: Filesystem Safety - Check Directory Existence
**Content**: Never try to edit or create a file in a nonexistent directory. Always check if the target directory exists before file operations. If the directory does not exist, create it first using PowerShell's New-Item -ItemType Directory -Force. This applies to all automated workflows.

### Error Handling
**Memory ID**: 2589454
**Title**: Error Handling - Use Logger Service Not Console
**Content**: All code must implement robust error handling. Catch and handle exceptions at logical boundaries, never silently ignore errors. Use logger service, not console (e.g. logger.error instead of console.error). Always provide clear, actionable error messages and fail safely, informing the user.

### Transparency
**Memory ID**: 2589460
**Title**: Transparency - Always Explain Actions and Rules
**Content**: For every automated action, provide a summary of what was done, why, and what rules or logic were followed. Allow the user to request a full activity or decision log at any time. Record origin, version, and timestamp of imported code or data.

### File Size Management
**Memory ID**: 2589467
**Title**: File Size Management - Avoid Large Uneditable Files
**Content**: Avoid creating or maintaining source files so large that they cannot be safely edited. When a file approaches system limits, proactively split it into smaller, logical modules or use chunked editing strategies. Never attempt single edit operations that risk failure due to size; prefer modularity and maintainability.

### Security
**Memory ID**: 2589469
**Title**: Security - Never Log Sensitive Data
**Content**: Never log, display, or transmit sensitive information (passwords, API keys) unless explicitly required and approved. Always sanitize user input and validate external data sources. Use environment variables for sensitive data, never hardcode credentials.

### Code Quality
**Memory ID**: 2589472
**Title**: Code Quality - Readable Self-Documenting Code
**Content**: All code must be readable and self-documenting. Use meaningful variable and function names. Keep functions small and focused (max 50 lines). Follow language-specific style guides. Include comments for complex logic. Maintain consistent indentation.

### User Experience
**Memory ID**: 2589477
**Title**: User Experience - Meaningful Feedback Always
**Content**: Users should always see meaningful feedback, never blank screens. Loading states must be implemented for all async operations. Error messages must be user-friendly and actionable. Always notify user of errors with clear summary and suggested next steps.

### Backup Strategy
**Memory ID**: 2589482
**Title**: Backup Strategy - Create Backups Before Destructive Operations
**Content**: Before destructive or high-impact operations, create a backup or checkpoint. Inform the user where the backup is stored and how to restore it. Offer to help set up lightweight, auto-staged commits or other safety nets to prevent accidental loss of work.

## Memory Management Notes

### Limitations
- I cannot directly export ALL memories from the system
- This file only documents memories created during recent conversations
- Some memories may exist from previous sessions that aren't listed here

### Memory Sources
- **Windsurf Rules Migration**: Converted from `.windsurf/rules/global_rules/rules1.md`, `rules2.md`, and `rules3.md`
- **User Instructions**: Direct rules provided in conversation
- **Previous Sessions**: May have additional memories not documented here

### Maintenance
- Update this file when creating new significant memories
- Remove entries when memories are deleted
- Note memory ID changes if memories are updated

## Usage in New Sessions

To activate these memories in new Cursor sessions:
1. Reference specific topics that trigger memory recall
2. Mention "Remember your rule about X" to prompt memory access
3. Correct behavior if memories aren't being applied properly

## Memory Categories

### Development Rules
- PowerShell syntax requirements
- Error handling standards
- Code quality guidelines
- File management practices

### Safety Rules
- Change management protocols
- Backup requirements
- Security standards
- User confirmation needs

### Workflow Rules
- Transparency requirements
- User experience standards
- Filesystem safety protocols
- Documentation practices

---

*Last Updated: [Current Date]*
*Total Documented Memories: 10* 