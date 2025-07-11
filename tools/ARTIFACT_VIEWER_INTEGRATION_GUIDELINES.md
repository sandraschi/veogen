# 🎨 VeoGen Artifact Viewer Integration Guidelines

## 🎯 **Purpose**
This document establishes comprehensive guidelines for creating tools that integrate beautifully with Claude's artifact viewer. Every VeoGen tool must provide an exceptional artifact window experience.

## 📐 **Artifact Window Specifications**

### **Display Constraints**
- **Width**: Optimized for 800-1200px (typical artifact window)
- **Height**: Responsive, no fixed height constraints
- **Viewport**: Mobile-friendly with minimum 320px support
- **Scrolling**: Vertical scrolling allowed, horizontal scrolling forbidden

### **Performance Requirements**
- **Load time**: < 2 seconds for initial display
- **Interaction response**: < 300ms for button clicks
- **Animation duration**: 200-500ms for smooth transitions
- **Memory usage**: < 50MB for typical operations

## 🎨 **Visual Design Standards**

### **Mandatory VeoGen Brand Identity**
```css
/* REQUIRED: VeoGen color palette */
:root {
    --vg-primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --vg-secondary: rgba(255, 255, 255, 0.95);
    --vg-accent: #3498db;
    --vg-success: #27ae60;
    --vg-warning: #f39c12;
    --vg-danger: #e74c3c;
    --vg-info: #17a2b8;
    --vg-dark: #2c3e50;
    --vg-light: #ecf0f1;
}

/* REQUIRED: Base styling */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--vg-primary-gradient);
    min-height: 100vh;
    margin: 0;
    padding: 20px;
    line-height: 1.6;
}

/* REQUIRED: Main container */
.container {
    max-width: 1200px;
    margin: 0 auto;
    background: var(--vg-secondary);
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    backdrop-filter: blur(10px);
}
```

### **Typography Standards**
```css
/* REQUIRED: Typography hierarchy */
h1 { 
    font-size: 2.5rem; 
    font-weight: 700; 
    color: white; 
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); 
}

h2 { 
    font-size: 2rem; 
    font-weight: 600; 
    color: var(--vg-dark); 
    margin-bottom: 1rem; 
}

h3 { 
    font-size: 1.5rem; 
    font-weight: 600; 
    color: var(--vg-dark); 
    margin-bottom: 0.75rem; 
}

p { 
    font-size: 1rem; 
    line-height: 1.6; 
    color: #666; 
    margin-bottom: 1rem; 
}

/* REQUIRED: Minimum font sizes for accessibility */
.small-text { font-size: 0.875rem; min-height: 14px; }
.large-text { font-size: 1.125rem; font-weight: 500; }
```

### **Button System Standards**
```css
/* REQUIRED: VeoGen button system */
.btn {
    background: var(--vg-primary-gradient);
    color: white;
    border: none;
    padding: 15px 25px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.btn:active {
    transform: translateY(-1px);
}

/* REQUIRED: Button variants */
.btn.success { background: linear-gradient(135deg, #27ae60, #2ecc71); }
.btn.warning { background: linear-gradient(135deg, #f39c12, #e67e22); }
.btn.danger { background: linear-gradient(135deg, #e74c3c, #c0392b); }
.btn.info { background: linear-gradient(135deg, #17a2b8, #138496); }
.btn.secondary { background: linear-gradient(135deg, #95a5a6, #7f8c8d); }

/* REQUIRED: Button sizes */
.btn.large { padding: 20px 35px; font-size: 1.125rem; }
.btn.small { padding: 10px 15px; font-size: 0.875rem; }
```

## 🎭 **Interactive Elements Standards**

### **Loading States**
```css
/* REQUIRED: Loading spinner */
.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--vg-accent);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* REQUIRED: Progress bar */
.progress-bar {
    width: 100%;
    height: 20px;
    background: #f3f3f3;
    border-radius: 10px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-fill {
    height: 100%;
    background: var(--vg-primary-gradient);
    width: 0%;
    transition: width 0.3s ease;
    border-radius: 10px;
}
```

### **Status Cards System**
```css
/* REQUIRED: Status card framework */
.status-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border-left: 5px solid var(--vg-accent);
    transition: transform 0.2s ease;
}

.status-card:hover {
    transform: translateY(-2px);
}

.status-card.success { border-left-color: var(--vg-success); }
.status-card.warning { border-left-color: var(--vg-warning); }
.status-card.error { border-left-color: var(--vg-danger); }
.status-card.info { border-left-color: var(--vg-info); }
```

