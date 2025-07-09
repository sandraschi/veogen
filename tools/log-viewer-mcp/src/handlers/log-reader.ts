import { McpError, ErrorCode } from '@modelcontextprotocol/sdk/types.js';
import { ReadLogsSchema } from '../lib/schemas.js';
import { LogReaderService } from '../lib/log-reader.js';
import { formatLogsForDisplay, getTimeRange } from '../lib/types.js';

export class LogReaderHandler {
  private logReader = new LogReaderService();

  async handle(args: any) {
    const params = ReadLogsSchema.parse(args);
    
    try {
      const logs = await this.logReader.readLogs({
        source: params.source,
        lines: params.lines,
        level: params.level,
        search: params.search,
        since: params.since,
        tail: params.tail
      });

      const summary = this.generateLogSummary(logs);
      const insights = this.generateInsights(logs);
      
      return {
        content: [
          {
            type: 'text',
            text: `📊 **Log Analysis Results**

**Source**: ${params.source}
**Lines Retrieved**: ${logs.length}
**Time Range**: ${getTimeRange(logs)}

${summary}

**Key Insights**:
${insights}

**Recent Entries**:
${formatLogsForDisplay(logs.slice(-Math.min(15, logs.length)))}

${logs.length > 15 ? `\n*Showing last 15 of ${logs.length} entries*` : ''}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to read logs: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private generateLogSummary(logs: any[]): string {
    const levels = logs.reduce((acc, log) => {
      acc[log.level] = (acc[log.level] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const errors = levels.ERROR || 0;
    const warnings = levels.WARNING || levels.WARN || 0;
    const info = levels.INFO || 0;

    return `**Log Level Summary**:
• 🔴 Errors: ${errors}
• 🟡 Warnings: ${warnings}  
• 🔵 Info: ${info}
• 🟢 Debug: ${levels.DEBUG || 0}`;
  }

  private generateInsights(logs: any[]): string {
    const insights: string[] = [];
    
    const errorLogs = logs.filter(log => log.level === 'ERROR');
    if (errorLogs.length > 0) {
      insights.push(`• Found ${errorLogs.length} error(s) - requires attention`);
    }

    if (logs.length === 0) {
      insights.push('• No logs found in specified criteria');
    } else {
      insights.push('• Log data successfully retrieved and parsed');
    }

    return insights.length > 0 ? insights.join('\n') : '• System appears to be running normally';
  }
}
