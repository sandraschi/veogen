@echo off
echo 🚀 Testing uvx availability and installing docker-mcp...
echo.

echo 📦 Checking uvx installation...
uvx --version
if %errorlevel% equ 0 (
    echo ✅ uvx found! Installing docker-mcp...
    uvx install docker-mcp
    if %errorlevel% equ 0 (
        echo ✅ docker-mcp installed successfully!
        echo.
        echo 📋 Add this to your Claude config:
        echo {
        echo   "mcpServers": {
        echo     "docker-mcp": {
        echo       "command": "uvx",
        echo       "args": ["docker-mcp"]
        echo     }
        echo   }
        echo }
        echo.
        echo 📍 Config location: %APPDATA%\Claude\claude_desktop_config.json
    ) else (
        echo ❌ Installation failed
    )
) else (
    echo ⚠️ uvx not found. Installing uv first...
    pip install uv
    if %errorlevel% equ 0 (
        echo ✅ uv installed! Now trying uvx...
        uvx install docker-mcp
    ) else (
        echo ❌ Failed to install uv. Please check Python/pip installation.
    )
)

echo.
echo 🎯 Installation attempt complete!
pause