### **Modal System Standards**
```css
/* REQUIRED: Modal overlay */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(5px);
}

.modal-content {
    background: white;
    border-radius: 20px;
    padding: 30px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
    from { transform: translateY(-50px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
```

## 📱 **Responsive Design Requirements**

### **Breakpoint System**
```css
/* REQUIRED: VeoGen responsive breakpoints */
.container {
    max-width: 1200px; /* Desktop */
}

@media (max-width: 1200px) {
    .container { max-width: 992px; } /* Large tablet */
}

@media (max-width: 992px) {
    .container { max-width: 768px; } /* Tablet */
    .control-panel { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
    .container { max-width: 576px; } /* Large phone */
    .control-panel { grid-template-columns: 1fr; }
    body { padding: 10px; }
}

@media (max-width: 576px) {
    .container { max-width: 100%; } /* Small phone */
    .header h1 { font-size: 2rem; }
    .btn { width: 100%; margin-bottom: 10px; }
}
```

### **Grid System Standards**
```css
/* REQUIRED: Flexible grid system */
.grid {
    display: grid;
    gap: 20px;
}

.grid-1 { grid-template-columns: 1fr; }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

.grid-auto { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.grid-responsive { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
```

## 🎬 **Animation Standards**

### **Micro-Interactions**
```css
/* REQUIRED: Smooth transitions */
* {
    transition: all 0.3s ease;
}

/* REQUIRED: Hover effects */
.interactive:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* REQUIRED: Click feedback */
.interactive:active {
    transform: translateY(0);
    transition: transform 0.1s ease;
}

/* REQUIRED: Focus states for accessibility */
.interactive:focus {
    outline: 3px solid var(--vg-accent);
    outline-offset: 2px;
}
```

### **Page Transitions**
```css
/* REQUIRED: Fade-in animation */
.fade-in {
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* REQUIRED: Slide-in animation */
.slide-in {
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from { transform: translateX(-100%); }
    to { transform: translateX(0); }
}
```

## 🧠 **JavaScript Standards**

### **VeoGen Tools Utility Framework**
```javascript
// REQUIRED: Standard utility object
const VeoGenTools = {
    // Loading states
    showLoading: (show) => {
        const loader = document.getElementById('loading');
        if (loader) loader.classList.toggle('hidden', !show);
    },
    
    // Status messages
    showError: (message) => {
        VeoGenTools.showStatus('error', '❌ Error', message);
    },
    
    showSuccess: (message) => {
        VeoGenTools.showStatus('success', '✅ Success', message);
    },
    
    showWarning: (message) => {
        VeoGenTools.showStatus('warning', '⚠️ Warning', message);
    },
    
    showInfo: (message) => {
        VeoGenTools.showStatus('info', 'ℹ️ Information', message);
    },
    
    // Generic status display
    showStatus: (type, title, message) => {
        const html = `
            <div class="status-card ${type}">
                <h3>${title}</h3>
                <p>${message}</p>
            </div>
        `;
        const results = document.getElementById('results');
        if (results) results.innerHTML = html;
    },
    
    // Progress indication
    updateProgress: (percent) => {
        const fill = document.querySelector('.progress-fill');
        if (fill) fill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
    },
    
    // Modal management
    showModal: (title, content, onConfirm = null) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>${title}</h3>
                <div>${content}</div>
                <div style="margin-top: 20px; text-align: right;">
                    ${onConfirm ? '<button class="btn" onclick="VeoGenTools.confirmModal()">Confirm</button>' : ''}
                    <button class="btn secondary" onclick="VeoGenTools.closeModal()" style="margin-left: 10px;">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        VeoGenTools._currentModal = { element: modal, onConfirm };
    },
    
    closeModal: () => {
        if (VeoGenTools._currentModal) {
            VeoGenTools._currentModal.element.remove();
            VeoGenTools._currentModal = null;
        }
    },
    
    confirmModal: () => {
        if (VeoGenTools._currentModal && VeoGenTools._currentModal.onConfirm) {
            VeoGenTools._currentModal.onConfirm();
        }
        VeoGenTools.closeModal();
    },
    
    // Data formatting
    formatTimestamp: (date = new Date()) => {
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Performance monitoring
    startTimer: (name) => {
        VeoGenTools._timers = VeoGenTools._timers || {};
        VeoGenTools._timers[name] = performance.now();
    },
    
    endTimer: (name) => {
        if (VeoGenTools._timers && VeoGenTools._timers[name]) {
            const duration = performance.now() - VeoGenTools._timers[name];
            console.log(`⏱️ ${name}: ${duration.toFixed(2)}ms`);
            delete VeoGenTools._timers[name];
            return duration;
        }
    }
};
```

