import fs from 'fs/promises';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import { glob } from 'glob';
import { LogEntry, CONFIG } from './types.js';

const execAsync = promisify(exec);

export class LogReader {
  
  async readLogsFromSource(
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

  async readDockerLogs(containerName: string, lines: number, tail: boolean): Promise<LogEntry[]> {
    try {
      const cmd = `docker logs ${tail ? '--tail ' + lines : '--since 24h'} --timestamps ${containerName}`;
      const { stdout, stderr } = await execAsync(cmd);
      
      if (stderr && !stdout) {
        throw new Error(`Docker logs error: ${stderr}`);
      }

      const logLines = stdout.split('\n').filter(line => line.trim());
      
      return logLines.map((line, index) => this.parseLogLine(line, `docker/${containerName}`, index + 1))
        .filter((entry): entry is LogEntry => entry !== null);

    } catch (error) {
      throw new Error(`Failed to read Docker logs for ${containerName}: ${error}`);
    }
  }

  async readFileLogsDirect(source: string, lines: number, tail: boolean): Promise<LogEntry[]> {
    try {
      const filePath = await this.resolveLogFilePath(source);
      
      if (!filePath) {
        throw new Error(`Log file not found: ${source}`);
      }

      const content = await fs.readFile(filePath, 'utf-8');
      const fileLines = content.split('\n').filter(line => line.trim());

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

  async resolveLogFilePath(source: string): Promise<string | null> {
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

  parseLogLine(line: string, source: string, lineNumber: number): LogEntry | null {
    if (!line.trim()) return null;

    // Extract timestamp
    let timestamp = new Date().toISOString();
    const timestampPatterns = [
      /(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?)/,
      /(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/,
      /(\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2})/
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
      /\b(DEBUG|DBG)\b/i
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

    // Extract message
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

  parseTimeFilter(since: string): Date {
    const now = new Date();
    
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

    try {
      return new Date(since);
    } catch {
      return new Date(now.getTime() - 60 * 60 * 1000); // Default to 1 hour ago
    }
  }
}
