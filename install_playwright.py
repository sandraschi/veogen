import subprocess
import sys

try:
    # Try to install playwright browser
    result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                          capture_output=True, text=True, timeout=60)
    print("Playwright install output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"Error installing playwright: {e}")

# Also try alternative approach
try:
    result2 = subprocess.run(["npx", "playwright", "install", "chromium"], 
                           capture_output=True, text=True, timeout=60)
    print("\nNPX install output:")
    print(result2.stdout)
    if result2.stderr:
        print("NPX Errors:")
        print(result2.stderr)
except Exception as e:
    print(f"NPX install error: {e}")
