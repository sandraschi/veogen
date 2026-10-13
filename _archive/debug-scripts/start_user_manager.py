#!/usr/bin/env python3
"""
Smart User Manager Startup Script
Automatically handles port conflicts and starts cleanly
"""

import subprocess
import sys
import time
import requests
import os

def safe_print(message, level="INFO"):
    """Print with timestamp and safe characters."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Use safe ASCII characters only
    level_symbols = {
        "INFO": "[INFO]",
        "SUCCESS": "[OK]",
        "ERROR": "[ERROR]", 
        "WARN": "[WARN]"
    }
    symbol = level_symbols.get(level, "[INFO]")
    print(f"[{timestamp}] {symbol} {message}")

def check_port_free(port):
    """Check if port is free."""
    try:
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.strip().split()
                if parts:
                    return False, parts[-1]  # Return False and PID
        return True, None  # Port is free
    except Exception as e:
        safe_print(f"Error checking port {port}: {e}", "ERROR")
        return False, None

def kill_process_on_port(port):
    """Kill process using a specific port."""
    is_free, pid = check_port_free(port)
    
    if is_free:
        safe_print(f"Port {port} is already free")
        return True
    
    safe_print(f"Port {port} is in use by process {pid}")
    safe_print(f"Killing process {pid}...")
    
    try:
        result = subprocess.run(
            ['taskkill', '/PID', str(pid), '/F'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            safe_print(f"Successfully freed port {port}", "SUCCESS")
            time.sleep(1)  # Give it a moment
            return True
        else:
            safe_print(f"Failed to kill process {pid}", "ERROR")
            return False
    except Exception as e:
        safe_print(f"Error killing process: {e}", "ERROR")
        return False

def test_user_manager():
    """Test if User Manager is responding."""
    try:
        response = requests.get("http://localhost:8083/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            safe_print(f"User Manager health check: {data}", "SUCCESS")
            return True
        else:
            safe_print(f"Health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        safe_print(f"Health check error: {e}", "ERROR")
        return False

def start_user_manager():
    """Start the User Manager server."""
    safe_print("Starting VeoGen User Manager...")
    
    # Change to the correct directory
    veogen_dir = r"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"
    os.chdir(veogen_dir)
    
    try:
        # Start the server
        process = subprocess.Popen(
            [sys.executable, "user_manager_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=veogen_dir
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if it's running
        if process.poll() is None:  # Process is still running
            safe_print("User Manager started successfully", "SUCCESS")
            safe_print("Dashboard: http://localhost:8083")
            safe_print("API Docs: http://localhost:8083/docs")
            return process
        else:
            stdout, stderr = process.communicate()
            safe_print(f"Server failed to start: {stderr}", "ERROR")
            return None
            
    except Exception as e:
        safe_print(f"Failed to start server: {e}", "ERROR")
        return None

def main():
    """Main startup routine."""
    safe_print("VeoGen User Manager Smart Startup v1.0")
    safe_print("=" * 50)
    
    # Step 1: Free up port 8083
    safe_print("Step 1: Checking port 8083...")
    if not kill_process_on_port(8083):
        safe_print("Could not free port 8083. Exiting.", "ERROR")
        sys.exit(1)
    
    # Step 2: Start User Manager
    safe_print("Step 2: Starting User Manager...")
    process = start_user_manager()
    
    if not process:
        safe_print("Failed to start User Manager", "ERROR")
        sys.exit(1)
    
    # Step 3: Test the service
    safe_print("Step 3: Testing service...")
    time.sleep(2)  # Give it more time
    
    if test_user_manager():
        safe_print("User Manager is ready and working!", "SUCCESS")
        safe_print("=" * 50)
        safe_print("ACCESS POINTS:")
        safe_print("- Web Interface: http://localhost:8083")
        safe_print("- API Documentation: http://localhost:8083/docs")
        safe_print("- Health Check: http://localhost:8083/health")
        safe_print("=" * 50)
        
        # Keep the script running to monitor
        try:
            safe_print("Monitoring service... (Press Ctrl+C to stop)")
            while True:
                time.sleep(30)  # Check every 30 seconds
                if process.poll() is not None:  # Process has terminated
                    safe_print("User Manager process has stopped!", "ERROR")
                    break
                    
                # Quick health check
                if not test_user_manager():
                    safe_print("Health check failed - service may be down", "WARN")
                    
        except KeyboardInterrupt:
            safe_print("Stopping User Manager...")
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
            safe_print("User Manager stopped", "SUCCESS")
    else:
        safe_print("User Manager failed health check", "ERROR")
        if process:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
