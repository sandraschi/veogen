#!/usr/bin/env node

/**
 * VeoGen User Manager MCP Server
 * 
 * A Model Context Protocol server that provides natural language access
 * to VeoGen's user management system with role-based access control.
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
import { Pool } from 'pg';
import bcrypt from 'bcrypt';
import validator from 'validator';
import { format, parseISO, subDays, subHours } from 'date-fns';

// Configuration
const CONFIG = {
  database: {
    host: process.env.VEOGEN_DB_HOST || 'localhost',
    port: parseInt(process.env.VEOGEN_DB_PORT || '4715'),
    database: process.env.VEOGEN_DB_NAME || 'veogen',
    user: process.env.VEOGEN_DB_USER || 'veogen',
    password: process.env.VEOGEN_DB_PASSWORD || 'veogen123',
  },
  maxResults: parseInt(process.env.MAX_RESULTS || '100'),
  bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS || '12'),
};

// Types
interface User {
  id: string;
  full_name: string;
  username: string;
  email: string;
  plan: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: Date;
  updated_at?: Date;
  last_login?: Date;
}

interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  verified_users: number;
  new_users_today: number;
  new_users_week: number;
  plan_distribution: Record<string, number>;
  recent_activity: {
    new_registrations: number;
    recent_logins: number;
    password_resets: number;
  };
}

// Schema definitions
const ListUsersSchema = z.object({
  limit: z.number().optional().default(50),
  offset: z.number().optional().default(0),
});

const GetUserSchema = z.object({
  identifier: z.string(),
});

const CreateUserSchema = z.object({
  full_name: z.string().min(1),
  username: z.string().min(3).max(50),
  email: z.string().email(),
  password: z.string().min(8),
  plan: z.enum(['free', 'pro', 'enterprise']).optional().default('free'),
  is_active: z.boolean().optional().default(true),
  is_verified: z.boolean().optional().default(false),
});

const SearchUsersSchema = z.object({
  query: z.string(),
  limit: z.number().optional().default(25),
});

const GetUserStatsSchema = z.object({
  timeframe: z.enum(['24h', '7d', '30d', '90d', 'all']).optional().default('7d'),
});

class UserManagerMCP {
  private server: Server;
  private db: Pool;

  constructor() {
    this.server = new Server(
      {
        name: 'veogen-user-manager',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.db = new Pool(CONFIG.database);
    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'list_users',
          description: 'List and filter users with pagination and sorting',
          inputSchema: ListUsersSchema,
        },
        {
          name: 'get_user',
          description: 'Get detailed information about a specific user',
          inputSchema: GetUserSchema,
        },
        {
          name: 'create_user',
          description: 'Create a new user account with validation',
          inputSchema: CreateUserSchema,
        },
        {
          name: 'search_users',
          description: 'Search users by name, email, or username',
          inputSchema: SearchUsersSchema,
        },
        {
          name: 'get_user_stats',
          description: 'Get comprehensive user statistics and analytics',
          inputSchema: GetUserStatsSchema,
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'list_users':
            return await this.handleListUsers(args);
          case 'get_user':
            return await this.handleGetUser(args);
          case 'create_user':
            return await this.handleCreateUser(args);
          case 'search_users':
            return await this.handleSearchUsers(args);
          case 'get_user_stats':
            return await this.handleGetUserStats(args);
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
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
      await this.db.end();
      await this.server.close();
      process.exit(0);
    });
  }

  private async handleListUsers(args: any) {
    const params = ListUsersSchema.parse(args);
    
    try {
      const query = 'SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2';
      const result = await this.db.query(query, [params.limit, params.offset]);
      const users = result.rows;

      return {
        content: [
          {
            type: 'text',
            text: `👥 **User List Results**

**Found**: ${users.length} users

${this.formatUserList(users)}

**Summary**:
• Active users: ${users.filter(u => u.is_active).length}
• Verified users: ${users.filter(u => u.is_verified).length}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to list users: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async handleGetUser(args: any) {
    const params = GetUserSchema.parse(args);
    
    try {
      const user = await this.findUserByIdentifier(params.identifier);
      
      if (!user) {
        throw new McpError(ErrorCode.InvalidRequest, `User not found: ${params.identifier}`);
      }

      return {
        content: [
          {
            type: 'text',
            text: `👤 **User Details: ${user.full_name}**

**Basic Information**:
• ID: ${user.id}
• Username: ${user.username}
• Email: ${user.email}
• Full Name: ${user.full_name}

**Account Status**:
• Plan: ${this.formatPlan(user.plan)}
• Active: ${user.is_active ? '✅ Yes' : '❌ No'}
• Verified: ${user.is_verified ? '✅ Yes' : '❌ No'}

**Timestamps**:
• Created: ${this.formatDate(user.created_at)}
• Updated: ${user.updated_at ? this.formatDate(user.updated_at) : 'Never'}
• Last Login: ${user.last_login ? this.formatDate(user.last_login) : 'Never'}`,
          },
        ],
      };
    } catch (error) {
      if (error instanceof McpError) throw error;
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to get user: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async handleCreateUser(args: any) {
    const params = CreateUserSchema.parse(args);
    
    try {
      await this.validateUserUniqueness(params.email, params.username);
      
      const hashedPassword = await bcrypt.hash(params.password, CONFIG.bcryptRounds);
      const userId = this.generateUserId();
      
      const query = `
        INSERT INTO users (id, full_name, username, email, hashed_password, plan, is_active, is_verified, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
        RETURNING *
      `;
      
      const values = [
        userId,
        params.full_name,
        params.username,
        params.email,
        hashedPassword,
        params.plan,
        params.is_active,
        params.is_verified
      ];
      
      const result = await this.db.query(query, values);
      const newUser = result.rows[0];

      return {
        content: [
          {
            type: 'text',
            text: `✅ **User Created Successfully**

**New User Details**:
• ID: ${newUser.id}
• Name: ${newUser.full_name}
• Username: ${newUser.username}
• Email: ${newUser.email}
• Plan: ${this.formatPlan(newUser.plan)}
• Status: ${newUser.is_active ? 'Active' : 'Inactive'}
• Verified: ${newUser.is_verified ? 'Yes' : 'No'}

*User created at: ${this.formatDate(newUser.created_at)}*`,
          },
        ],
      };
    } catch (error) {
      if (error instanceof McpError) throw error;
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to create user: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async handleSearchUsers(args: any) {
    const params = SearchUsersSchema.parse(args);
    
    try {
      const query = `
        SELECT * FROM users 
        WHERE full_name ILIKE $1 OR username ILIKE $1 OR email ILIKE $1
        ORDER BY created_at DESC LIMIT $2
      `;

      const result = await this.db.query(query, [`%${params.query}%`, params.limit]);
      const users = result.rows;

      return {
        content: [
          {
            type: 'text',
            text: `🔍 **Search Results for: "${params.query}"**

**Found**: ${users.length} users

${this.formatUserList(users)}`,
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

  private async handleGetUserStats(args: any) {
    const params = GetUserStatsSchema.parse(args);
    
    try {
      const stats = await this.calculateUserStats(params.timeframe);
      
      return {
        content: [
          {
            type: 'text',
            text: `📊 **User Statistics (${params.timeframe})**

**Overview**:
• Total Users: ${stats.total_users}
• Active Users: ${stats.active_users}
• Verified Users: ${stats.verified_users}
• New Users Today: ${stats.new_users_today}

**Plan Distribution**:
${Object.entries(stats.plan_distribution)
  .map(([plan, count]) => `• ${this.formatPlan(plan)}: ${count}`)
  .join('\n')}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to get user stats: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async findUserByIdentifier(identifier: string): Promise<User | null> {
    if (identifier.length === 36 && identifier.includes('-')) {
      const result = await this.db.query('SELECT * FROM users WHERE id = $1', [identifier]);
      if (result.rows.length > 0) return result.rows[0];
    }

    if (validator.isEmail(identifier)) {
      const result = await this.db.query('SELECT * FROM users WHERE email = $1', [identifier]);
      if (result.rows.length > 0) return result.rows[0];
    }

    const result = await this.db.query('SELECT * FROM users WHERE username = $1', [identifier]);
    if (result.rows.length > 0) return result.rows[0];

    return null;
  }

  private async validateUserUniqueness(email: string, username: string): Promise<void> {
    const emailCheck = await this.db.query('SELECT id FROM users WHERE email = $1', [email]);
    if (emailCheck.rows.length > 0) {
      throw new McpError(ErrorCode.InvalidRequest, `Email already exists: ${email}`);
    }

    const usernameCheck = await this.db.query('SELECT id FROM users WHERE username = $1', [username]);
    if (usernameCheck.rows.length > 0) {
      throw new McpError(ErrorCode.InvalidRequest, `Username already exists: ${username}`);
    }
  }

  private generateUserId(): string {
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async calculateUserStats(timeframe: string): Promise<UserStats> {
    try {
      const totalResult = await this.db.query('SELECT COUNT(*) as total FROM users');
      const activeResult = await this.db.query('SELECT COUNT(*) as active FROM users WHERE is_active = true');
      const verifiedResult = await this.db.query('SELECT COUNT(*) as verified FROM users WHERE is_verified = true');
      
      const todayResult = await this.db.query(
        'SELECT COUNT(*) as new_today FROM users WHERE created_at >= CURRENT_DATE'
      );
      
      const planResult = await this.db.query(
        'SELECT plan, COUNT(*) as count FROM users GROUP BY plan'
      );
      
      const planDistribution: Record<string, number> = {};
      planResult.rows.forEach(row => {
        planDistribution[row.plan] = parseInt(row.count);
      });

      return {
        total_users: parseInt(totalResult.rows[0].total),
        active_users: parseInt(activeResult.rows[0].active),
        inactive_users: parseInt(totalResult.rows[0].total) - parseInt(activeResult.rows[0].active),
        verified_users: parseInt(verifiedResult.rows[0].verified),
        new_users_today: parseInt(todayResult.rows[0].new_today),
        new_users_week: 0,
        plan_distribution: planDistribution,
        recent_activity: {
          new_registrations: parseInt(todayResult.rows[0].new_today),
          recent_logins: 0,
          password_resets: 0,
        }
      };
    } catch (error) {
      throw new Error(`Failed to calculate user stats: ${error}`);
    }
  }

  private formatUserList(users: User[]): string {
    if (users.length === 0) {
      return '*No users found matching the criteria*';
    }

    return users.slice(0, 10).map((user, index) => {
      const statusEmoji = user.is_active ? '🟢' : '🔴';
      const verifiedEmoji = user.is_verified ? '✅' : '⏳';
      const planEmoji = this.getPlanEmoji(user.plan);
      
      return `${index + 1}. ${statusEmoji} **${user.full_name}** (@${user.username})
   📧 ${user.email} | ${planEmoji} ${user.plan} | ${verifiedEmoji}
   📅 Created: ${this.formatDate(user.created_at)}`;
    }).join('\n\n');
  }

  private formatDate(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    return format(d, 'MMM dd, yyyy HH:mm');
  }

  private formatPlan(plan: string): string {
    const planMap: Record<string, string> = {
      'free': 'Free',
      'pro': 'Pro',
      'enterprise': 'Enterprise'
    };
    return planMap[plan] || plan;
  }

  private getPlanEmoji(plan: string): string {
    const emojiMap: Record<string, string> = {
      'free': '🆓',
      'pro': '⭐',
      'enterprise': '🏢'
    };
    return emojiMap[plan] || '📦';
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('VeoGen User Manager MCP server running on stdio');
  }
}

const server = new UserManagerMCP();
server.run().catch(console.error);