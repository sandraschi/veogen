#!/usr/bin/env node

/**
 * VeoGen Log Viewer MCP Server
 * 
 * A Model Context Protocol server that provides natural language access
 * to VeoGen's logging system for intelligent debugging and monitoring.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import { glob } from 'glob';
import { parseISO, subHours, isAfter } from 'date-fns';

const execAsync = promisify(exec);
// Configuration
const CONFIG = {
  logPaths: process.env.VEOGEN_LOG_PATHS?.split(',') || [
    './logs',
    '/var/logs/veogen',
    'C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/logs'
  ],
  dockerEnabled: process.env.VEOGEN_DOCKER_ENABLED !== 'false',
  maxLogLines: parseInt(process.env.MAX_LOG_LINES || '1000'),
  tailBufferSize: parseInt(process.env.TAIL_BUFFER_SIZE || '500'),
};

// Types
interface LogEntry {
  timestamp: string;
  level: string;
  source: string;
  message: string;
  rawLine: string;
  lineNumber: number;
}

interface LogStats {
  totalLines: number;
  errorCount: number;
  warningCount: number;
  infoCount: number;
  debugCount: number;
  sources: Record<string, number>;
  timeRange: {
    start?: string;
    end?: string;
  };
}

// Schema definitions
const ReadLogsSchema = z.object({
  source: z.string().describe("Log source (file path, Docker container, or 'auto' for intelligent selection)"),
  lines: z.number().optional().default(100).describe("Number of lines to read (max 1000)"),
  level: z.enum(['ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG']).optional().describe("Filter by log level"),
  search: z.string().optional().describe("Search term or regex pattern"),
  since: z.string().optional().describe("Time filter: '1h', '30m', '2024-01-01', or ISO timestamp"),
  tail: z.boolean().optional().default(false).describe("Read from end of file (most recent first)")
});
const SearchLogsSchema = z.object({
  query: z.string().describe("Search query (supports regex and natural language)"),
  sources: z.array(z.string()).optional().describe("Specific sources to search (empty = all sources)"),
  timeRange: z.string().optional().describe("Time range: '1h', '24h', '7d', or ISO date range"),
  contextLines: z.number().optional().default(2).describe("Include surrounding lines for context"),
  maxResults: z.number().optional().default(100).describe("Maximum results to return")
});

const TailLogsSchema = z.object({
  source: z.string().describe("Log source to monitor"),
  follow: z.boolean().optional().default(true).describe("Continue following new entries"),
  filter: z.string().optional().describe("Filter pattern for relevant entries"),
  lines: z.number().optional().default(50).describe("Initial lines to show")
});

const GetLogStatsSchema = z.object({
  sources: z.array(z.string()).optional().describe("Sources to analyze (empty = all sources)"),
  timeWindow: z.string().optional().default('24h').describe("Analysis window: '1h', '24h', '7d'"),
  includeTrends: z.boolean().optional().default(false).describe("Include trend analysis")
});

const DebugVeogenSchema = z.object({
  includeDocker: z.boolean().optional().default(true).describe("Include Docker container status"),
  includePerformance: z.boolean().optional().default(true).describe("Include performance metrics"),
  quickScan: z.boolean().optional().default(false).describe("Quick health check vs full analysis")
});

const WatchLogsSchema = z.object({
  patterns: z.array(z.string()).describe("Patterns to watch for (regex or keywords)"),
  sources: z.array(z.string()).optional().describe("Sources to monitor (empty = all)"),
  alertThreshold: z.number().optional().default(5).describe("Alert when pattern occurs N times in 5 minutes")
});

const GetLogSourcesSchema = z.object({
  includeDocker: z.boolean().optional().default(true).describe("Include Docker containers"),
  includeSystem: z.boolean().optional().default(false).describe("Include system logs"),
  verifyAccess: z.boolean().optional().default(true).describe("Check read permissions")
});

class LogViewerMCP {
  private server: Server;
  private logCache = new Map<string, LogEntry[]>();
  private watchPatterns = new Map<string, RegExp[]>();

  constructor() {
    this.server = new Server(
      {
        name: 'veogen-log-viewer',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'read_logs',
          description: 'Read log entries from specified sources with intelligent filtering and parsing',
          inputSchema: ReadLogsSchema,
        },
        {
          name: 'search_logs',
          description: 'Search across multiple log sources with advanced pattern matching and context',
          inputSchema: SearchLogsSchema,
        },
        {
          name: 'tail_logs',
          description: 'Monitor logs in real-time with live updates and filtering',
          inputSchema: TailLogsSchema,
        },
        {
          name: 'get_log_stats',
          description: 'Get comprehensive statistics, trends, and health metrics from logs',
          inputSchema: GetLogStatsSchema,
        },
        {
          name: 'debug_veogen',
          description: 'Comprehensive VeoGen system debugging and health check with intelligent analysis',
          inputSchema: DebugVeogenSchema,
        },
        {
          name: 'watch_logs',
          description: 'Set up intelligent log monitoring with custom alerts and pattern detection',
          inputSchema: WatchLogsSchema,
        },
        {
          name: 'get_log_sources',
          description: 'Discover and list all available log sources with metadata and access verification',
          inputSchema: GetLogSourcesSchema,
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'read_logs':
            return await this.handleReadLogs(args);
          case 'search_logs':
            return await this.handleSearchLogs(args);
          case 'tail_logs':
            return await this.handleTailLogs(args);
          case 'get_log_stats':
            return await this.handleGetLogStats(args);
          case 'debug_veogen':
            return await this.handleDebugVeogen(args);
          case 'watch_logs':
            return await this.handleWatchLogs(args);
          case 'get_log_sources':
            return await this.handleGetLogSources(args);
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    });
  }

  private setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  // CORE IMPLEMENTATION METHODS
  private async handleReadLogs(args: any) {
    const params = ReadLogsSchema.parse(args);
    
    try {
      if (params.source === 'auto') {
        params.source = await this.detectBestLogSource();
      }

      const logs = await this.readLogsFromSource(
        params.source,
        params.lines,
        params.level,
        params.search,
        params.since,
        params.tail
      );

      const summary = this.generateLogSummary(logs);
      const insights = this.generateInsights(logs);
      
      return {
        content: [
          {
            type: 'text',
            text: `📊 **Log Analysis Results**

**Source**: ${params.source}
**Lines Retrieved**: ${logs.length}
**Time Range**: ${this.getTimeRange(logs)}

${summary}

**Key Insights**:
${insights}

**Recent Entries**:
${this.formatLogsForDisplay(logs.slice(-Math.min(15, logs.length)))}

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

  private async handleSearchLogs(args: any) {
    const params = SearchLogsSchema.parse(args);
    
    try {
      const sources = params.sources?.length ? params.sources : await this.getAllLogSources();
      const allResults: LogEntry[] = [];
      
      for (const source of sources.slice(0, 5)) { // Limit to 5 sources
        try {
          const logs = await this.searchInSource(source, params.query, params.timeRange);
          allResults.push(...logs);
        } catch (error) {
          console.warn(`Failed to search in ${source}: ${error}`);
        }
      }

      const sortedResults = this.rankSearchResults(allResults, params.query)
        .slice(0, params.maxResults);

      const patterns = this.analyzePatterns(sortedResults);
      
      return {
        content: [
          {
            type: 'text',
            text: `🔍 **Search Results for: "${params.query}"**

**Found**: ${sortedResults.length} matches across ${sources.length} sources
**Time Range**: ${this.getTimeRange(sortedResults)}

**Top Results**:
${this.formatSearchResults(sortedResults.slice(0, 10))}

**Pattern Analysis**:
${patterns}

**Recommendations**:
${this.generateRecommendations(sortedResults)}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Search failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async handleDebugVeogen(args: any) {
    const params = DebugVeogenSchema.parse(args);
    
    try {
      const systemHealth = await this.checkSystemHealth();
      const services = await this.checkVeogenServices();
      const recentErrors = await this.getRecentCriticalErrors();
      const dockerStatus = params.includeDocker ? await this.getDockerStatus() : null;
      
      const healthScore = this.calculateHealthScore({
        systemHealth,
        services,
        recentErrors,
        dockerStatus
      });

      return {
        content: [
          {
            type: 'text',
            text: `🔧 **VeoGen System Debug Report**

**System Health Score**: ${healthScore}/100 ${this.getHealthEmoji(healthScore)}

**Service Status**:
${this.formatServiceStatus(services)}

**Recent Critical Issues** (Last 1 hour):
${recentErrors.length > 0 ? 
  this.formatCriticalErrors(recentErrors) : 
  '✅ No critical errors detected'}

${dockerStatus ? `**Docker Status**:\n${this.formatDockerStatus(dockerStatus)}` : ''}

**Health Summary**:
${this.generateHealthSummary(healthScore, services, recentErrors)}

**Next Steps**:
${this.suggestNextSteps(healthScore, recentErrors)}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Debug analysis failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  // REAL LOG READING IMPLEMENTATION
  private async readLogsFromSource(
    source: string, 
    lines: number, 
    level?: string, 
    search?: string, 
    since?: string, 
    tail: boolean = false
  ): Promise<LogEntry[]> {
    
    try {
      let logEntries: LogEntry[] = [];

      if (source.startsWith('docker/')) {
        logEntries = await this.readDockerLogs(source.substring(7), lines, tail);
      } else {
        logEntries = await this.readFileLogsDirect(source, lines, tail);
      }

      // Apply filters
      if (level) {
        logEntries = logEntries.filter(entry => 
          entry.level.toLowerCase() === level.toLowerCase()
        );
      }

      if (search) {
        const searchRegex = new RegExp(search, 'i');
        logEntries = logEntries.filter(entry => 
          searchRegex.test(entry.message) || searchRegex.test(entry.rawLine)
        );
      }

      if (since) {
        const sinceDate = this.parseTimeFilter(since);
        logEntries = logEntries.filter(entry => 
          new Date(entry.timestamp) >= sinceDate
        );
      }

      return logEntries.slice(0, Math.min(lines, CONFIG.maxLogLines));

    } catch (error) {
      throw new Error(`Failed to read from source ${source}: ${error}`);
    }
  }

  private async readDockerLogs(containerName: string, lines: number, tail: boolean): Promise<LogEntry[]> {
    try {
      const cmd = [
        'docker', 'logs',
        tail ? '--tail' : '--since', 
        tail ? lines.toString() : '24h',
        '--timestamps',
        containerName
      ];

      const { stdout, stderr } = await execAsync(cmd.join(' '));
      
      if (stderr && !stdout) {
        throw new Error(`Docker logs error: ${stderr}`);
      }

      const lines_array = stdout.split('\n').filter(line => line.trim());
      
      return lines_array.map((line, index) => this.parseLogLine(line, `docker/${containerName}`, index + 1))
        .filter((entry): entry is LogEntry => entry !== null);

    } catch (error) {
      throw new Error(`Failed to read Docker logs for ${containerName}: ${error}`);
    }
  }

  private async readFileLogsDirect(source: string, lines: number, tail: boolean): Promise<LogEntry[]> {
    try {
      // Find the actual file path
      const filePath = await this.resolveLogFilePath(source);
      
      if (!filePath) {
        throw new Error(`Log file not found: ${source}`);
      }

      // Read file content
      const content = await fs.readFile(filePath, 'utf-8');
      const fileLines = content.split('\n').filter(line => line.trim());

      // Get the lines we want
      const startIndex = tail ? Math.max(0, fileLines.length - lines) : 0;
      const endIndex = tail ? fileLines.length : Math.min(lines, fileLines.length);
      const selectedLines = fileLines.slice(startIndex, endIndex);

      return selectedLines.map((line, index) => 
        this.parseLogLine(line, source, startIndex + index + 1)
      ).filter((entry): entry is LogEntry => entry !== null);

    } catch (error) {
      throw new Error(`Failed to read file logs from ${source}: ${error}`);
    }
  }

  private async resolveLogFilePath(source: string): Promise<string | null> {
    // Try each configured log path
    for (const logPath of CONFIG.logPaths) {
      try {
        const fullPath = path.resolve(logPath, source);
        await fs.access(fullPath);
        return fullPath;
      } catch {
        // Try next path
      }
      
      // Also try treating source as absolute path
      try {
        await fs.access(source);
        return source;
      } catch {
        // Continue
      }
    }
    
    return null;
  }

  private parseLogLine(line: string, source: string, lineNumber: number): LogEntry | null {
    if (!line.trim()) return null;

    // Extract timestamp
    let timestamp = new Date().toISOString();
    const timestampPatterns = [
      /(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?)/,  // ISO format
      /(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/,                 // Standard format
      /(\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2})/                // US format
    ];

    for (const pattern of timestampPatterns) {
      const match = line.match(pattern);
      if (match) {
        try {
          timestamp = new Date(match[1]).toISOString();
          break;
        } catch {
          // Invalid date, keep trying
        }
      }
    }

    // Extract log level
    let level = 'INFO';
    const levelPatterns = [
      /\b(ERROR|ERRO|ERR)\b/i,
      /\b(WARN|WARNING)\b/i,
      /\b(INFO|INFORMATION)\b/i,
      /\b(DEBUG|DBG)\b/i,
      /\b(TRACE|TRC)\b/i
    ];

    for (const pattern of levelPatterns) {
      const match = line.match(pattern);
      if (match) {
        level = match[1].toUpperCase();
        if (level === 'ERRO' || level === 'ERR') level = 'ERROR';
        if (level === 'WARN') level = 'WARNING';
        break;
      }
    }

    // Extract message (everything after timestamp and level)
    let message = line;
    const messageMatch = line.match(/(?:\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\s]*\s*)?(?:ERROR|WARN|INFO|DEBUG|TRACE)?\s*[-:]?\s*(.+)$/i);
    if (messageMatch) {
      message = messageMatch[1].trim();
    }

    return {
      timestamp,
      level,
      source,
      message,
      rawLine: line,
      lineNumber
    };
  }
  // UTILITY METHODS
  private async detectBestLogSource(): Promise<string> {
    const sources = await this.getAllLogSources();
    
    // Prioritize VeoGen specific logs
    const priorities = [
      'veogen-backend-1',
      'veogen-frontend-1', 
      'docker/veogen-backend-1',
      'docker/veogen-frontend-1',
      'backend.log',
      'frontend.log',
      'app.log'
    ];

    for (const priority of priorities) {
      if (sources.includes(priority)) {
        return priority;
      }
    }

    return sources[0] || 'docker/veogen-backend-1';
  }

  private async getAllLogSources(): Promise<string[]> {
    const sources: string[] = [];
    
    // Docker containers
    if (CONFIG.dockerEnabled) {
      try {
        const { stdout } = await execAsync('docker ps --format "{{.Names}}"');
        const containers = stdout.split('\n').filter(name => name.trim());
        sources.push(...containers.map(name => `docker/${name}`));
      } catch (error) {
        console.warn('Failed to get Docker containers:', error);
      }
    }

    // Log files
    for (const logPath of CONFIG.logPaths) {
      try {
        const pattern = path.join(logPath, '**/*.log');
        const files = await glob(pattern);
        sources.push(...files);
      } catch (error) {
        console.warn(`Failed to scan log path ${logPath}:`, error);
      }
    }

    return [...new Set(sources)];
  }

  private generateLogSummary(logs: LogEntry[]): string {
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

  private generateInsights(logs: LogEntry[]): string {
    const insights: string[] = [];
    
    const errorLogs = logs.filter(log => log.level === 'ERROR');
    if (errorLogs.length > 0) {
      insights.push(`• Found ${errorLogs.length} error(s) - requires attention`);
    }

    const commonErrors = this.findCommonPatterns(errorLogs.map(log => log.message));
    if (commonErrors.length > 0) {
      insights.push(`• Common error patterns detected: ${commonErrors.slice(0, 2).join(', ')}`);
    }

    if (logs.length === 0) {
      insights.push('• No logs found in specified criteria');
    }

    return insights.length > 0 ? insights.join('\n') : '• System appears to be running normally';
  }

  private findCommonPatterns(messages: string[]): string[] {
    const patterns = new Map<string, number>();
    
    messages.forEach(message => {
      // Simple keyword extraction
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

  private formatLogsForDisplay(logs: LogEntry[]): string {
    return logs.map(log => {
      const timeStr = new Date(log.timestamp).toLocaleTimeString();
      const levelEmoji = this.getLevelEmoji(log.level);
      return `${timeStr} ${levelEmoji} **${log.level}**: ${log.message}`;
    }).join('\n');
  }

  private getLevelEmoji(level: string): string {
    switch (level.toUpperCase()) {
      case 'ERROR': return '🔴';
      case 'WARNING':
      case 'WARN': return '🟡';
      case 'INFO': return '🔵';
      case 'DEBUG': return '🟢';
      default: return '⚪';
    }
  }

  private getTimeRange(logs: LogEntry[]): string {
    if (logs.length === 0) return 'No data';
    
    const timestamps = logs.map(log => new Date(log.timestamp)).sort();
    const start = timestamps[0];
    const end = timestamps[timestamps.length - 1];
    
    return `${start.toLocaleString()} - ${end.toLocaleString()}`;
  }

  private parseTimeFilter(since: string): Date {
    const now = new Date();
    
    // Handle relative time formats
    const relativeMatch = since.match(/^(\d+)([hmds])$/);
    if (relativeMatch) {
      const [, amount, unit] = relativeMatch;
      const minutes = parseInt(amount) * {
        's': 1/60,
        'm': 1,
        'h': 60,
        'd': 1440
      }[unit as 's'|'m'|'h'|'d']!;
      
      return new Date(now.getTime() - minutes * 60 * 1000);
    }

    // Handle ISO timestamps or date strings
    try {
      return new Date(since);
    } catch {
      return subHours(now, 1); // Default to 1 hour ago
    }
  }

  // Stub implementations for remaining methods
  private async handleTailLogs(args: any) {
    const params = TailLogsSchema.parse(args);
    return {
      content: [{
        type: 'text',
        text: `🔄 **Monitoring ${params.source}**\n\n⚠️ Real-time log monitoring not yet implemented.\nUse 'read_logs' with tail=true for recent entries.`
      }]
    };
  }

  private async handleGetLogStats(args: any) {
    const params = GetLogStatsSchema.parse(args);
    const sources = params.sources || await this.getAllLogSources();
    
    return {
      content: [{
        type: 'text',
        text: `📈 **Log Statistics**\n\n**Sources Analyzed**: ${sources.length}\n**Time Window**: ${params.timeWindow}\n\n⚠️ Detailed statistics analysis not yet implemented.`
      }]
    };
  }

  private async handleWatchLogs(args: any) {
    return {
      content: [{
        type: 'text',
        text: `👁️ **Log Watching**\n\n⚠️ Pattern watching not yet implemented.\nUse 'search_logs' for one-time pattern searches.`
      }]
    };
  }

  private async handleGetLogSources(args: any) {
    const params = GetLogSourcesSchema.parse(args);
    const sources = await this.getAllLogSources();
    
    return {
      content: [{
        type: 'text',
        text: `📁 **Available Log Sources**\n\n${sources.map(source => `• ${source}`).join('\n')}\n\n**Total**: ${sources.length} sources found`
      }]
    };
  }

  private async searchInSource(source: string, query: string, timeRange?: string): Promise<LogEntry[]> {
    const logs = await this.readLogsFromSource(source, 1000, undefined, query, timeRange);
    return logs;
  }

  private rankSearchResults(results: LogEntry[], query: string): LogEntry[] {
    return results.sort((a, b) => {
      const aScore = this.calculateRelevanceScore(a, query);
      const bScore = this.calculateRelevanceScore(b, query);
      return bScore - aScore;
    });
  }

  private calculateRelevanceScore(entry: LogEntry, query: string): number {
    let score = 0;
    const queryLower = query.toLowerCase();
    const messageLower = entry.message.toLowerCase();
    
    if (messageLower.includes(queryLower)) score += 10;
    if (entry.level === 'ERROR') score += 5;
    if (entry.level === 'WARNING') score += 3;
    
    return score;
  }

  private analyzePatterns(results: LogEntry[]): string {
    const sources = new Set(results.map(r => r.source));
    const levels = results.reduce((acc, r) => {
      acc[r.level] = (acc[r.level] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return `• Sources involved: ${Array.from(sources).join(', ')}\n• Level distribution: ${Object.entries(levels).map(([k, v]) => `${k}:${v}`).join(', ')}`;
  }

  private formatSearchResults(results: LogEntry[]): string {
    return results.slice(0, 10).map((result, i) => {
      const time = new Date(result.timestamp).toLocaleTimeString();
      return `${i + 1}. [${time}] ${this.getLevelEmoji(result.level)} ${result.message}`;
    }).join('\n');
  }

  private generateRecommendations(results: LogEntry[]): string {
    const errorCount = results.filter(r => r.level === 'ERROR').length;
    
    if (errorCount > 10) {
      return '• High error count detected - investigate error patterns\n• Consider reviewing recent deployments or configuration changes';
    } else if (errorCount > 0) {
      return '• Some errors found - monitor these patterns\n• Check if errors are recurring or one-time issues';
    }
    
    return '• No critical issues found in search results\n• System appears stable for the searched criteria';
  }

  private async checkSystemHealth(): Promise<any> {
    return { status: 'unknown', message: 'Health check not implemented' };
  }

  private async checkVeogenServices(): Promise<any[]> {
    try {
      const { stdout } = await execAsync('docker-compose ps --format json');
      return JSON.parse(`[${stdout.split('\n').filter(l => l.trim()).join(',')}]`);
    } catch {
      return [];
    }
  }

  private async getRecentCriticalErrors(): Promise<LogEntry[]> {
    try {
      const logs = await this.readLogsFromSource('auto', 1000, 'ERROR', undefined, '1h');
      return logs.filter(log => log.level === 'ERROR');
    } catch {
      return [];
    }
  }

  private async getDockerStatus(): Promise<any> {
    try {
      const { stdout } = await execAsync('docker system df');
      return { summary: stdout };
    } catch {
      return null;
    }
  }

  private calculateHealthScore(data: any): number {
    let score = 100;
    if (data.recentErrors.length > 10) score -= 30;
    else if (data.recentErrors.length > 5) score -= 15;
    else if (data.recentErrors.length > 0) score -= 5;
    
    return Math.max(0, score);
  }

  private getHealthEmoji(score: number): string {
    if (score >= 90) return '🟢';
    if (score >= 70) return '🟡';
    return '🔴';
  }

  private formatServiceStatus(services: any[]): string {
    if (services.length === 0) return '⚠️ No services detected';
    
    return services.map(service => {
      const name = service.Name || service.name || 'Unknown';
      const status = service.State || service.status || 'Unknown';
      const emoji = status.includes('Up') || status.includes('running') ? '🟢' : '🔴';
      return `${emoji} ${name}: ${status}`;
    }).join('\n');
  }

  private formatCriticalErrors(errors: LogEntry[]): string {
    return errors.slice(0, 5).map(error => {
      const time = new Date(error.timestamp).toLocaleTimeString();
      return `🔴 [${time}] ${error.message}`;
    }).join('\n');
  }

  private formatDockerStatus(status: any): string {
    return '🐳 Docker system information:\n' + (status.summary || 'Status unavailable');
  }

  private generateHealthSummary(score: number, services: any[], errors: LogEntry[]): string {
    if (score >= 90) {
      return '✅ System is running well with no major issues detected.';
    } else if (score >= 70) {
      return '⚠️ System is mostly stable but has some issues that should be monitored.';
    } else {
      return '🚨 System has significant issues that require immediate attention.';
    }
  }

  private suggestNextSteps(score: number, errors: LogEntry[]): string {
    const steps: string[] = [];
    
    if (errors.length > 0) {
      steps.push('• Investigate recent error patterns using search_logs');
      steps.push('• Check specific service logs for failing components');
    }
    
    if (score < 80) {
      steps.push('• Monitor system resources and performance');
      steps.push('• Review recent configuration or deployment changes');
    }
    
    if (steps.length === 0) {
      steps.push('• Continue regular monitoring');
      steps.push('• System appears stable - maintain current operations');
    }
    
    return steps.join('\n');
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('VeoGen Log Viewer MCP server running on stdio');
  }
}

const server = new LogViewerMCP();
server.run().catch(console.error);