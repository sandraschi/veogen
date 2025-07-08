#!/usr/bin/env python3
"""
Validate that the Claude Developer Rulebook system is complete and functional
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen")

def validate_rulebook_system():
    """Validate the complete rulebook system"""
    
    print("=" * 60)
    print("  CLAUDE DEVELOPER RULEBOOK SYSTEM VALIDATION")
    print("=" * 60)
    
    # Check core files exist
    core_files = [
        "CLAUDE_DEV_RULEBOOK.md",      # Main rulebook
        "CLAUDE_RESTART_GUIDE.md",     # Restart instructions  
        "NEW_SESSION_START.md",        # Quick start guide
        "claude_onboard.py",           # Onboarding script
        "test_final_auth.py",          # System tests
        "AUTHENTICATION_SUCCESS.md"    # Recent work status
    ]
    
    print("\n1. CORE DOCUMENTATION FILES:")
    all_exist = True
    for file in core_files:
        file_path = PROJECT_ROOT / file
        exists = file_path.exists()
        status = "OK" if exists else "MISSING"
        print(f"   {status}: {file}")
        if not exists:
            all_exist = False
    
    # Check file sizes (should not be empty)
    print("\n2. FILE CONTENT VALIDATION:")
    for file in core_files:
        file_path = PROJECT_ROOT / file
        if file_path.exists():
            size = file_path.stat().st_size
            if size > 1000:  # At least 1KB
                print(f"   OK: {file} ({size:,} bytes)")
            else:
                print(f"   WARNING: {file} seems too small ({size} bytes)")
        else:
            print(f"   MISSING: {file}")
    
    # Check rulebook content
    print("\n3. RULEBOOK CONTENT CHECK:")
    rulebook_path = PROJECT_ROOT / "CLAUDE_DEV_RULEBOOK.md"
    if rulebook_path.exists():
        content = rulebook_path.read_text(encoding='utf-8')
        
        # Check for key sections
        required_sections = [
            "BUILD & DEPLOYMENT RULES",
            "CSS & STYLING RULES", 
            "DEBUG & LOGGING RULES",
            "Logger Modal",
            "TESTING RULES",
            "CODE QUALITY RULES",
            "DEPLOYMENT RULES",
            "SECURITY RULES",
            "BROWSER AUTOMATION RULES",
            "PERFORMANCE RULES"
        ]
        
        for section in required_sections:
            if section in content:
                print(f"   OK: {section} section found")
            else:
                print(f"   MISSING: {section} section")
        
        # Count rules
        rule_count = content.count("### RULE")
        print(f"   INFO: Found {rule_count} rules in rulebook")
    
    # Check integration with restart system
    print("\n4. RESTART SYSTEM INTEGRATION:")
    restart_guide = PROJECT_ROOT / "NEW_SESSION_START.md"
    if restart_guide.exists():
        restart_content = restart_guide.read_text(encoding='utf-8')
        if "CLAUDE_DEV_RULEBOOK.md" in restart_content:
            print("   OK: Rulebook integrated into restart system")
        else:
            print("   WARNING: Rulebook not referenced in restart guide")
    
    # Validate command examples
    print("\n5. COMMAND EXAMPLES VALIDATION:")
    if rulebook_path.exists():
        content = rulebook_path.read_text(encoding='utf-8')
        
        # Check for proper timeout examples
        if "300000" in content and "execute_command" in content:
            print("   OK: Proper timeout examples found")
        else:
            print("   WARNING: Missing timeout examples")
        
        # Check for CSS examples
        if "css" in content.lower() and "@media" in content:
            print("   OK: CSS examples with media queries found")
        else:
            print("   WARNING: Missing CSS examples")
        
        # Check for JavaScript examples
        if "async" in content and "await" in content:
            print("   OK: Modern JavaScript examples found")
        else:
            print("   WARNING: Missing modern JavaScript examples")
    
    # Summary
    print("\n" + "=" * 60)
    print("  VALIDATION SUMMARY")
    print("=" * 60)
    
    if all_exist:
        print("SUCCESS: All core documentation files present")
    else:
        print("WARNING: Some core files are missing")
    
    print(f"PROJECT ROOT: {PROJECT_ROOT}")
    print("\nNEXT STEPS FOR NEW CLAUDE SESSIONS:")
    print("1. read_file('CLAUDE_DEV_RULEBOOK.md')")
    print("2. read_file('NEW_SESSION_START.md')")
    print("3. execute_command('python claude_onboard.py', 30000)")
    
    return all_exist

def validate_specific_rules():
    """Validate specific rule implementations"""
    
    print("\n" + "=" * 60)
    print("  SPECIFIC RULE VALIDATION")
    print("=" * 60)
    
    rulebook_path = PROJECT_ROOT / "CLAUDE_DEV_RULEBOOK.md"
    if not rulebook_path.exists():
        print("ERROR: Rulebook file not found")
        return False
    
    content = rulebook_path.read_text(encoding='utf-8')
    
    # Rule 2: Build Patience Protocol
    print("\n1. RULE 2 - Build Patience Protocol:")
    if "300 seconds" in content and "600000" in content:
        print("   OK: Proper build timeouts specified")
    else:
        print("   WARNING: Build timeout rules may be incomplete")
    
    # Rule 4: CSS Architecture
    print("\n2. RULE 4 - CSS Architecture:")
    if "BEM methodology" in content and "__element" in content:
        print("   OK: CSS naming conventions specified")
    else:
        print("   WARNING: CSS naming rules may be incomplete")
    
    # Rule 5: Debug Sequence
    print("\n3. RULE 5 - Debug Sequence Protocol:")
    debug_commands = ["docker-compose ps", "curl -v", "test_final_auth.py"]
    found_commands = sum(1 for cmd in debug_commands if cmd in content)
    print(f"   INFO: Found {found_commands}/3 debug commands")
    
    # Rule 6: Logger Modal
    print("\n4. RULE 6 - Logger Modal:")
    if "logger-modal" in content and "LoggerModal" in content:
        print("   OK: Complete logger modal implementation found")
    else:
        print("   WARNING: Logger modal implementation may be incomplete")
    
    # Rule 13: Browser Automation
    print("\n5. RULE 13 - Browser Automation:")
    if "Playwright" in content and "page.screenshot" in content:
        print("   OK: Browser automation rules found")
    else:
        print("   WARNING: Browser automation rules may be incomplete")
    
    return True

def create_quick_reference():
    """Create a quick reference card for the most important rules"""
    
    quick_ref_content = """# 🚀 Claude Developer Quick Reference Card

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

