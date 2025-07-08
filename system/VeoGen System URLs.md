---
title: VeoGen System URLs
type: note
permalink: system-veo-gen-system-urls
tags:
- urls
- access
- ports
- docker
---

# VeoGen System URLs & Access Points

## Frontend URLs
- **Main App**: http://localhost:4710
- **Login Page**: http://localhost:4710/auth
- **Email Verification**: http://localhost:4710/verify-email
- **Password Reset**: http://localhost:4710/reset-password

## Backend URLs
- **API Base**: http://localhost:4700
- **API Documentation**: http://localhost:4700/docs
- **Health Check**: http://localhost:4700/health

## Monitoring & Admin
- **Grafana Dashboard**: http://localhost:4725 (admin/veogen123)
- **Prometheus**: http://localhost:4740
- **Database**: PostgreSQL on port 4715

## Docker Services
- Frontend: port 4710
- Backend: port 4700 
- Database: port 4715
- Redis: port 4720
- Grafana: port 4725

## Project Location
```
C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen
```

Updated: July 6, 2025