# 📏 CLAUDE FILE SIZE AND STRUCTURE RULES
# Preventing Giant File Disasters and Promoting Clean Architecture

## 🚨 MANDATORY FILE SIZE LIMITS

### **JavaScript/TypeScript Files**
- **MAXIMUM**: 300 lines per file
- **OPTIMAL**: 150-250 lines per file  
- **TRIGGER**: If expecting >300 lines → MANDATORY modular refactor

### **HTML Files**
- **MAXIMUM**: 400 lines per file
- **OPTIMAL**: 200-300 lines per file  
- **TRIGGER**: If expecting >400 lines → Split into components

### **CSS Files**
- **MAXIMUM**: 500 lines per file
- **OPTIMAL**: 250-400 lines per file
- **TRIGGER**: If expecting >500 lines → Split by components/sections

### **Documentation (MD/TXT)**
- **MAXIMUM**: 800 lines per file
- **OPTIMAL**: 400-600 lines per file
- **TRIGGER**: If expecting >800 lines → Split into multiple docs

### **Configuration/Data Files (JSON/YAML/etc)**
- **MAXIMUM**: 100 lines per file
- **OPTIMAL**: 50-80 lines per file
- **TRIGGER**: If expecting >100 lines → Split by feature/environment

## 🏗️ MANDATORY REFACTORING RULES

### **When File Will Exceed Limits:**
1. **STOP IMMEDIATELY** - Do not attempt to write the large file
2. **ANNOUNCE REFACTORING** - Tell user: "This will be >X lines, creating modular structure instead"
3. **CREATE FOLDER STRUCTURE** - Make logical subdirectories
4. **SPLIT BY FUNCTIONALITY** - Each file should have single responsibility
5. **CREATE INDEX/MAIN** - Entry point that imports/exports all modules
6. **WRITE README** - Document the structure and usage

### **JavaScript/TypeScript Modular Patterns:**

#### **For Libraries/Utilities (>200 lines):**
```
my-library/
├── index.js                 # Main export file
├── README.md               # Documentation
└── src/
    ├── core.js             # Core functionality (~100-150 lines)
    ├── utils.js            # Utility functions (~80-120 lines)
    ├── api.js              # API interactions (~100-150 lines)
    └── components.js       # UI components (~120-180 lines)
```

#### **For Applications (>200 lines):**
```
my-app/
├── index.js                # Entry point
├── config.js              # Configuration
├── README.md              # Documentation
└── modules/
    ├── auth.js            # Authentication (~150 lines)
    ├── ui.js              # User interface (~180 lines)
    ├── data.js            # Data management (~120 lines)
    └── api.js             # API calls (~100 lines)
```

### **HTML Modular Patterns:**

#### **For Complex Pages (>300 lines):**
```
my-page/
├── index.html             # Main page structure (~100 lines)
├── components/
│   ├── header.html        # Header component (~50 lines)
│   ├── sidebar.html       # Sidebar component (~80 lines)
│   ├── main-content.html  # Main content (~150 lines)
│   └── footer.html        # Footer component (~40 lines)
├── styles/
│   ├── main.css          # Main styles (~200 lines)
│   ├── components.css    # Component styles (~180 lines)
│   └── responsive.css    # Media queries (~120 lines)
└── scripts/
    ├── main.js           # Main functionality (~150 lines)
    ├── components.js     # Component logic (~120 lines)
    └── utils.js          # Utilities (~80 lines)
```

## 🔧 IMPLEMENTATION WORKFLOW

### **Pre-Writing Checklist:**
1. **Estimate Line Count** - Before starting, estimate final file size
2. **Check Against Limits** - Compare estimate with file type limits
3. **Plan Structure** - If >limit, plan modular structure first
4. **Create Folders** - Set up directory structure before writing
5. **Write Modules** - Create individual focused files
6. **Create Index** - Write main entry point that ties everything together
7. **Document** - Create README explaining structure