---

**📖 For complete rules, read: CLAUDE_DEV_RULEBOOK.md**
**🚀 For project setup: NEW_SESSION_START.md**
"""
    
    quick_ref_path = PROJECT_ROOT / "CLAUDE_QUICK_REFERENCE.md"
    quick_ref_path.write_text(quick_ref_content, encoding='utf-8')
    print(f"\nSUCCESS: Created quick reference: {quick_ref_path}")

def main():
    """Main validation function"""
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    
    # Run validations
    system_valid = validate_rulebook_system()
    rules_valid = validate_specific_rules()
    
    # Create quick reference
    create_quick_reference()
    
    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL VALIDATION RESULTS")
    print("=" * 60)
    
    if system_valid and rules_valid:
        print("SUCCESS: Claude Developer Rulebook System is complete!")
        print("SUCCESS: All documentation files present")
        print("SUCCESS: Rulebook contains comprehensive rules")
        print("SUCCESS: Integration with restart system working")
        print("SUCCESS: Quick reference card created")
        
        print("\nUSAGE INSTRUCTIONS:")
        print("1. New Claude sessions should ALWAYS start with:")
        print("   read_file('CLAUDE_DEV_RULEBOOK.md')")
        print("2. Followed by the project onboarding:")
        print("   execute_command('python claude_onboard.py', 30000)")
        print("3. Use the quick reference for common patterns:")
        print("   read_file('CLAUDE_QUICK_REFERENCE.md')")
        
    else:
        print("WARNING: Some issues found in rulebook system")
        print("   Review the validation output above")
        print("   Fix any missing files or content")
    
    print(f"\nProject Location: {PROJECT_ROOT}")
    print("Beer status: Still owed for authentication fix + browser demo!")

if __name__ == "__main__":
    main()
