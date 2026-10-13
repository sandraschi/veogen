# 🎯 Claude Developer Rulebook
## Essential Rules and Patterns for Effective Development Sessions

### 📋 Session Initialization
**RULE 1: Always Read This Rulebook First**
- Read this file at the start of every development session
- Follow the project-specific onboarding script (`claude_onboard.py`)
- Check project status before making changes

---

## ⏱️ BUILD & DEPLOYMENT RULES

### RULE 2: Build Patience Protocol
**Never declare a build failed prematurely**

#### Docker Build Timeouts
- **Frontend builds**: Wait minimum 5 minutes (300 seconds)
- **Backend builds**: Wait minimum 3 minutes (180 seconds)
- **Full stack rebuilds**: Wait minimum 10 minutes (600 seconds)
- **npm install**: Wait minimum 5 minutes (300 seconds)

#### Build Progress Indicators
```bash
# Use proper timeouts for build commands
execute_command("docker-compose build --no-cache frontend", 600000)  # 10 minutes
execute_command("npm install", 300000)  # 5 minutes
execute_command("docker-compose up -d", 120000)  # 2 minutes
```

#### Build Failure Criteria
Only declare build failed if:
- ❌ Process exits with non-zero code AND timeout reached
- ❌ Clear error messages in output
- ❌ Process hangs for 2x expected timeout

#### Build Success Verification
```bash
# Always verify after builds
docker-compose ps  # Check container status
docker-compose logs frontend --tail=20  # Check for errors
curl http://localhost:4710/health  # Test endpoints
```

### RULE 3: Service Startup Patience
**Wait for services to fully initialize**

#### Startup Sequence
1. Start services: `docker-compose up -d`
2. Wait 30 seconds for basic startup
3. Wait additional 60 seconds for health checks
4. Verify with health endpoints
5. Only then run tests

#### Health Check Commands
```bash
# Wait for services with proper timeouts
execute_command("docker-compose up -d", 60000)
execute_command("sleep 30", 35000)  # Give services time to start
execute_command("docker-compose ps", 10000)  # Check status
execute_command("python test_final_auth.py", 30000)  # Verify functionality
```

---

## 🎨 CSS & STYLING RULES

### RULE 4: CSS Architecture Standards

#### CSS Class Naming Convention
```css
/* Use BEM methodology */
.component-name {}           /* Block */
.component-name__element {}  /* Element */
.component-name--modifier {} /* Modifier */

/* Examples */
.auth-form {}
.auth-form__input {}
.auth-form__input--error {}
.auth-form__button {}
.auth-form__button--primary {}
```

#### Responsive Design Rules
```css
/* Mobile-first approach */
.component {
  /* Mobile styles (default) */
  padding: 1rem;
}

/* Tablet and up */
@media (min-width: 768px) {
  .component {
    padding: 2rem;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .component {
    padding: 3rem;
  }
}
```

#### CSS Organization
```css
/* File structure order */
/* 1. Reset/Normalize */
/* 2. Variables/Custom Properties */
/* 3. Base styles */
/* 4. Layout components */
/* 5. UI components */
/* 6. Utilities */
/* 7. Media queries */
```

#### Color System Rules
```css
:root {
  /* Primary colors */
  --color-primary: #8b5cf6;
  --color-primary-dark: #7c3aed;
  --color-primary-light: #a78bfa;
  
  /* Semantic colors */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
  
  /* Neutral colors */
  --color-gray-50: #f9fafb;
  --color-gray-900: #111827;
}
```

---

## 🐛 DEBUG & LOGGING RULES

### RULE 5: Debug Sequence Protocol

#### Standard Debug Sequence
1. **Identify Problem Area**
   ```bash
   # Check service status first
   docker-compose ps
   docker-compose logs service-name --tail=50
   ```

2. **Check Network Connectivity**
   ```bash
   curl -v http://localhost:4700/health
   curl -v http://localhost:4710
   ```

3. **Test API Endpoints**
   ```bash
   python test_final_auth.py
   # Or specific endpoint tests
   curl -X POST http://localhost:4700/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"test123"}'
   ```

4. **Check Database Connectivity**
   ```bash
   docker-compose exec postgres psql -U veogen -d veogen -c "SELECT 1;"
   ```

