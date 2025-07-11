# Settings Page Fix Plan

## Problem Summary
The Settings page save button always fails because frontend is calling non-existent API endpoints. The backend has basic settings but no profile or API key management.

## Step-by-Step Fix Plan

### Phase 1: Backend API Implementation (2-3 hours)

#### 1.1 Create Profile Management Endpoints
**File**: `backend/app/api/api_v1/endpoints/profile.py` (NEW)
```python
# Implement these endpoints:
GET  /api/v1/auth/profile      # Get user profile
PUT  /api/v1/auth/profile      # Update user profile
```

#### 1.2 Fix Settings Endpoints  
**File**: `backend/app/api/api_v1/endpoints/settings.py` (MODIFY)
```python
# Add missing endpoints:
PUT  /api/v1/auth/settings     # Individual setting update
GET  /api/v1/auth/settings     # Get all user settings
```

#### 1.3 Create API Key Management Endpoints
**File**: `backend/app/api/api_v1/endpoints/api_keys.py` (NEW)
```python
# Implement full CRUD:
GET    /api/v1/auth/api-keys           # List user's API keys
POST   /api/v1/auth/api-keys           # Create new API key
PUT    /api/v1/auth/api-keys/{id}      # Update API key
DELETE /api/v1/auth/api-keys/{id}      # Delete API key
```

#### 1.4 Create Database Models
**File**: `backend/app/models/api_key.py` (NEW)
```python
# Table for storing encrypted API keys:
class APIKey(Base):
    id, user_id, service_name, key_name
    encrypted_api_key, status, created_at, last_used
```

#### 1.5 Update Router Registration
**File**: `backend/app/main.py` (MODIFY)
```python
# Add new routers:
from app.api.api_v1.endpoints import profile, api_keys
app.include_router(profile.router, prefix="/api/v1/auth", tags=["profile"])
app.include_router(api_keys.router, prefix="/api/v1/auth", tags=["api-keys"])
```

### Phase 2: Database Schema Updates (1 hour)

