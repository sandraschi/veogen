// Types and interfaces for the log viewer
export interface LogEntry {
  timestamp: string;
  level: string;
  source: string;
  message: string;
  rawLine: string;
  lineNumber: number;
}

export interface LogStats {
  totalLines: number;
  errorCount: number;
  warningCount: number;
  infoCount: number;
  debugCount: number;
  sources: Record<string, number>;
  timeRange: { start?: string; end?: string };
  patterns: Array<{pattern: string; count: number}>;
  health: 'good' | 'warning' | 'critical';
}

export interface TailSession {
  source: string;
  lastPosition: number;
  filter?: RegExp;
  isActive: boolean;
  startTime: Date;
}

export const CONFIG = {
  logPaths: process.env.VEOGEN_LOG_PATHS?.split(',') || [
    './logs',
    '/var/logs/veogen',
    'C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/logs',
    'C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen'
  ],
  dockerEnabled: process.env.VEOGEN_DOCKER_ENABLED !== 'false',
  maxLogLines: parseInt(process.env.MAX_LOG_LINES || '1000'),
  refreshInterval: parseInt(process.env.REFRESH_INTERVAL || '5000'),
};
