# 🚨 CRITICAL ISSUES - QUICK REFERENCE INDEX

**Purpose**: Immediate access to known critical issues without searching  
**Rule**: CHECK THIS FILE FIRST before any documentation searching

---

## 🔴 **IMMEDIATE DANGERS - DATA LOSS RISK**

### **Desktop Commander MCP - FILE CORRUPTION BUG**
- **Issue**: Truncates beginning of large files during write operations
- **Evidence**: VeoGen Voice work lost 300+ lines from multiple files
- **Pattern**: Head corruption only, tails remain intact
- **Mitigation**: Use filesystem MCP for large files, avoid Desktop Commander
- **File**: `voice-ai-revolution\COMPLETE_FILE_AUDIT.md`

### **File Size Limits to Prevent Corruption**
- **JavaScript/TypeScript**: 300 lines max
- **HTML**: 400 lines max  
- **CSS**: 500 lines max
- **Documentation**: 800 lines max
- **Rule**: Create modular structure if exceeding limits

---

## ⚠️ **KNOWN PROBLEMATIC MCP SERVERS**

### **QuantGeekDev docker-mcp**
- **Issue**: Poor Windows support, Linux-centric development
- **Problems**: Fails after installation, requires misconfiguration fixes
- **Author**: Barcelona-based "Linux freak" with no Windows testing
- **Stars**: 313 (popular but broken)
- **Alternative**: Use direct Docker commands or wait for official Anthropic server

### **MCP Hallucination Disaster**
- **Issue**: Claude suggests fake MCP packages that don't exist
- **Examples**: teams, outlook, sharepoint, onenote packages (all fake)
- **Result**: 17 fake packages polluted config, caused "overnight breakage"
- **Prevention**: MANDATORY web search verification before suggesting packages
- **File**: `docs\claude\MCP_HALLUCINATION_DISASTER_CASE_STUDY.md`

---

## 🔧 **TOOLS FOR IMMEDIATE PROBLEM SOLVING**

### **MCP Configuration Reader**
```powershell
# Read actual MCP configuration (use this first!)
.\mcp-config-reader.ps1 -All

# Quick server list
.\mcp-config-reader.ps1 -ListServers

# Check for known problems
.\mcp-config-reader.ps1 -ShowProblems
```

### **Quick Health Checks**
```powershell
# VeoGen Docker status
docker-compose ps

# Authentication test  
python test_final_auth.py

# MCP config backup
.\mcp-config-reader.ps1 -Backup
```

---

## ✅ **VERIFIED WORKING MCP SERVERS**

### **Safe for Production Use**
- **basic-memory**: ✅ Knowledge management, no corruption issues
- **github-official**: ✅ Repository operations
- **microsoft-365**: ✅ Office integration
- **filesystem**: ✅ Official Anthropic server for file operations

### **VeoGen Custom Servers**
- **ImmichMCP**: ✅ Photo management (local compiled)
- **CalibreMCP**: ✅ Ebook management (local compiled) 
- **VeoGenVoiceMCP**: ✅ Voice control integration

---

## 🚫 **CRITICAL ANTI-PATTERNS**

### **Mock Data Syndrome**
- **Problem**: Claude declares "COMPLETED SUCCESSFULLY" with fake data
- **Examples**: "Joe Bloggs", "Jane Doe" placeholder names
- **Rule**: NO mock data without explicit disclosure
- **File**: `docs\claude\ANTI_MOCK_DATA_MANIFESTO.md`

### **Windows Incompatibility Signs**
- **Red flags**: Linux-style commands in docs, no Windows testing
- **Examples**: `source venv/bin/activate` vs `venv\Scripts\activate`
- **Pattern**: European developers often ignore Windows compatibility

---

## 🎯 **MANDATORY SEARCH PROTOCOL**

### **Before ANY Documentation Searching:**
1. ✅ **Check this index first** (CRITICAL_ISSUES_INDEX.md)
2. ✅ **Run MCP config reader** if MCP-related: `.\mcp-config-reader.ps1 -All`
3. ✅ **Check specific known files** mentioned in this index
4. ✅ **Ask Sandra** if issue not found after 2 minutes

### **Stop Random Searching:**
- ❌ Don't search basic-memory randomly
- ❌ Don't search filesystem without direction  
- ❌ Don't spend 10+ minutes "rummaging around"
- ✅ Follow this index → specific docs → ask Sandra

---

## 📍 **Key Documentation Locations**

### **Critical Files to Check:**
- **File corruption**: `voice-ai-revolution\COMPLETE_FILE_AUDIT.md`
- **MCP disasters**: `docs\claude\MCP_HALLUCINATION_DISASTER_CASE_STUDY.md`
- **Anti-patterns**: `docs\claude\ANTI_MOCK_DATA_MANIFESTO.md`
- **Working servers**: `docs\claude\ESSENTIAL_WORKING_MCP_SERVERS.md`

### **Configuration Files:**
- **MCP config**: `%APPDATA%\Claude\claude_desktop_config.json`
- **VeoGen Docker**: `docker-compose.yml`
- **Restart guide**: `CLAUDE_RESTART_GUIDE.md`

---

## 🎯 **SUCCESS METRICS**
- **Issue resolution**: < 2 minutes for known issues
- **Documentation efficiency**: 80% of questions resolved by this index
- **No more "rummaging"**: Follow protocol, don't search randomly
- **Sandra satisfaction**: Quick, accurate answers to critical issues

---

**🚨 REMEMBER: This index exists to PREVENT inefficient searching!**  
**Use it FIRST, always!**