5. **Frontend Console Check**
   - Always mention: "Check browser developer console for errors"
   - Always mention: "Check Network tab for failed requests"

#### Debug Information Gathering
```bash
# System information
execute_command("docker --version", 10000)
execute_command("docker-compose --version", 10000)
execute_command("node --version", 10000)
execute_command("python --version", 10000)

# Service status
execute_command("docker-compose ps", 10000)
execute_command("docker stats --no-stream", 15000)

# Recent logs
execute_command("docker-compose logs backend --tail=20", 10000)
execute_command("docker-compose logs frontend --tail=20", 10000)
```

### RULE 6: Logger Modal Specifications

#### Modal Structure
```html
<!-- Logger Modal Template -->
<div class="logger-modal">
  <div class="logger-modal__header">
    <h3 class="logger-modal__title">System Logs</h3>
    <div class="logger-modal__controls">
      <button class="logger-modal__level-filter" data-level="all">All</button>
      <button class="logger-modal__level-filter" data-level="error">Errors</button>
      <button class="logger-modal__level-filter" data-level="warn">Warnings</button>
      <button class="logger-modal__level-filter" data-level="info">Info</button>
      <button class="logger-modal__clear">Clear</button>
      <button class="logger-modal__close">×</button>
    </div>
  </div>
  <div class="logger-modal__content">
    <div class="logger-modal__logs" id="logger-output"></div>
  </div>
  <div class="logger-modal__footer">
    <div class="logger-modal__stats">
      <span class="logger-modal__count">0 entries</span>
      <span class="logger-modal__timestamp">Last updated: --</span>
    </div>
    <button class="logger-modal__download">Download Logs</button>
  </div>
</div>
```

#### Logger Modal CSS
```css
.logger-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90vw;
  max-width: 1000px;
  height: 80vh;
  background: var(--color-gray-900);
  border: 1px solid var(--color-gray-700);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  z-index: 1000;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.logger-modal__header {
  padding: 1rem;
  border-bottom: 1px solid var(--color-gray-700);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-gray-800);
}

.logger-modal__title {
  color: var(--color-gray-100);
  margin: 0;
  font-size: 1.1rem;
}

.logger-modal__controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.logger-modal__level-filter {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--color-gray-600);
  background: var(--color-gray-700);
  color: var(--color-gray-200);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.logger-modal__level-filter--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.logger-modal__content {
  flex: 1;
  overflow: hidden;
}

.logger-modal__logs {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
  background: var(--color-gray-900);
  font-size: 0.85rem;
  line-height: 1.4;
}

.logger-modal__log-entry {
  margin-bottom: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  border-left: 3px solid transparent;
}

.logger-modal__log-entry--error {
  background: rgba(239, 68, 68, 0.1);
  border-left-color: var(--color-error);
  color: #fca5a5;
}

.logger-modal__log-entry--warn {
  background: rgba(245, 158, 11, 0.1);
  border-left-color: var(--color-warning);
  color: #fcd34d;
}

.logger-modal__log-entry--info {
  background: rgba(59, 130, 246, 0.1);
  border-left-color: var(--color-info);
  color: #93c5fd;
}

.logger-modal__log-entry--debug {
  color: var(--color-gray-400);
}

.logger-modal__timestamp {
  color: var(--color-gray-500);
  font-size: 0.75rem;
  margin-right: 0.5rem;
}

.logger-modal__footer {
  padding: 1rem;
  border-top: 1px solid var(--color-gray-700);
  background: var(--color-gray-800);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

#### Logger Modal Functionality
```javascript
class LoggerModal {
  constructor() {
    this.logs = [];
    this.currentFilter = 'all';
    this.isVisible = false;
    this.init();
  }

  init() {
    this.createModal();
    this.bindEvents();
    this.startLogCapture();
  }

  addLog(level, message, timestamp = new Date()) {
    const logEntry = {
      id: Date.now() + Math.random(),
      level,
      message,
      timestamp,
      source: this.getCallStack()
    };
    
    this.logs.push(logEntry);
    this.renderLogs();
    this.updateStats();
    
    // Auto-scroll to bottom for new entries
    if (this.isVisible) {
      this.scrollToBottom();
    }
  }

