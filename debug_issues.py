# Fix 1: Add logs router import check
print("Checking logs router...")
import sys
import os
sys.path.append("C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/backend")

try:
    from app.api.api_v1.endpoints import logs
    print("✅ Logs module imported successfully")
    print(f"Router object: {logs.router}")
    print(f"Router routes: {[route.path for route in logs.router.routes]}")
except Exception as e:
    print(f"❌ Error importing logs: {e}")

# Fix 2: Check docsify path
app_dir = "C:/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen/backend/app"
docsify_path = os.path.join(os.path.dirname(os.path.dirname(app_dir)), "docsify_viewer")
print(f"\nDocsify path calculation:")
print(f"app_dir: {app_dir}")
print(f"dirname(app_dir): {os.path.dirname(app_dir)}")
print(f"dirname(dirname(app_dir)): {os.path.dirname(os.path.dirname(app_dir))}")
print(f"Final docsify_path: {docsify_path}")
print(f"Docsify path exists: {os.path.exists(docsify_path)}")

if os.path.exists(docsify_path):
    files = os.listdir(docsify_path)[:10]  # First 10 files
    print(f"Files in docsify directory: {files}")