#### 2.1 Create API Keys Table Migration
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    service_name VARCHAR(50) NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    encrypted_api_key TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP,
    UNIQUE(user_id, service_name, key_name)
);
```

#### 2.2 Update User Settings Table (if needed)
```sql
-- Ensure user_settings table exists and supports all preference types
-- May need to add columns for new preference types
```

### Phase 3: Frontend Fixes (1-2 hours)

#### 3.1 Fix API Endpoint URLs
**File**: `frontend/src/components/settings/Settings.jsx` (MODIFY)
```javascript
// Fix these API calls:
- GET /api/v1/auth/profile ✓ (keep - will be implemented)
- PUT /api/v1/auth/profile ✓ (keep - will be implemented)  
- GET /api/v1/auth/api-keys ✓ (keep - will be implemented)
- PUT /api/v1/auth/settings ✓ (keep - will be implemented)
```

#### 3.2 Add Error Handling
```javascript
// Add better error messages:
- Network connection errors
- Validation errors from backend
- Success confirmations
- Loading states
```

#### 3.3 Fix HTTP Methods and Payloads
```javascript
// Ensure request formats match backend expectations:
- Settings update payload structure
- Profile update validation
- API key encryption handling
```

### Phase 4: Security & Encryption (1 hour)

#### 4.1 API Key Encryption Service
**File**: `backend/app/services/encryption_service.py` (NEW)
```python
# Implement AES encryption for API keys:
- encrypt_api_key()
- decrypt_api_key()  
- key derivation from user password/secret
```

#### 4.2 API Key Validation
```python
# Add validation for different API key formats:
- Google API Key format validation
- OpenAI API Key format validation
- Generic key validation
```

### Phase 5: Testing & Validation (1 hour)

#### 5.1 Backend API Testing
```bash
# Test all new endpoints:
curl -X GET /api/v1/auth/profile
curl -X PUT /api/v1/auth/profile -d '{...}'
curl -X GET /api/v1/auth/api-keys
curl -X POST /api/v1/auth/api-keys -d '{...}'
```

#### 5.2 Frontend Integration Testing
```javascript
// Test complete workflow:
1. Load settings page
2. Modify profile information  
3. Add API key
4. Save preferences
5. Verify all saves work
```

#### 5.3 Connection Testing
```python
# Verify connection test endpoint exists and works:
POST /api/v1/enhanced-auth/test-connection
```

## Implementation Priority

### 🔥 Critical (Fix Immediately)
1. **Fix Settings Save** - Create missing PUT /api/v1/auth/settings endpoint
2. **Fix Profile Save** - Create missing profile endpoints
3. **Update Frontend URLs** - Fix API endpoint mismatches

### 🟡 Important (Next Session)  
4. **API Key Management** - Full CRUD implementation
5. **Connection Testing** - Verify and fix test endpoint
6. **Database Migration** - Add API keys table

### 🔵 Enhancement (Future)
7. **API Key Encryption** - Secure storage implementation
8. **Input Validation** - Better error handling
9. **UI/UX Polish** - Loading states and confirmations

## Files That Need Changes

### New Files to Create:
- `backend/app/api/api_v1/endpoints/profile.py`
- `backend/app/api/api_v1/endpoints/api_keys.py` 
- `backend/app/models/api_key.py`
- `backend/app/services/encryption_service.py`
- Database migration script

### Existing Files to Modify:
- `backend/app/api/api_v1/endpoints/settings.py`
- `backend/app/main.py` 
- `frontend/src/components/settings/Settings.jsx`

## Root Cause Analysis

### Problem
Frontend Settings.jsx is trying to call endpoints that were never implemented:

#### Missing/Wrong Endpoints:
1. **Profile Management**: 
   - Frontend calls: `GET/PUT /api/v1/auth/profile` 
   - Backend reality: **DOESN'T EXIST**

2. **Settings Update**:
   - Frontend calls: `PUT /api/v1/auth/settings`
   - Backend reality: `POST /api/v1/settings/` (wrong URL + wrong HTTP method)

3. **API Key Management**:
   - Frontend calls: `GET/POST/PUT /api/v1/auth/api-keys`
   - Backend reality: **DOESN'T EXIST**

4. **Connection Testing**:
   - Frontend calls: `POST /api/v1/enhanced-auth/test-connection`
   - Backend reality: **UNKNOWN** (need to verify)

### Current Working Endpoints
Based on main.py router setup:
- `/api/v1/settings/` - Basic settings (POST only)
- `/api/v1/auth/` - Basic auth endpoints
- `/api/v1/enhanced-auth/` - Enhanced auth endpoints

## Estimated Time: 5-7 hours total
- Phase 1 (Backend): 2-3 hours
- Phase 2 (Database): 1 hour  
- Phase 3 (Frontend): 1-2 hours
- Phase 4 (Security): 1 hour
- Phase 5 (Testing): 1 hour

## Success Criteria
✅ Settings page loads without errors  
✅ Profile information can be updated and saved  
✅ User preferences can be modified and saved  
✅ API keys can be added, edited, and deleted  
✅ Connection testing works properly  
✅ All saves show success messages instead of failures  
✅ No console errors in browser developer tools

## Next Session Instructions

When continuing this work in 2 hours:

1. **Read this file first**: `docs/development/SETTINGS_PAGE_FIX_PLAN.md`
2. **Start with Phase 1.1**: Create profile endpoints (quickest win)
3. **Test immediately**: After each endpoint, test with curl/Postman
4. **Use the restart guide**: Follow `CLAUDE_RESTART_GUIDE.md` for context
5. **Check basic memory**: Switch to veogen project for stored info

## Related Files
- **Problem documentation**: See `todo/` folder for bug report
- **User model**: `backend/app/models/user.py` (shows available fields)
- **Current settings**: `backend/app/api/api_v1/endpoints/settings.py`
- **Frontend code**: `frontend/src/components/settings/Settings.jsx`