### **During Writing Process:**
- **Monitor Line Count** - Check file size every 50-100 lines
- **Stop at Limits** - If approaching limit, split immediately
- **Single Responsibility** - Each file should do ONE thing well
- **Clear Names** - File names should describe exact purpose
- **Logical Grouping** - Related functions in same file

## 📋 FILE NAMING CONVENTIONS

### **JavaScript/TypeScript:**
- `auth-manager.js` - Authentication management
- `api-client.js` - API communication
- `ui-components.js` - User interface components
- `data-models.js` - Data structures and models
- `utils.js` - General utilities
- `config.js` - Configuration settings

### **HTML Components:**
- `header-component.html` - Header section
- `navigation-menu.html` - Navigation elements
- `content-section.html` - Main content areas
- `sidebar-widget.html` - Sidebar components
- `footer-links.html` - Footer elements

### **CSS Modules:**
- `layout.css` - Layout and grid systems
- `components.css` - Component-specific styles
- `typography.css` - Font and text styles
- `colors.css` - Color schemes and variables
- `responsive.css` - Media queries and responsiveness

## 🚀 BENEFITS OF THIS SYSTEM

### **For Development:**
- **Faster Loading** - Smaller files load and parse faster
- **Easier Debugging** - Issues isolated to specific modules
- **Better Collaboration** - Multiple people can work on different files
- **Cleaner Git** - Smaller, focused commits

### **For Maintenance:**
- **Easier Updates** - Modify specific functionality without affecting others
- **Better Testing** - Test individual components in isolation
- **Reduced Conflicts** - Less chance of merge conflicts
- **Clear Structure** - Easy to understand project organization

### **For Claude:**
- **No Truncation** - Avoids file size limits that cause corruption
- **Better Context** - Easier to understand smaller, focused files
- **Faster Processing** - Smaller files process more quickly
- **Reduced Errors** - Less chance of syntax errors in large files

## ⚠️ EXCEPTION CASES

### **When Large Files Are Acceptable:**
1. **Generated Code** - Auto-generated files (but document this clearly)
2. **Data Dumps** - Large datasets (consider database instead)
3. **Legacy Integration** - Existing large files (refactor when possible)
4. **Third-Party Libraries** - External dependencies (don't modify)

### **Emergency Overrides:**
- **MUST be explicitly justified** - Explain why modular approach won't work
- **MUST include refactoring plan** - How will it be improved later
- **MUST be documented** - Clear warnings about file size
- **MUST be temporary** - Set timeline for proper refactoring

## 🎯 CLAUDE IMPLEMENTATION COMMANDS

### **Before Writing Large Files:**
```
STOP: This file will exceed [X] lines. 
Creating modular structure instead:
- Creating folder: [name]
- Splitting into [N] modules: [list]
- Each module will be ~[X] lines
- Creating index file for easy import
```

### **File Size Monitoring:**
```
Current file: [X] lines
Limit for [filetype]: [Y] lines
Status: ✅ Under limit / ⚠️ Approaching limit / 🚨 EXCEEDS - REFACTORING
```

## 📊 SUCCESS METRICS

- **Average File Size**: Target <150 lines for JS/TS, <250 for HTML
- **Module Count**: Prefer 3-8 modules over 1 giant file
- **Documentation Ratio**: 1 README per 5-10 code files
- **Reusability**: Modules should be reusable across projects
- **Maintainability**: New developers can understand structure in <10 minutes

---

**GOLDEN RULE: "If you're thinking about writing a file longer than these limits, you're thinking wrong. Think modular instead!"**

This rule system prevents:
- ✅ Truncated files
- ✅ Unmanageable code
- ✅ Debugging nightmares  
- ✅ Collaboration conflicts
- ✅ Performance issues

And promotes:
- 🚀 Clean architecture
- 🧠 Better understanding
- 🔧 Easy maintenance
- 👥 Team collaboration
- 📈 Scalable systems