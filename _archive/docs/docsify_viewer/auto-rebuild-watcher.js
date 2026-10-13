#!/usr/bin/env node

/**
 * Node.js File Watcher for Docsify Sidebar Auto-Regeneration
 * Watches the windsurf-docs directory and rebuilds sidebar on changes
 */

const fs = require('fs');
const path = require('path');
const { spawn, exec } = require('child_process');

const CONFIG = {
    docsPath: './windsurf-docs',
    sidebarScript: './rebuild-sidebar.ps1',
    watchExtensions: ['.md'],
    debounceMs: 1000,
    verbose: process.argv.includes('--verbose') || process.argv.includes('-v')
};

class SidebarWatcher {
    constructor() {
        this.rebuildTimeout = null;
        this.lastRebuild = 0;
        this.watching = false;
    }

    log(message, level = 'INFO') {
        const timestamp = new Date().toISOString().replace('T', ' ').substr(0, 19);
        const colors = {
            INFO: '\x1b[36m',    // Cyan
            SUCCESS: '\x1b[32m', // Green
            WARNING: '\x1b[33m', // Yellow
            ERROR: '\x1b[31m',   // Red
            RESET: '\x1b[0m'     // Reset
        };
        
        console.log(`${colors[level]}[${timestamp}] [${level}] ${message}${colors.RESET}`);
    }

    async checkPrerequisites() {
        // Check if docs directory exists
        if (!fs.existsSync(CONFIG.docsPath)) {
            this.log(`Docs path not found: ${CONFIG.docsPath}`, 'ERROR');
            this.log('Make sure the windsurf-docs symbolic link is created', 'ERROR');
            return false;
        }

        // Check if rebuild script exists
        if (!fs.existsSync(CONFIG.sidebarScript)) {
            this.log(`Rebuild script not found: ${CONFIG.sidebarScript}`, 'ERROR');
            return false;
        }

        this.log('Prerequisites check passed', 'SUCCESS');
        return true;
    }

    async rebuildSidebar() {
        const now = Date.now();
        if (now - this.lastRebuild < CONFIG.debounceMs) {
            this.log('Rebuild request debounced', 'INFO');
            return;
        }

        this.lastRebuild = now;
        this.log('Rebuilding sidebar...', 'INFO');

        try {
            const result = await this.execPowerShell(CONFIG.sidebarScript);
            this.log('Sidebar rebuilt successfully', 'SUCCESS');
            if (CONFIG.verbose) {
                this.log(`PowerShell output: ${result}`, 'INFO');
            }
        } catch (error) {
            this.log(`Sidebar rebuild failed: ${error.message}`, 'ERROR');
        }
    }

    execPowerShell(scriptPath) {
        return new Promise((resolve, reject) => {
            const powershell = spawn('powershell', [
                '-ExecutionPolicy', 'Bypass',
                '-File', scriptPath
            ]);

            let output = '';
            let errorOutput = '';

            powershell.stdout.on('data', (data) => {
                output += data.toString();
            });

            powershell.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });

            powershell.on('close', (code) => {
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(`PowerShell exit code ${code}: ${errorOutput}`));
                }
            });

            powershell.on('error', (error) => {
                reject(new Error(`Failed to start PowerShell: ${error.message}`));
            });
        });
    }

    shouldWatchFile(filename) {
        const ext = path.extname(filename).toLowerCase();
        return CONFIG.watchExtensions.includes(ext);
    }

    setupWatcher() {
        this.log(`Starting file watcher for: ${CONFIG.docsPath}`, 'INFO');
        this.log(`Watching extensions: ${CONFIG.watchExtensions.join(', ')}`, 'INFO');
        this.log('Press Ctrl+C to stop', 'INFO');

        try {
            const watcher = fs.watch(CONFIG.docsPath, { recursive: true }, (eventType, filename) => {
                if (!filename || !this.shouldWatchFile(filename)) {
                    return;
                }

                if (CONFIG.verbose) {
                    this.log(`File ${eventType}: ${filename}`, 'INFO');
                }

                // Debounce rebuild requests
                if (this.rebuildTimeout) {
                    clearTimeout(this.rebuildTimeout);
                }

                this.rebuildTimeout = setTimeout(() => {
                    this.rebuildSidebar();
                }, CONFIG.debounceMs);
            });

            this.watching = true;

            // Handle graceful shutdown
            process.on('SIGINT', () => {
                this.log('Stopping file watcher...', 'INFO');
                watcher.close();
                this.watching = false;
                process.exit(0);
            });

            // Keep the process alive
            const keepAlive = setInterval(() => {
                if (!this.watching) {
                    clearInterval(keepAlive);
                }
            }, 1000);

        } catch (error) {
            this.log(`Failed to setup file watcher: ${error.message}`, 'ERROR');
            throw error;
        }
    }

    async start() {
        this.log('=== Docsify Sidebar Auto-Rebuilder ===', 'INFO');
        
        if (!(await this.checkPrerequisites())) {
            process.exit(1);
        }

        // Initial rebuild
        await this.rebuildSidebar();

        // Start watching
        this.setupWatcher();
    }
}

// Main execution
if (require.main === module) {
    const watcher = new SidebarWatcher();
    watcher.start().catch(error => {
        console.error('Failed to start sidebar watcher:', error);
        process.exit(1);
    });
}

module.exports = SidebarWatcher;
