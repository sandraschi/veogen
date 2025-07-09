import { McpError, ErrorCode } from '@modelcontextprotocol/sdk/types.js';
import { TailLogsSchema } from '../lib/schemas.js';
import { LogReaderService } from '../lib/log-reader.js';
import { formatLogsForDisplay } from '../lib/types.js';

export class LogTailHandler {
  private logReader = new LogReaderService();
  private tailSessions = new Map<string, any>();

  async handle(args: any) {
    const params = TailLogsSchema.parse(args);
    
    try {
      const sessionId = `${params.source}-${Date.now()}`;
      
      // Create filter pattern if specified
      let filterPattern: RegExp | undefined;
      if (params.filter) {
        try {
          filterPattern = new RegExp(params.filter, 'i');
        } catch {
          filterPattern = new RegExp(params.filter.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
        }
      }

      // Get initial log lines
      const initialLogs = await this.logReader.readLogs({
        source: params.source,
        lines: params.lines,
        tail: true
      });

      // Filter initial logs if pattern specified
      const filteredInitial = filterPattern 
        ? initialLogs.filter(log => filterPattern!.test(log.message) || filterPattern!.test(log.rawLine))
        : initialLogs;

      // Store session for potential future use
      this.tailSessions.set(sessionId, {
        source: params.source,
        filter: filterPattern,
        isActive: true,
        startTime: new Date()
      });

      return {
        content: [
          {
            type: 'text',
            text: `🔄 **Real-time Log Monitor**

**Source**: ${params.source}
**Session ID**: ${sessionId}
**Filter**: ${params.filter || 'None'}
**Lines**: ${params.lines}

**Initial Log Entries**:
${formatLogsForDisplay(filteredInitial)}

**Status**: ✅ Monitoring session created
**Note**: This shows the most recent entries. For continuous monitoring, 
use this as a baseline and call read_logs with tail=true for updates.

To get new entries since this session:
• Use read_logs with since parameter set to this session's start time
• Or use search_logs to find specific patterns that appeared recently`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to start log tailing: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  // Get active sessions for monitoring
  getActiveSessions() {
    return Array.from(this.tailSessions.entries()).map(([id, session]) => ({
      id,
      source: session.source,
      startTime: session.startTime,
      isActive: session.isActive
    }));
  }

  // Clean up old sessions
  cleanupSessions() {
    const now = Date.now();
    const thirtyMinutes = 30 * 60 * 1000;
    
    for (const [id, session] of this.tailSessions.entries()) {
      if (now - session.startTime.getTime() > thirtyMinutes) {
        this.tailSessions.delete(id);
      }
    }
  }
}
