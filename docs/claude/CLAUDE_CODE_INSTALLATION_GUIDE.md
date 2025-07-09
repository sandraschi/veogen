# 🚀 Claude Code Installation Guide for Windows + VSCode

## 📋 **Prerequisites**

You have WSL2 with Ubuntu - perfect! Claude Code requires a Unix-like environment.

## 🛠️ **Step-by-Step Installation**

### **Step 1: Open WSL Ubuntu Terminal**

1. **Open WSL Ubuntu:**
   - Press `Windows + R`
   - Type `wsl` and press Enter
   - OR open Windows Terminal and select "Ubuntu"

### **Step 2: Install Node.js in WSL**

```bash
# Update package list
sudo apt update

# Install Node.js and npm
sudo apt install -y nodejs npm

# Verify installation
node --version
npm --version
```

### **Step 3: Install Claude Code**

```bash
# Install Claude Code globally
npm install -g @anthropic-ai/claude-code

# Verify installation
claude-code --version
```

### **Step 4: Set up Anthropic API Key**

```bash
# Set your API key (replace with your actual key)
export ANTHROPIC_API_KEY="your-api-key-here"

# Make it permanent by adding to .bashrc
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### **Step 5: Test Claude Code**

```bash
# Test basic functionality
claude-code --help

# Create a test project
mkdir ~/test-claude-code
cd ~/test-claude-code

# Initialize a simple project
echo "console.log('Hello from Claude Code!');" > test.js

# Use Claude Code to improve the file
claude-code "Make this JavaScript file more robust with error handling"
```

---

## 🔗 **Integrating with VSCode**

### **Method 1: Use WSL Extension in VSCode**

1. **Install WSL Extension:**
   - Open VSCode
   - Install "WSL" extension by Microsoft
   - Install "Remote Development" extension pack

2. **Open WSL Project in VSCode:**
   - Press `Ctrl+Shift+P`
   - Type "WSL: New WSL Window"
   - OR click the WSL button in bottom-left corner

3. **Open Terminal in WSL:**
   - In VSCode, press `Ctrl+`` (backtick)
   - Make sure it shows "WSL: Ubuntu" in terminal

4. **Use Claude Code from VSCode Terminal:**
   ```bash
   # Navigate to your project
   cd /mnt/c/Users/sandr/your-project
   
   # Use Claude Code
   claude-code "Add TypeScript types to this JavaScript project"
   ```

### **Method 2: Create VSCode Tasks**

Create `.vscode/tasks.json` in your project:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Claude Code: Improve File",
            "type": "shell",
            "command": "wsl",
            "args": [
                "-d", "Ubuntu",
                "bash", "-c",
                "cd '${workspaceFolder}' && claude-code 'Improve the currently selected file'"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        },
        {
            "label": "Claude Code: Add Tests",
            "type": "shell", 
            "command": "wsl",
            "args": [
                "-d", "Ubuntu",
                "bash", "-c",
                "cd '${workspaceFolder}' && claude-code 'Add comprehensive tests for this project'"
            ],
            "group": "test"
        }
    ]
}
```

### **Method 3: Create VSCode Shortcuts**

Add to `keybindings.json` (Ctrl+Shift+P → "Preferences: Open Keyboard Shortcuts (JSON)"):

```json
[
    {
        "key": "ctrl+alt+c",
        "command": "workbench.action.tasks.runTask",
        "args": "Claude Code: Improve File"
    },
    {
        "key": "ctrl+alt+t", 
        "command": "workbench.action.tasks.runTask",
        "args": "Claude Code: Add Tests"
    }
]
```

---

## 🎯 **Common Claude Code Commands**

### **Code Improvement**
```bash
# Improve code quality
claude-code "Refactor this code for better performance and readability"

# Add error handling
claude-code "Add comprehensive error handling to all functions"

# Add documentation
claude-code "Add JSDoc comments to all functions and classes"
```

### **Testing**
```bash
# Generate tests
claude-code "Create unit tests for all functions in this file"

# Add integration tests
claude-code "Add integration tests for the API endpoints"
```

### **Project Structure**
```bash
# Organize project
claude-code "Reorganize this project structure following best practices"

# Add configuration
claude-code "Add ESLint, Prettier, and TypeScript configuration"
```

### **Feature Development**
```bash
# Add new features
claude-code "Add user authentication to this Express.js app"

# Database integration
claude-code "Add PostgreSQL integration with proper migrations"
```

---

## 📁 **Working with Your VeoGen Project**

### **Navigate to VeoGen in WSL**
```bash
# Your VeoGen project path in WSL
cd /mnt/c/Users/sandr/AppData/Local/AnthropicClaude/app-0.11.6/veogen

# Use Claude Code on VeoGen
claude-code "Add comprehensive error handling to the backend API"
claude-code "Optimize the React frontend for better performance"
claude-code "Add more sophisticated email templates"
```

### **VeoGen-Specific Tasks**
```bash
# Enhance video generation
claude-code "Add new video style options to the VeoGen platform"

# Improve monitoring
claude-code "Add custom Grafana dashboards for VeoGen metrics"

# Database optimization  
claude-code "Optimize PostgreSQL queries for better performance"
```

---

## 🔧 **Troubleshooting**

### **If Claude Code Installation Fails:**
```bash
# Update npm to latest version
npm install -g npm@latest

# Clear npm cache
npm cache clean --force

# Try installing with verbose logging
npm install -g @anthropic-ai/claude-code --verbose
```

### **If API Key Issues:**
```bash
# Check if API key is set
echo $ANTHROPIC_API_KEY

# Test API connection
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/complete
```

### **If Permission Issues:**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) /usr/local/lib/node_modules
```

---

## 🚀 **Getting Started Quickly**

1. **Open WSL Ubuntu terminal**
2. **Run the commands from Step 2 above**
3. **Set your Anthropic API key**
4. **Open VSCode with WSL extension**
5. **Start using Claude Code in your projects!**

---

## 📚 **Additional Resources**

- **Claude Code Documentation**: https://docs.anthropic.com/en/docs/agents-and-tools/claude-code
- **VSCode WSL Guide**: https://code.visualstudio.com/docs/remote/wsl
- **Anthropic API Docs**: https://docs.anthropic.com/

---

**🎉 Once installed, you'll be able to delegate coding tasks directly to Claude from your terminal and VSCode!**
