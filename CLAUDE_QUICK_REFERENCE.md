# 🚀 Claude Developer Quick Reference Card

## 🔥 CRITICAL RULES (Always Remember!)

### 1. Session Start Protocol
```bash
read_file("CLAUDE_DEV_RULEBOOK.md")     # ALWAYS FIRST!
execute_command("python claude_onboard.py", 30000)
```

### 2. Build Patience (RULE 2)
- Frontend builds: Wait 5+ minutes (300 seconds)
- Docker builds: Wait 10+ minutes (600 seconds)  
- Never declare failed before timeout!

### 3. Debug Sequence (RULE 5)
```bash
docker-compose ps                        # 1. Check services
docker-compose logs service --tail=20    # 2. Check logs
curl -v http://localhost:4700/health     # 3. Test endpoints
python test_final_auth.py               # 4. Run tests
```

### 4. CSS Standards (RULE 4)
```css
/* BEM Methodology */
.component-name {}                 /* Block */
.component-name__element {}        /* Element */  
.component-name--modifier {}       /* Modifier */
```

### 5. Error Handling (RULE 9)
```javascript
try {
  const result = await apiCall();
  return result;
} catch (error) {
  console.error('Operation failed:', error);
  logger.addLog('error', `API call failed: ${error.message}`);
  return null; // Safe fallback
}
```

### 6. Test Timeouts
```bash
execute_command("npm test", 120000)           # 2 minutes
execute_command("python test_final_auth.py", 30000)  # 30 seconds
execute_command("npx playwright test", 300000)       # 5 minutes
```

### 7. Logger Modal Structure
```javascript
window.logger.addLog('error', 'Something failed');
window.logger.addLog('info', 'Process completed');
window.logger.show(); // Display modal
```

### 8. Security Rules (RULE 12)
- ❌ Never log passwords/tokens
- ✅ Always sanitize user input
- ✅ Validate API responses
- ✅ Use secure token storage

### 9. Emergency Recovery
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
# Wait 30 seconds, then test
python test_final_auth.py
```

### 10. Performance Standards (RULE 14)
- JS bundles: < 250KB gzipped
- CSS bundles: < 50KB gzipped
- Images: < 500KB each
- Build time: < 5 minutes

### 11. Unicode Safety (RULE 19) - CRITICAL!
```python
# ❌ NEVER - Will crash on Windows
print("✅ Success!")

# ✅ ALWAYS - Windows compatible  
print("SUCCESS: Operation completed")
print("ERROR: Something failed")
print("WARNING: Check this")
```

### 12. Smart Builds (RULE 20) - CRITICAL!
```bash
# 1. Try restart first (30 seconds)
docker-compose restart frontend

# 2. Only rebuild if packages changed (3-5 minutes)
docker-compose build frontend

# 3. NEVER do full rebuild unless Dockerfile changed
# Avoid: docker-compose build --no-cache (10+ minutes)
```

#### Build Decision Tree
- CSS/JS changes → `restart` (30 sec)
- Python/API changes → `restart` (30 sec)  
- package.json changes → `build service` (3-5 min)
- Dockerfile changes → `build --no-cache service` (5-10 min)
- NEVER full rebuild unless absolutely necessary!

---

**📖 For complete rules, read: CLAUDE_DEV_RULEBOOK.md**
**🚀 For project setup: NEW_SESSION_START.md**