### **Async Operations Standards**
```javascript
// REQUIRED: Promise-based operations
async function performAsyncOperation(operationName, asyncFunction) {
    try {
        VeoGenTools.showLoading(true);
        VeoGenTools.startTimer(operationName);
        
        const result = await asyncFunction();
        
        VeoGenTools.endTimer(operationName);
        VeoGenTools.showLoading(false);
        VeoGenTools.showSuccess(`${operationName} completed successfully`);
        
        return result;
    } catch (error) {
        VeoGenTools.showLoading(false);
        VeoGenTools.showError(`${operationName} failed: ${error.message}`);
        throw error;
    }
}

// REQUIRED: Error boundary for operations
function safeExecute(operation, fallback = null) {
    try {
        return operation();
    } catch (error) {
        console.error('Safe execution failed:', error);
        VeoGenTools.showError(`Operation failed: ${error.message}`);
        return fallback;
    }
}
```

### **Event Handling Standards**
```javascript
// REQUIRED: Debounced event handling
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// REQUIRED: DOM ready handler
function onReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

// REQUIRED: Window resize handler
const handleResize = debounce(() => {
    // Responsive adjustments
    const container = document.querySelector('.container');
    if (container && window.innerWidth < 768) {
        container.classList.add('mobile-view');
    } else {
        container.classList.remove('mobile-view');
    }
}, 250);

window.addEventListener('resize', handleResize);
```

## 🔧 **Integration Patterns**

### **Basic Memory Integration**
```javascript
// REQUIRED: Basic Memory save pattern
async function saveToBasicMemory(title, content, folder = 'tool-sessions') {
    if (typeof window.claude !== 'undefined' && window.claude.complete) {
        try {
            const prompt = `Save to basic memory in folder "${folder}" with title "${title}": ${content}`;
            await window.claude.complete(prompt);
            VeoGenTools.showSuccess('Data saved to basic memory');
            return true;
        } catch (error) {
            console.warn('Basic memory save failed:', error);
            VeoGenTools.showWarning('Could not save to basic memory');
            return false;
        }
    } else {
        console.info('Basic memory not available - Claude API not found');
        return false;
    }
}

// REQUIRED: Auto-save session data
function autoSaveSession() {
    const sessionData = {
        tool: document.title,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userData: getCurrentUserData() // Implement per tool
    };
    
    saveToBasicMemory(
        `Session-${sessionData.tool}-${Date.now()}`,
        JSON.stringify(sessionData, null, 2)
    );
}
```

### **API Integration Pattern**
```javascript
// REQUIRED: API communication wrapper
class VeoGenAPI {
    constructor(baseURL = 'http://localhost:8100/api') {
        this.baseURL = baseURL;
        this.timeout = 30000; // 30 seconds
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}/${endpoint}`;
        const config = {
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }
    
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async healthCheck() {
        try {
            await this.get('health');
            return true;
        } catch {
            return false;
        }
    }
}

// REQUIRED: API instance
const api = new VeoGenAPI();
```

## 📊 **Performance Standards**

### **Resource Management**
```javascript
// REQUIRED: Memory management
function cleanupResources() {
    // Remove event listeners
    const elements = document.querySelectorAll('[data-cleanup]');
    elements.forEach(el => {
        el.removeEventListener('click', el._clickHandler);
        el.removeEventListener('change', el._changeHandler);
    });
    
    // Clear intervals and timeouts
    if (window._veoGenIntervals) {
        window._veoGenIntervals.forEach(clearInterval);
        window._veoGenIntervals = [];
    }
    
    if (window._veoGenTimeouts) {
        window._veoGenTimeouts.forEach(clearTimeout);
        window._veoGenTimeouts = [];
    }
}

// REQUIRED: Cleanup on page unload
window.addEventListener('beforeunload', cleanupResources);
```

### **Performance Monitoring**
```javascript
// REQUIRED: Performance tracking
const VeoGenPerformance = {
    marks: {},
    
    mark: (name) => {
        VeoGenPerformance.marks[name] = performance.now();
    },
    
    measure: (name, startMark) => {
        if (VeoGenPerformance.marks[startMark]) {
            const duration = performance.now() - VeoGenPerformance.marks[startMark];
            console.log(`📊 ${name}: ${duration.toFixed(2)}ms`);
            
            // Warn about slow operations
            if (duration > 1000) {
                console.warn(`⚠️ Slow operation detected: ${name} took ${duration.toFixed(2)}ms`);
            }
            
            return duration;
        }
    }
};
```

## 🛡️ **Security Standards**

### **Input Validation**
```javascript
// REQUIRED: Input sanitization
function sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}

