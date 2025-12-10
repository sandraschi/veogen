#!/usr/bin/env python3
"""
Git add all changes script
"""
import os
import subprocess
from pathlib import Path
from typing import List

def run_git_add() -> None:
    """Run git add . in the VeoGen directory"""

    # Change to the VeoGen directory
    repo_root = Path(__file__).resolve().parent
    os.chdir(repo_root)
    
    print("📦 Adding all changes to git...")
    print(f"📍 Working directory: {os.getcwd()}")
    
    try:
        # Run git add .
        result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        
        if result.returncode == 0:
            print("✅ Successfully added all changes to git!")
            
            # Show git status
            print("\n📊 Git status:")
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            
            if status_result.returncode == 0:
                staged_files: List[str] = (
                    status_result.stdout.strip().splitlines()
                    if status_result.stdout.strip()
                    else []
                )
                if staged_files and staged_files[0]:
                    print(f"   📁 {len(staged_files)} files staged for commit")
                    for file_line in staged_files[:10]:  # Show first 10 files
                        if file_line:
                            print(f"   {file_line}")
                    if len(staged_files) > 10:
                        print(f"   ... and {len(staged_files) - 10} more files")
                else:
                    print("   📝 No changes to stage (working tree clean)")
            
            # Suggest next step
            print('\n🚀 Next step: Run \'git commit -m "Fix User Manager UUID support and rebuild frontend"\'')
            
        else:
            print("❌ Git add failed:")
            print(f"   Return code: {result.returncode}")
            print(f"   Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Git add timed out")
    except FileNotFoundError:
        print("❌ Git not found - make sure git is installed and in PATH")
    except Exception as e:
        print(f"❌ Git add failed: {e}")

if __name__ == "__main__":
    run_git_add()
