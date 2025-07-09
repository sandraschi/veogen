import { z } from 'zod';

export const ReadLogsSchema = z.object({
  source: z.string().describe("Log source (file path, Docker container, or 'auto')"),
  lines: z.number().optional().default(100),
  level: z.enum(['ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG']).optional(),
  search: z.string().optional(),
  since: z.string().optional(),
  tail: z.boolean().optional().default(false)
});

export const SearchLogsSchema = z.object({
  query: z.string().describe("Search query"),
  sources: z.array(z.string()).optional(),
  timeRange: z.string().optional(),
  contextLines: z.number().optional().default(2),
  maxResults: z.number().optional().default(100)
});

export const TailLogsSchema = z.object({
  source: z.string(),
  follow: z.boolean().optional().default(true),
  filter: z.string().optional(),
  lines: z.number().optional().default(50)
});

export const GetLogStatsSchema = z.object({
  sources: z.array(z.string()).optional(),
  timeWindow: z.string().optional().default('24h'),
  includeTrends: z.boolean().optional().default(false)
});

export const DebugVeogenSchema = z.object({
  includeDocker: z.boolean().optional().default(true),
  includePerformance: z.boolean().optional().default(true),
  quickScan: z.boolean().optional().default(false)
});

export const WatchLogsSchema = z.object({
  patterns: z.array(z.string()),
  sources: z.array(z.string()).optional(),
  alertThreshold: z.number().optional().default(5)
});

export const GetLogSourcesSchema = z.object({
  includeDocker: z.boolean().optional().default(true),
  includeSystem: z.boolean().optional().default(false),
  verifyAccess: z.boolean().optional().default(true)
});
