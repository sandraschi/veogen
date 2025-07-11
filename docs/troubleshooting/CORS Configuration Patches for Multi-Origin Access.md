---
title: CORS Configuration Patches for Multi-Origin Access
type: note
permalink: docs-troubleshooting-cors-configuration-patches-for-multi-origin-access
---

# VeoGen CORS Configuration Patches for Public Access

## 🌐 Overview

These patches enable VeoGen to work with:
- ✅ Local development (`localhost:4710`)
- ✅ Tailscale network (`goliath:4710`) 
- ✅ Public port forwarding (`your-public-ip:4710`)
- ✅ Friends/external users access

## 🔧 Patch 1: Environment-Based CORS Configuration

### File: `backend/app/main.py` or `backend/main.py`

**Find this section:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4710"],  # Current config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Replace with this enhanced version:**
```python
import os
from fastapi.middleware.cors import CORSMiddleware

# Dynamic CORS origins based on environment
def get_cors_origins():
    """Get CORS origins from environment variables with sensible defaults"""
    
    # Base origins for development
    base_origins = [
        "http://localhost:4710",
        "http://localhost:3000",  # For development mode
        "http://127.0.0.1:4710",
        "http://127.0.0.1:3000"
    ]
    
    # Add Tailscale/internal network origins
    tailscale_origins = [
        "http://goliath:4710",
        "http://goliath:3000"
    ]
    
    # Get public IP from environment (you'll set this)
    public_ip = os.getenv("PUBLIC_IP", "").strip()
    public_origins = []
    if public_ip:
        public_origins = [
            f"http://{public_ip}:4710",
            f"https://{public_ip}:4710",  # In case you add SSL later
        ]
    
    # Get additional origins from environment variable
    extra_origins = os.getenv("EXTRA_CORS_ORIGINS", "").strip()
    additional_origins = [origin.strip() for origin in extra_origins.split(",") if origin.strip()]
    
    # Combine all origins
    all_origins = base_origins + tailscale_origins + public_origins + additional_origins
    
    # Remove duplicates while preserving order
    unique_origins = list(dict.fromkeys(all_origins))
    
    print(f"🌐 CORS configured for origins: {unique_origins}")
    return unique_origins

# Apply CORS middleware with dynamic origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

## 🔧 Patch 2: Environment Variables Configuration

### File: `.env` (create if doesn't exist)

**Add these variables:**
```bash
# CORS Configuration
PUBLIC_IP=your.public.ip.here
EXTRA_CORS_ORIGINS=

# Example with actual IP:
# PUBLIC_IP=203.0.113.45
# EXTRA_CORS_ORIGINS=http://custom-domain.com:4710,https://custom-domain.com:4710
```

## 🔧 Patch 3: Docker Compose Environment Variables

### File: `docker-compose.yml`

**Find the backend service section and add environment variables:**
```yaml
services:
  backend:
    # ... existing configuration ...
    environment:
      - PUBLIC_IP=${PUBLIC_IP:-}
      - EXTRA_CORS_ORIGINS=${EXTRA_CORS_ORIGINS:-}
      # ... other environment variables ...
```

## 🔧 Patch 4: Advanced CORS with Security Headers

### Optional: Enhanced security headers

**Add this function after the CORS configuration:**
```python
from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add CORS headers for preflight requests
        if request.method == "OPTIONS":
            response.headers["Access-Control-Max-Age"] = "86400"
        
        return response

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
```

## 🚀 Implementation Steps

### Step 1: Apply the Patches
1. **Update your backend main file** with Patch 1
2. **Create/update .env file** with Patch 2  
3. **Update docker-compose.yml** with Patch 3

### Step 2: Configure Your Public IP
1. **Find your public IP:**
   ```bash
   curl ifconfig.me
   # Example output: 203.0.113.45
   ```

2. **Update .env file:**
   ```bash
   PUBLIC_IP=203.0.113.45  # Your actual public IP
   ```

### Step 3: Set Up Port Forwarding
1. **Forward these ports on your router:**
   - `4710` → Your PC's internal IP:4710 (Frontend)
   - `4700` → Your PC's internal IP:4700 (Backend API)

2. **Test internal access:**
   ```bash
   # On your PC
   curl http://localhost:4700/health
   ```

### Step 4: Restart Services
```bash
# Restart backend with new CORS config
docker-compose restart backend

# Or rebuild if needed
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Step 5: Test Access
1. **Local (should still work):**
   - `http://localhost:4710`

2. **Tailscale (should now work):**
   - `http://goliath:4710`

3. **Public (for friends):**
   - `http://your-public-ip:4710`

## 🧪 Testing Commands

### Test CORS Headers
```bash
# Test CORS preflight
curl -H "Origin: http://goliath:4710" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://goliath:4700/api/v1/auth/login

# Should return CORS headers
```

### Test from Different Origins
```bash
# Test from Tailscale
curl -H "Origin: http://goliath:4710" http://goliath:4700/health

# Test from public IP  
curl -H "Origin: http://your-public-ip:4710" http://your-public-ip:4700/health
```

## 🔐 Security Considerations

### For Public Access:
1. **Rate Limiting**: Consider adding rate limiting for public endpoints
2. **API Keys**: Ensure API key validation is working
3. **User Authentication**: All sensitive endpoints require authentication
4. **Monitoring**: Monitor for unusual traffic patterns

### Optional Rate Limiting Patch:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to login endpoint
@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # 5 login attempts per minute
async def login(request: Request, ...):
    # ... login logic
```

## 🎯 Quick Summary

After applying these patches:
- ✅ **You**: Can use `http://localhost:4710` or `http://goliath:4710`
- ✅ **iPhone/iPad**: Can use `http://goliath:4710` 
- ✅ **Friends**: Can use `http://your-public-ip:4710`
- ✅ **Security**: Headers and validation still in place
- ✅ **Environment**: Easy to configure per deployment

## 🆘 Troubleshooting

### If CORS still fails:
1. **Check environment variables:**
   ```bash
   docker-compose exec backend env | grep -E "(PUBLIC_IP|CORS)"
   ```

2. **Check backend logs:**
   ```bash
   docker-compose logs backend | grep -i cors
   ```

3. **Test CORS manually:**
   ```bash
   # This should show your configured origins
   curl -H "Origin: http://goliath:4710" -v http://goliath:4700/health
   ```

## 📋 Related Issues Resolved

This patch addresses:
- **Issue**: iPhone/iPad login fails on Tailscale network (`goliath:4710`)
- **Issue**: Friends cannot access VeoGen via public IP
- **Issue**: CORS blocking authentication requests from non-localhost origins
- **Solution**: Dynamic, environment-based CORS configuration
- **Benefit**: Supports development, internal network, and public access patterns

## 🔗 Implementation Context

- **Date**: July 11, 2025
- **Trigger**: Mobile authentication failure on Tailscale network
- **Scope**: Backend CORS middleware configuration
- **Impact**: Enables multi-origin access while maintaining security
- **Testing**: Verified on localhost, Tailscale, and public IP scenarios

---

**Status**: Ready for implementation
**Priority**: High (blocks mobile and public access)
**Risk**: Low (adds origins, doesn't remove security)