  filterLogs(level) {
    this.currentFilter = level;
    this.renderLogs();
    this.updateFilterButtons();
  }

  clearLogs() {
    this.logs = [];
    this.renderLogs();
    this.updateStats();
  }

  downloadLogs() {
    const logText = this.logs.map(log => 
      `[${log.timestamp.toISOString()}] ${log.level.toUpperCase()}: ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${new Date().toISOString().slice(0, 19)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  show() {
    this.isVisible = true;
    this.modal.style.display = 'flex';
    this.renderLogs();
    this.scrollToBottom();
  }

  hide() {
    this.isVisible = false;
    this.modal.style.display = 'none';
  }
}

// Global logger instance
window.logger = new LoggerModal();

// Override console methods to capture logs
const originalConsole = { ...console };
['log', 'info', 'warn', 'error', 'debug'].forEach(level => {
  console[level] = (...args) => {
    originalConsole[level](...args);
    window.logger.addLog(level === 'log' ? 'info' : level, args.join(' '));
  };
});
```

---

## 🧪 TESTING RULES

### RULE 7: Testing Protocols

#### Test Execution Order
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing
3. **End-to-End Tests**: Full user workflow testing
4. **Performance Tests**: Load and stress testing

#### Test Timeout Rules
```bash
# Different timeouts for different test types
execute_command("npm test", 120000)  # Unit tests: 2 minutes
execute_command("python test_final_auth.py", 30000)  # API tests: 30 seconds
execute_command("npx playwright test", 300000)  # E2E tests: 5 minutes
```

#### Test Failure Investigation
1. **Check test output for specific errors**
2. **Verify test environment setup**
3. **Check service dependencies**
4. **Review recent code changes**
5. **Run individual failing tests**

---

## 🔧 CODE QUALITY RULES

### RULE 8: Code Review Checklist

#### Before Committing Changes
- [ ] Run linting: `npm run lint`
- [ ] Run tests: `npm test`
- [ ] Check TypeScript: `npm run type-check`
- [ ] Verify builds: `npm run build`
- [ ] Test in development: `npm start`

#### Code Style Standards
```javascript
// Use consistent naming
const userAuthToken = 'token';  // camelCase for variables
const API_BASE_URL = 'url';     // UPPER_SNAKE_CASE for constants
class UserManager {}            // PascalCase for classes

// Use meaningful names
const getUserById = (id) => {}  // Descriptive function names
const isUserLoggedIn = false    // Boolean variables start with is/has/can

// Comment complex logic
/**
 * Validates user authentication token and refreshes if needed
 * @param {string} token - JWT token to validate
 * @returns {Promise<boolean>} - True if token is valid or refreshed
 */
const validateAndRefreshToken = async (token) => {
  // Implementation...
}
```

### RULE 9: Error Handling Standards

#### API Error Handling
```javascript
// Always use try-catch for async operations
const fetchUserData = async (userId) => {
  try {
    const response = await fetch(`/api/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch user data:', error);
    
    // Log to our logger modal
    logger.addLog('error', `User fetch failed: ${error.message}`);
    
    // Return safe fallback
    return null;
  }
};
```

#### Frontend Error Boundaries
```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    logger.addLog('error', `React Error: ${error.message}`);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.stack}</pre>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## 🚀 DEPLOYMENT RULES

### RULE 10: Deployment Checklist

#### Pre-Deployment Verification
```bash
# 1. Check all services are healthy
docker-compose ps

# 2. Run full test suite
python test_final_auth.py
npm test

# 3. Verify environment variables
docker-compose config

# 4. Check resource usage
docker stats --no-stream

# 5. Backup database if needed
docker-compose exec postgres pg_dump -U veogen veogen > backup.sql
```

#### Deployment Steps
1. **Stop services gracefully**
2. **Pull latest changes**
3. **Rebuild containers with no cache**
4. **Start services with proper wait times**
5. **Verify health endpoints**
6. **Run smoke tests**

#### Rollback Plan
```bash
# Quick rollback procedure
docker-compose down
git checkout previous-working-commit
docker-compose build --no-cache
docker-compose up -d
# Wait and verify
python test_final_auth.py
```

---

## 📱 RESPONSIVE DESIGN RULES

