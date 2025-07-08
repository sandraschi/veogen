#!/usr/bin/env python3
"""
Unicode-safe printing utilities for Windows compatibility
Implements RULE 19: Unicode Character Avoidance
"""

class SafePrint:
    """Windows-compatible printing with semantic indicators"""
    
    @staticmethod
    def success(message):
        """Print success message"""
        print(f"SUCCESS: {message}")
    
    @staticmethod
    def error(message):
        """Print error message"""
        print(f"ERROR: {message}")
    
    @staticmethod
    def warning(message):
        """Print warning message"""
        print(f"WARNING: {message}")
    
    @staticmethod
    def info(message):
        """Print info message"""
        print(f"INFO: {message}")
    
    @staticmethod
    def debug(message):
        """Print debug message"""
        print(f"DEBUG: {message}")
    
    @staticmethod
    def status(message, status_type="INFO"):
        """Print status message with type"""
        print(f"{status_type}: {message}")

# Convenience functions
def print_success(message):
    SafePrint.success(message)

def print_error(message):
    SafePrint.error(message)

def print_warning(message):
    SafePrint.warning(message)

def print_info(message):
    SafePrint.info(message)

# Example usage:
if __name__ == "__main__":
    print_success("Authentication working")
    print_error("Build failed")
    print_warning("Service degraded")
    print_info("Process completed")
