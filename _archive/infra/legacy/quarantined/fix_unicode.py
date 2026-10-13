#!/usr/bin/env python3
"""
Fix Unicode characters in Python files to be Windows-compatible
Implements RULE 19: Unicode Character Avoidance
"""
import os
import re
from pathlib import Path

# Project root
PROJECT_ROOT = Path(r"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen")

# Unicode replacements
UNICODE_REPLACEMENTS = {
    '✅': 'SUCCESS',
    '❌': 'ERROR', 
    '🎉': 'CELEBRATION',
    '📁': 'FOLDER',
    '⚠️': 'WARNING',
    '🗄️': 'DATABASE',
    '🔧': 'TOOLS',
    '🚀': 'LAUNCH',
    '💻': 'COMPUTER',
    '📊': 'CHART',
    '🔐': 'SECURITY',
    '🎯': 'TARGET',
    '⭐': 'STAR',
    '🔥': 'FIRE',
    '💡': 'IDEA',
    '🎪': 'CIRCUS',
    '🍺': 'BEER'
}

def fix_unicode_in_file(file_path):
    """Fix Unicode characters in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Replace Unicode characters in print statements
        for unicode_char, replacement in UNICODE_REPLACEMENTS.items():
            if unicode_char in content:
                # More sophisticated replacement that preserves context
                pattern = rf'print\([^)]*{re.escape(unicode_char)}[^)]*\)'
                
                def replace_in_print(match):
                    print_statement = match.group(0)
                    new_statement = print_statement.replace(unicode_char, replacement + ':')
                    return new_statement
                
                new_content = re.sub(pattern, replace_in_print, content)
                if new_content != content:
                    content = new_content
                    changes_made.append(f"{unicode_char} -> {replacement}")
        
        # Write back if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"FIXED: {file_path.name}")
            for change in changes_made:
                print(f"  - {change}")
            return True
        else:
            print(f"OK: {file_path.name} - no Unicode issues")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not process {file_path}: {e}")
        return False

def find_python_files():
    """Find all Python files in the project"""
    python_files = []
    
    # Look for .py files
    for py_file in PROJECT_ROOT.glob("*.py"):
        python_files.append(py_file)
    
    # Look in subdirectories
    for subdir in ["backend", "frontend", "monitoring"]:
        subdir_path = PROJECT_ROOT / subdir
        if subdir_path.exists():
            python_files.extend(subdir_path.rglob("*.py"))
    
    return python_files

def create_unicode_safe_functions():
    """Create a utility file with Unicode-safe printing functions"""
    
    safe_print_content = '''#!/usr/bin/env python3
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
'''
    
    safe_print_path = PROJECT_ROOT / "unicode_safe_print.py"
    with open(safe_print_path, 'w', encoding='utf-8') as f:
        f.write(safe_print_content)
    
    print(f"CREATED: {safe_print_path}")
    return safe_print_path

def main():
    """Main function to fix Unicode issues"""
    
    print("=" * 60)
    print("  UNICODE SAFETY FIX - RULE 19 IMPLEMENTATION")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    
    # Find Python files
    python_files = find_python_files()
    print(f"\nFOUND: {len(python_files)} Python files to check")
    
    # Fix Unicode issues
    files_fixed = 0
    for py_file in python_files:
        if py_file.name.startswith('.'):
            continue  # Skip hidden files
        
        if fix_unicode_in_file(py_file):
            files_fixed += 1
    
    # Create safe printing utilities
    create_unicode_safe_functions()
    
    # Summary
    print("\n" + "=" * 60)
    print("  UNICODE SAFETY SUMMARY")
    print("=" * 60)
    
    if files_fixed > 0:
        print(f"FIXED: {files_fixed} files had Unicode issues")
    else:
        print("SUCCESS: No Unicode issues found")
    
    print("\nRECOMMENDATIONS:")
    print("1. Use unicode_safe_print.py for future scripts")
    print("2. Always test scripts on Windows")
    print("3. Use text indicators instead of Unicode symbols")
    
    print(f"\nProject: {PROJECT_ROOT}")
    print("Rule 19: Unicode Character Avoidance - IMPLEMENTED")

if __name__ == "__main__":
    main()