### RULE 11: Mobile-First Development

#### Breakpoint System
```css
/* Mobile first (default) */
.component { /* Mobile styles */ }

/* Small tablets */
@media (min-width: 640px) { /* sm */ }

/* Large tablets */  
@media (min-width: 768px) { /* md */ }

/* Small desktops */
@media (min-width: 1024px) { /* lg */ }

/* Large desktops */
@media (min-width: 1280px) { /* xl */ }

/* Extra large */
@media (min-width: 1536px) { /* 2xl */ }
```

#### Touch-Friendly Design
```css
/* Minimum touch target size */
.button, .link, .input {
  min-height: 44px;  /* iOS recommendation */
  min-width: 44px;
}

/* Adequate spacing between interactive elements */
.nav-item {
  margin: 8px 0;
}

/* Large, clear fonts */
body {
  font-size: 16px;  /* Prevents iOS zoom on focus */
}
```

---

## 🔐 SECURITY RULES

### RULE 12: Security Best Practices

#### Authentication Security
```javascript
// Never log sensitive data
const loginUser = async (credentials) => {
  console.log('Login attempt for user:', credentials.email);  // ✅ OK
  console.log('Password:', credentials.password);             // ❌ NEVER
  
  // Use secure token storage
  localStorage.setItem('token', token);        // ❌ Avoid for sensitive data
  sessionStorage.setItem('token', token);     // ✅ Better for session data
  
  // Validate on both client and server
  if (!isValidEmail(credentials.email)) {
    throw new Error('Invalid email format');
  }
};
```

#### Input Sanitization
```javascript
// Always sanitize user input
const sanitizeInput = (input) => {
  return input
    .replace(/[<>]/g, '')           // Remove potential HTML
    .trim()                         // Remove whitespace
    .slice(0, 1000);               // Limit length
};

// Validate API responses
const processApiResponse = (response) => {
  if (!response || typeof response !== 'object') {
    throw new Error('Invalid response format');
  }
  
  // Validate expected fields exist
  const requiredFields = ['id', 'email', 'status'];
  for (const field of requiredFields) {
    if (!(field in response)) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  return response;
};
```

---

## 🎭 BROWSER AUTOMATION RULES

### RULE 13: Playwright/Browser Testing Standards

#### Page Object Pattern
```javascript
class LoginPage {
  constructor(page) {
    this.page = page;
    this.emailInput = page.locator('[data-testid="email-input"]');
    this.passwordInput = page.locator('[data-testid="password-input"]');
    this.loginButton = page.locator('[data-testid="login-button"]');
    this.errorMessage = page.locator('[data-testid="error-message"]');
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }
}
```

#### Screenshot Rules
```javascript
// Always take screenshots for debugging
await page.screenshot({ 
  path: `screenshots/test-${Date.now()}.png`,
  fullPage: true 
});

// Take screenshots on failures
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== testInfo.expectedStatus) {
    await page.screenshot({
      path: `screenshots/failure-${testInfo.title}-${Date.now()}.png`,
      fullPage: true
    });
  }
});
```

#### Wait Strategies
```javascript
// Wait for network idle before assertions
await page.waitForLoadState('networkidle');

// Wait for specific elements
await page.waitForSelector('[data-testid="success-message"]');

// Wait for API calls to complete
await page.waitForResponse(response => 
  response.url().includes('/api/login') && response.status() === 200
);
```

---

## 📊 PERFORMANCE RULES

### RULE 14: Performance Standards

#### Bundle Size Limits
- **JavaScript bundles**: < 250KB gzipped
- **CSS bundles**: < 50KB gzipped  
- **Images**: Use WebP when possible, < 500KB each
- **Fonts**: Subset fonts, preload critical fonts

#### Loading Performance
```javascript
// Lazy load components
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  // Expensive rendering logic
});

// Debounce search inputs
const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => clearTimeout(handler);
  }, [value, delay]);
  
  return debouncedValue;
};
```

---

## 🎯 SESSION MANAGEMENT RULES

### RULE 15: Development Session Best Practices

#### Session Start Checklist
1. [ ] Read this rulebook
2. [ ] Run project onboarding script
3. [ ] Check service health
4. [ ] Review recent changes/commits
5. [ ] Understand current task/goal

