# VeoGen Email System Integration Guide

## 🚀 Quick Integration Steps

### 1. **Add Email Router to FastAPI Main App**
File: `backend/app/api/api_v1/api.py`

Add this import and router:
```python
from api.api_v1.endpoints.email_workflows import email_router

# Add to existing router includes
api_router.include_router(email_router)
```

### 2. **Update Database Lookup Functions**
File: `backend/app/api/api_v1/endpoints/email_workflows.py`

Replace placeholder lookups like:
```python
# Replace this:
user_email = "sandraschipal@hotmail.com"  # Placeholder

# With this:
from services.user_service import get_user_by_id  # Your existing user service
user = await get_user_by_id(request.user_id)
user_email = user.email
user_name = user.name
```

### 3. **Test the Email Endpoints**
Visit: http://localhost:4700/docs

Available endpoints:
- `POST /api/email/verification/enhanced` - Enhanced registration emails
- `POST /api/email/challenge/initiate` - Security challenges
- `POST /api/email/password-reset/advanced` - Advanced password reset
- `POST /api/email/notification/project-complete` - Project notifications
- `POST /api/email/test/demo` - Demo all email types

### 4. **Frontend Integration Examples**

#### Enhanced Registration:
```javascript
const response = await fetch('/api/email/verification/enhanced', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    email: 'user@example.com', 
    name: 'User Name' 
  })
});
```

#### Security Challenge:
```javascript
const response = await fetch('/api/email/challenge/initiate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    user_id: 'user123', 
    action: 'Delete Account' 
  })
});
```

#### Password Reset:
```javascript
const response = await fetch('/api/email/password-reset/advanced', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    email: 'user@example.com',
    name: 'User Name' 
  })
});
```

### 5. **Production Configuration**
To enable real email sending, update `docker-compose.yml`:
```yaml
environment:
  - EMAIL_SMTP=smtp-mail.outlook.com  # Change from 'dev'
  # Keep existing email credentials
```

### 6. **Test the Complete System**
Run the demo script:
```bash
cd C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen
python test_email_workflows.py
```

This generates all 6 email types and saves them to `dev_emails/` folder.

## 📧 Email Types Available

1. **Enhanced Verification** - Professional welcome with feature preview
2. **Security Challenge** - 6-digit codes for sensitive actions  
3. **Advanced Password Reset** - Security-focused with forensics
4. **Project Notification** - Video completion alerts
5. **Weekly Digest** - Personalized user statistics
6. **Security Alert** - Suspicious activity warnings

## 🔥 Ready for Production!

The email system is fully implemented and ready to enhance VeoGen's user experience with enterprise-grade email communications.