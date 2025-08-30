const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class MCPClient {
  constructor() {
    this.servers = new Map();
    this.configPath = path.join(process.env.APPDATA, '.codeium', 'windsurf-next', 'mcp_config.json');
  }

  // Load MCP server configurations from the config file
  loadConfig() {
    try {
      if (!fs.existsSync(this.configPath)) {
        console.error('MCP config file not found at:', this.configPath);
        return false;
      }
      
      const config = JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
      this.config = config.mcpServers || {};
      return true;
    } catch (error) {
      console.error('Error loading MCP config:', error);
      return false;
    }
  }

  // Start all configured MCP servers
  async startServers() {
    if (!this.loadConfig()) {
      throw new Error('Failed to load MCP configuration');
    }

    const serverPromises = [];
    
    for (const [serverName, config] of Object.entries(this.config)) {
      if (config.disabled) continue;
      
      const serverProcess = this.startServer(serverName, config);
      if (serverProcess) {
        this.servers.set(serverName, serverProcess);
        serverPromises.push(this.waitForServerReady(serverProcess, serverName));
      }
    }

    await Promise.all(serverPromises);
    return Array.from(this.servers.keys());
  }

  // Start a single MCP server
  startServer(serverName, config) {
    try {
      const { command, args = [], env = {} } = config;
      
      console.log(`Starting MCP server: ${serverName}`, { command, args });
      
      const serverProcess = spawn(command, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, ...env },
        shell: true
      });

      serverProcess.on('error', (error) => {
        console.error(`MCP Server ${serverName} error:`, error);
        this.servers.delete(serverName);
      });

      serverProcess.on('exit', (code, signal) => {
        console.log(`MCP Server ${serverName} exited with code ${code} and signal ${signal}`);
        this.servers.delete(serverName);
      });

      // Log server output
      serverProcess.stdout.on('data', (data) => {
        console.log(`[${serverName} stdout] ${data}`);
      });

      serverProcess.stderr.on('data', (data) => {
        console.error(`[${serverName} stderr] ${data}`);
      });

      return serverProcess;
    } catch (error) {
      console.error(`Failed to start MCP server ${serverName}:`, error);
      return null;
    }
  }

  // Wait for server to be ready
  waitForServerReady(serverProcess, serverName, timeout = 10000) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Timeout waiting for ${serverName} to start`));
      }, timeout);

      const onData = (data) => {
        if (data.toString().includes('Server running') || 
            data.toString().includes('Listening on')) {
          clearTimeout(timer);
          serverProcess.stdout.off('data', onData);
          console.log(`${serverName} server is ready`);
          resolve();
        }
      };

      serverProcess.stdout.on('data', onData);
    });
  }

  // Stop all MCP servers
  stopServers() {
    for (const [name, process] of this.servers.entries()) {
      console.log(`Stopping MCP server: ${name}`);
      process.kill();
    }
    this.servers.clear();
  }

  // Get list of available MCP servers
  getAvailableServers() {
    return Array.from(this.servers.keys());
  }
}

// Create a singleton instance
const mcpClient = new MCPClient();

// Handle process exit
process.on('exit', () => {
  mcpClient.stopServers();
});

// Handle Ctrl+C
process.on('SIGINT', () => {
  mcpClient.stopServers();
  process.exit();
});

module.exports = mcpClient;