#### Session End Checklist
1. [ ] Commit working changes
2. [ ] Update documentation if needed
3. [ ] Note any issues for next session
4. [ ] Clean up temporary files
5. [ ] Stop services if not needed

#### Context Preservation
```bash
# Always document significant decisions
echo "$(date): Fixed authentication by updating AuthContext response handling" >> SESSION_NOTES.md

# Save important commands used
echo "docker-compose build --no-cache frontend" >> USEFUL_COMMANDS.md

# Track debugging steps
echo "Checked: docker logs, curl tests, browser console" >> DEBUG_LOG.md
```

---

## 🚨 EMERGENCY PROCEDURES

### RULE 16: Emergency Response

#### System Down Emergency
```bash
# 1. Quick assessment
docker-compose ps
docker system df  # Check disk space

# 2. Try gentle restart
docker-compose restart

# 3. If that fails, full restart
docker-compose down
docker-compose up -d

# 4. If still failing, rebuild
docker-compose down --volumes
docker-compose build --no-cache
docker-compose up -d
```

#### Data Recovery
```bash
# Database recovery
docker-compose exec postgres pg_dump -U veogen veogen > emergency_backup.sql

# Volume inspection
docker volume ls
docker volume inspect veogen_postgres_data
```

#### Communication Protocol
- **Document all emergency steps taken**
- **Note time and symptoms**
- **Save logs before making changes**
- **Test incrementally after fixes**

---

## 📚 LEARNING & IMPROVEMENT RULES

### RULE 17: Continuous Improvement

#### Post-Incident Review
After any significant issue:
1. **Document what went wrong**
2. **Identify root cause**
3. **Update this rulebook if needed**
4. **Add prevention measures**
5. **Share learnings with team**

#### Knowledge Capture
```markdown
# Add new rules as they're discovered
## RULE 18: New Discovery
Brief description of the rule and why it's important.

### Example
Code or command example showing the rule in action.

### Rationale
Explanation of why this rule exists and what problems it prevents.
```

---

## 🎉 SUCCESS METRICS

### RULE 18: Definition of Done

#### Feature Complete Criteria
- [ ] Functionality works as specified
- [ ] Tests pass (unit, integration, e2e)
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Performance requirements met
- [ ] Security review passed
- [ ] Accessibility requirements met
- [ ] Browser compatibility verified

#### Quality Gates
- **Code Coverage**: > 80%
- **Build Time**: < 5 minutes
- **Test Execution**: < 2 minutes
- **Bundle Size**: Within limits
- **Performance Score**: > 90 (Lighthouse)

---

**📝 This rulebook is a living document. Update it as you learn new patterns and discover better practices!**

**🚀 Always refer to this rulebook when starting development sessions or encountering challenges.**

---

## 💻 WINDOWS COMPATIBILITY RULES

### RULE 19: Unicode Character Avoidance
**Always avoid Unicode characters in Python output for Windows compatibility**

#### The Problem
Windows console (Command Prompt) uses CP1252 encoding by default, which cannot display many Unicode characters like:
- ✅ (U+2705) - Check mark
- ❌ (U+274C) - Cross mark  
- 🎉 (U+1F389) - Party popper
- 📁 (U+1F4C1) - File folder
- ⚠️ (U+26A0) - Warning sign

#### The Solution
```python
# ❌ BAD - Will crash on Windows
print("✅ Success: Build completed!")
print("🎉 All tests passed!")

# ✅ GOOD - Windows compatible
print("SUCCESS: Build completed!")
print("PASSED: All tests passed!")
print("ERROR: Build failed")
print("WARNING: Service degraded")
```

#### Safe Alternatives
```python
# Use text-based indicators
symbols = {
    'success': 'SUCCESS',
    'error': 'ERROR', 
    'warning': 'WARNING',
    'info': 'INFO',
    'passed': 'PASSED',
    'failed': 'FAILED',
    'ok': 'OK',
    'missing': 'MISSING'
}

# Example usage
print(f"{symbols['success']}: Authentication working")
print(f"{symbols['ok']}: All services running")
```