function validateInput(input, maxLength = 1000) {
    if (typeof input !== 'string') {
        throw new Error('Input must be a string');
    }
    
    if (input.length > maxLength) {
        throw new Error(`Input too long (max ${maxLength} characters)`);
    }
    
    // Check for dangerous patterns
    const dangerousPatterns = [/<script/i, /javascript:/i, /on\w+=/i];
    for (const pattern of dangerousPatterns) {
        if (pattern.test(input)) {
            throw new Error('Invalid input detected');
        }
    }
    
    return sanitizeInput(input);
}
```

### **Safe DOM Manipulation**
```javascript
// REQUIRED: Safe HTML insertion
function safeSetHTML(element, html) {
    // Create a temporary container
    const temp = document.createElement('div');
    temp.innerHTML = html;
    
    // Remove any script tags
    const scripts = temp.querySelectorAll('script');
    scripts.forEach(script => script.remove());
    
    // Remove dangerous attributes
    const elements = temp.querySelectorAll('*');
    elements.forEach(el => {
        const attributes = Array.from(el.attributes);
        attributes.forEach(attr => {
            if (attr.name.startsWith('on') || attr.name === 'href' && attr.value.includes('javascript:')) {
                el.removeAttribute(attr.name);
            }
        });
    });
    
    element.innerHTML = temp.innerHTML;
}
```

## 📋 **Quality Checklist**

### **Pre-Deployment Verification**
Before any tool can be marked as artifact-ready:

#### **Visual Standards**
- [ ] Uses VeoGen color palette and gradients
- [ ] Header with tool icon and title
- [ ] Professional button system with hover effects
- [ ] Status cards for feedback
- [ ] Loading states for async operations
- [ ] Responsive design for all screen sizes

#### **Functionality Standards**
- [ ] All interactive elements work correctly
- [ ] Error handling displays user-friendly messages
- [ ] Success feedback is clear and immediate
- [ ] Progress indication for long operations
- [ ] Keyboard navigation support

#### **Performance Standards**
- [ ] Loads in under 2 seconds
- [ ] Smooth animations (no janky transitions)
- [ ] Memory usage stays under 50MB
- [ ] No console errors or warnings

#### **Integration Standards**
- [ ] VeoGenTools utility object implemented
- [ ] Basic Memory integration (if applicable)
- [ ] API integration (if applicable)
- [ ] Session auto-save functionality

#### **Code Quality Standards**
- [ ] Well-commented JavaScript
- [ ] Consistent naming conventions
- [ ] Error boundaries implemented
- [ ] Resource cleanup on page unload

---

## 🎯 **Implementation Example**

### **Complete Artifact-Ready Tool Template**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Example Tool - VeoGen Professional Tool</title>
    <style>
        /* Include all required CSS from above */
    </style>
</head>
<body>
    <div class="container fade-in">
        <div class="header">
            <h1>🔧 Example Tool</h1>
            <p class="subtitle">Demonstrates perfect artifact integration</p>
        </div>
        
        <div class="main-content">
            <div class="control-panel grid-auto">
                <button class="btn" onclick="demonstrateFeature()">🚀 Demonstrate</button>
                <button class="btn success" onclick="showSuccess()">✅ Success Test</button>
                <button class="btn warning" onclick="showWarning()">⚠️ Warning Test</button>
                <button class="btn danger" onclick="showError()">❌ Error Test</button>
            </div>
            
            <div id="loading" class="loading hidden">
                <div class="spinner"></div>
                <p>Processing...</p>
            </div>
            
            <div id="results">
                <div class="status-card">
                    <h3>🎨 Perfect Artifact Integration</h3>
                    <p>This tool demonstrates all VeoGen artifact standards</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        /* Include VeoGenTools and all required JavaScript from above */
        
        function demonstrateFeature() {
            performAsyncOperation('Feature Demo', async () => {
                // Simulate async work
                await new Promise(resolve => setTimeout(resolve, 2000));
                return { success: true };
            });
        }
        
        function showSuccess() {
            VeoGenTools.showSuccess('This is how success messages look!');
        }
        
        function showWarning() {
            VeoGenTools.showWarning('This is how warning messages appear!');
        }
        
        function showError() {
            VeoGenTools.showError('This is how error messages are displayed!');
        }
        
        // Initialize tool
        onReady(() => {
            console.log('🎨 Artifact integration demo ready');
        });
    </script>
</body>
</html>
```

---

**This document ensures every VeoGen tool provides an exceptional artifact viewer experience with consistent branding, professional interactions, and seamless integration.**

**Created**: July 10, 2025  
**Version**: 1.0.0  
**Status**: Active Standard ✅