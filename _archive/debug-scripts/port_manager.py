#!/usr/bin/env python3
"""
Port Manager - Kill processes on specific ports before starting new ones
Solves the "something is already running at that port" problem permanently
"""

import subprocess
import sys
import time
import re
import argparse

def get_process_on_port(port):
    """Get PID of process using a specific port."""
    try:
        # Use netstat to find process on port
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        # Look for the port in the output
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                # Extract PID (last column)
                parts = line.strip().split()
                if parts:
                    return parts[-1]
        return None
    except Exception as e:
        print(f"Error checking port {port}: {e}")
        return None

def kill_process(pid):
    """Kill a process by PID."""
    try:
        result = subprocess.run(
            ['taskkill', '/PID', str(pid), '/F'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error killing process {pid}: {e}")
        return False

def free_port(port, force=False):
    """Free up a port by killing the process using it."""
    print(f"Checking port {port}...")
    
    pid = get_process_on_port(port)
    if not pid:
        print(f"Port {port} is free")
        return True
    
    print(f"Port {port} is in use by process {pid}")
    
    if not force:
        response = input(f"Kill process {pid} to free port {port}? (y/N): ")
        if response.lower() != 'y':
            print("Aborted")
            return False
    
    print(f"Killing process {pid}...")
    if kill_process(pid):
        print(f"Successfully freed port {port}")
        return True
    else:
        print(f"Failed to kill process {pid}")
        return False

def free_multiple_ports(ports, force=False):
    """Free multiple ports."""
    results = {}
    for port in ports:
        results[port] = free_port(port, force)
    return results

# Common VeoGen ports
VEOGEN_PORTS = {
    4700: "VeoGen Backend",
    4710: "VeoGen Frontend", 
    4715: "PostgreSQL",
    4720: "Redis",
    4725: "Grafana",
    4740: "Prometheus",
    8083: "User Manager"
}

def main():
    parser = argparse.ArgumentParser(description="Free up ports by killing processes")
    parser.add_argument("ports", nargs="*", type=int, help="Ports to free up")
    parser.add_argument("--force", "-f", action="store_true", help="Don't ask for confirmation")
    parser.add_argument("--veogen", action="store_true", help="Free all VeoGen ports")
    parser.add_argument("--list", "-l", action="store_true", help="List processes on VeoGen ports")
    
    args = parser.parse_args()
    
    if args.list:
        print("VeoGen Port Status:")
        print("-" * 40)
        for port, service in VEOGEN_PORTS.items():
            pid = get_process_on_port(port)
            status = f"PID {pid}" if pid else "Free"
            print(f"{port:4d} | {service:15s} | {status}")
        return
    
    if args.veogen:
        ports_to_free = [8083]  # Only User Manager, don't kill VeoGen services
        print("Freeing User Manager port...")
    elif args.ports:
        ports_to_free = args.ports
    else:
        # Default: just check port 8083
        ports_to_free = [8083]
    
    results = free_multiple_ports(ports_to_free, args.force)
    
    # Summary
    print("\nSummary:")
    for port, success in results.items():
        status = "FREED" if success else "FAILED"
        print(f"Port {port}: {status}")
    
    failed_ports = [port for port, success in results.items() if not success]
    if failed_ports:
        print(f"\nFailed to free ports: {failed_ports}")
        sys.exit(1)
    else:
        print("\nAll requested ports are now free!")
        sys.exit(0)

if __name__ == "__main__":
    main()
