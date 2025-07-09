import { LogEntry, LogStats } from './types.js';

export class LogAnalyzer {
  
  generateLogSummary(logs: LogEntry[]): string {
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

  generateInsights(logs: LogEntry[]): string {
    const insights: string[] = [];
    
    const errorLogs = logs.filter(log => log.level === 'ERROR');
    if (errorLogs.length > 0) {
      insights.push(`• Found ${errorLogs.length} error(s) - requires attention`);
    }

    const commonErrors = this.findCommonPatterns(errorLogs.map(log => log.message));
    if (commonErrors.length > 0) {
      insights.push(`• Common error patterns: ${commonErrors.slice(0, 2).join(', ')}`);
    }

    if (logs.length === 0) {
      insights.push('• No logs found in specified criteria');
    }

    return insights.length > 0 ? insights.join('\n') : '• System appears to be running normally';
  }

  findCommonPatterns(messages: string[]): string[] {
    const patterns = new Map<string, number>();
    
    messages.forEach(message => {
      const keywords = message.toLowerCase().match(/\b\w{4,}\b/g) || [];
      keywords.forEach(keyword => {
        patterns.set(keyword, (patterns.get(keyword) || 0) + 1);
      });
    });

    return Array.from(patterns.entries())
      .filter(([, count]) => count > 1)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([pattern]) => pattern);
  }

  generateStats(logs: LogEntry[]): LogStats {
    const stats: LogStats = {
      totalLines: logs.length,
      errorCount: 0,
      warningCount: 0,
      infoCount: 0,
      debugCount: 0,
      sources: {},
      timeRange: {},
      patterns: [],
      health: 'good'
    };

    logs.forEach(log => {
      stats.sources[log.source] = (stats.sources[log.source] || 0) + 1;
      
      switch (log.level.toUpperCase()) {
        case 'ERROR': stats.errorCount++; break;
        case 'WARNING':
        case 'WARN': stats.warningCount++; break;
        case 'INFO': stats.infoCount++; break;
        case 'DEBUG': stats.debugCount++; break;
      }
    });

    // Calculate time range
    if (logs.length > 0) {
      const timestamps = logs.map(log => new Date(log.timestamp)).sort();
      stats.timeRange.start = timestamps[0].toISOString();
      stats.timeRange.end = timestamps[timestamps.length - 1].toISOString();
    }

    // Find patterns
    const errorLogs = logs.filter(log => log.level === 'ERROR');
    stats.patterns = this.findCommonErrorPatterns(errorLogs);

    // Determine health
    const errorRate = stats.totalLines > 0 ? stats.errorCount / stats.totalLines : 0;
    if (errorRate > 0.1) stats.health = 'critical';
    else if (errorRate > 0.05 || stats.errorCount > 50) stats.health = 'warning';
    else stats.health = 'good';

    return stats;
  }

  findCommonErrorPatterns(errorLogs: LogEntry[]): Array<{pattern: string; count: number}> {
    const patterns = new Map<string, number>();
    
    errorLogs.forEach(log => {
      const words = log.message.toLowerCase().match(/\b\w{4,}\b/g) || [];
      const meaningfulWords = words.filter(word => 
        !['error', 'failed', 'exception', 'warning'].includes(word) &&
        word.length > 3
      );
      
      meaningfulWords.forEach(word => {
        patterns.set(word, (patterns.get(word) || 0) + 1);
      });
    });

    return Array.from(patterns.entries())
      .filter(([, count]) => count > 1)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([pattern, count]) => ({ pattern, count }));
  }

  formatLogsForDisplay(logs: LogEntry[]): string {
    return logs.map(log => {
      const timeStr = new Date(log.timestamp).toLocaleTimeString();
      const levelEmoji = this.getLevelEmoji(log.level);
      return `${timeStr} ${levelEmoji} **${log.level}**: ${log.message}`;
    }).join('\n');
  }

  getLevelEmoji(level: string): string {
    switch (level.toUpperCase()) {
      case 'ERROR': return '🔴';
      case 'WARNING':
      case 'WARN': return '🟡';
      case 'INFO': return '🔵';
      case 'DEBUG': return '🟢';
      default: return '⚪';
    }
  }

  getTimeRange(logs: LogEntry[]): string {
    if (logs.length === 0) return 'No data';
    
    const timestamps = logs.map(log => new Date(log.timestamp)).sort();
    const start = timestamps[0];
    const end = timestamps[timestamps.length - 1];
    
    return `${start.toLocaleString()} - ${end.toLocaleString()}`;
  }
}