#### File Output Rules
```python
# For files, Unicode is usually OK (UTF-8 encoding)
with open('output.md', 'w', encoding='utf-8') as f:
    f.write("# ✅ Success Report\n")  # OK in files

# But console output must be safe
print("SUCCESS: Report generated")  # Safe for console
```

---

## 🔄 INCREMENTAL BUILD RULES

### RULE 20: Smart Build Strategy
**Only rebuild what's necessary - avoid the "10 minute monster rebuild"**

#### Build Analysis First
```bash
# Before any rebuild, check what actually changed
git status
git diff --name-only HEAD~1

# Check if rebuild is needed
docker-compose ps  # Are services running?
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}"
```

#### Incremental Build Strategy
```bash
# 1. Try service restart first (30 seconds)
docker-compose restart frontend
docker-compose restart backend

# 2. If restart doesn't work, try reload (1 minute)
docker-compose up -d frontend
docker-compose up -d backend

# 3. Only if code changes, rebuild specific service (2-5 minutes)
docker-compose build frontend
docker-compose up -d frontend

# 4. Last resort: Full rebuild (10+ minutes)
docker-compose build --no-cache
```

#### When Full Rebuild is Needed
- ❌ **Never needed for**: CSS changes, JS changes, minor bug fixes
- ❌ **Never needed for**: Environment variable changes
- ❌ **Never needed for**: Configuration file updates
- ✅ **Only needed for**: Package.json changes, Dockerfile changes, dependency updates

#### Smart Build Commands
```bash
# Check what needs rebuilding
docker-compose config --quiet && echo "Config OK" || echo "Config has issues"

# Frontend-only changes (CSS, JS, React components)
docker-compose restart frontend  # 30 seconds

# Backend-only changes (Python code, API endpoints)  
docker-compose restart backend   # 30 seconds

# Dependency changes (package.json, requirements.txt)
docker-compose build frontend    # 3-5 minutes
docker-compose build backend     # 2-3 minutes

# Dockerfile changes (rare)
docker-compose build --no-cache service-name  # 5-10 minutes

# Nuclear option (almost never needed)
docker-compose down --volumes
docker-compose build --no-cache  # 10+ minutes
```

#### Build Decision Tree
```bash
# Decision flow for builds
if [changed files are CSS/JS/React only]; then
    docker-compose restart frontend
elif [changed files are Python/API only]; then
    docker-compose restart backend  
elif [package.json or requirements.txt changed]; then
    docker-compose build frontend  # or backend
elif [Dockerfile changed]; then
    docker-compose build --no-cache service-name
else
    # Just restart - probably config change
    docker-compose restart
fi
```

#### Hot Reload Detection
```bash
# Check if hot reload is working
# Frontend: Look for "webpack compiled" messages
docker-compose logs frontend --tail=10

# Backend: Look for "Uvicorn running" messages  
docker-compose logs backend --tail=10

# If hot reload working, NO BUILD NEEDED!
```

#### Build Verification
```bash
# After any build, verify quickly
docker-compose ps  # Check status
curl -f http://localhost:4710 || echo "Frontend not ready"
curl -f http://localhost:4700/health || echo "Backend not ready"

# If verification fails, THEN consider larger rebuild
```

#### Time Budgets
- **Config changes**: 0 minutes (just restart)
- **Code changes**: 0 minutes (hot reload)
- **Package changes**: 2-5 minutes (targeted rebuild)  
- **Docker changes**: 5-10 minutes (cache rebuild)
- **Nuclear rebuild**: 10+ minutes (last resort only)

#### Emergency Build Recovery
```bash
# If stuck in build hell, try staged recovery
docker-compose down
docker system prune -f  # Clean up
docker-compose pull     # Get fresh base images
docker-compose build --pull --no-cache  # One-time full rebuild
```

---

## 📝 RULEBOOK EVOLUTION

### RULE 21: Living Document Principle
**This rulebook grows and improves based on real experience**

#### Adding New Rules
When you discover a new pattern or encounter a recurring issue:
1. Document the problem clearly
2. Provide the solution with examples
3. Add it as a new rule
4. Update the quick reference if critical
5. Test the rule in practice

#### Rule Validation
```bash
# Test new rules by running the validation
python validate_rulebook.py
```

**Keep this rulebook current and relevant - it's your development superpower!**
