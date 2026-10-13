# 👥 VeoGen User Manager

**A beautiful, standalone user management tool for VeoGen platform administration**

## 📋 Overview

The VeoGen User Manager is a comprehensive web-based tool that provides complete user administration capabilities independent of the main VeoGen application. Built with modern web technologies, it offers real-time user management, analytics, and administrative operations through an intuitive interface.

## ✨ Features

### 🔧 **Core User Management**
- **Complete CRUD Operations**: Create, read, update, delete user accounts
- **User Profile Management**: Edit names, emails, usernames, and settings
- **Account Status Control**: Activate, deactivate, and manage user states
- **Role Assignment**: Manage user roles (free, premium, admin)
- **Password Management**: Reset passwords and force password changes

### 📊 **Analytics & Insights**
- **Real-time Statistics**: Live user counts, activity metrics, and system health
- **User Activity Tracking**: Login patterns, feature usage, and engagement metrics
- **Performance Analytics**: API usage, video generation statistics, and resource utilization
- **Visual Dashboards**: Charts and graphs for data visualization
- **Historical Trends**: Time-series analysis of user behavior

### 🛠️ **Administrative Tools**
- **Advanced Search**: Multi-field search with complex filtering
- **Bulk Operations**: Mass user updates, deletions, and role changes
- **Data Export**: CSV, JSON, and Excel export with customizable fields
- **Audit Logging**: Complete action history and administrative tracking
- **Real-time Notifications**: Live updates and system alerts

## 🚀 Quick Start

### Prerequisites
- VeoGen main services running (PostgreSQL on port 4715)
- Python 3.11+ installed
- Modern web browser

### Installation
```bash
# Navigate to user manager directory
cd tools/user-manager

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

### Access
- **Frontend**: http://localhost:8100
- **API Documentation**: http://localhost:8100/docs

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL (direct connection to VeoGen DB)
- **Authentication**: Session-based admin authentication
- **API**: RESTful design with OpenAPI documentation

### Frontend Stack
- **Technology**: Vanilla HTML5/CSS3/JavaScript
- **Design**: Glass morphism with gradient aesthetics
- **Responsiveness**: Mobile-first responsive design
- **Updates**: Real-time data with live refresh

## 📡 API Reference

### User Management Endpoints

#### Get All Users
```http
GET /api/users
```

#### Create New User
```http
POST /api/users
Content-Type: application/json

{
    "email": "newuser@example.com",
    "username": "newuser",
    "full_name": "New User",
    "password": "securepassword",
    "plan": "free",
    "is_active": true
}
```

#### Update User
```http
PUT /api/users/{user_id}
Content-Type: application/json

{
    "email": "updated@example.com",
    "full_name": "Updated Name",
    "plan": "premium",
    "is_active": true
}
```

#### Delete User
```http
DELETE /api/users/{user_id}
```

#### Toggle User Status
```http
PATCH /api/users/{user_id}/status
Content-Type: application/json

{
    "is_active": false
}
```

### Analytics Endpoints

#### Dashboard Statistics
```http
GET /api/analytics/overview
```

#### Individual User Analytics
```http
GET /api/analytics/users/{user_id}
```

## 🎨 User Interface

### Dashboard Overview
- **Statistics Cards**: Key metrics with real-time updates
- **Activity Feed**: Recent user activities and system events
- **Quick Actions**: Common administrative tasks
- **Search Bar**: Global user search with instant results

### User Management Grid
- **Card Layout**: Beautiful user cards with avatars and key info
- **Advanced Filtering**: Search by name, email, plan, status, date range
- **Bulk Selection**: Checkbox system for mass operations
- **Inline Actions**: Quick edit, activate/deactivate, delete buttons

### User Detail Modal
- **Comprehensive Profile**: All user information in organized tabs
- **Activity Timeline**: Chronological activity history
- **Analytics Charts**: Visual metrics for individual users
- **Quick Edit Mode**: Inline editing with instant save

## 🧪 Testing

### API Testing
```bash
# Test user listing
curl -X GET "http://localhost:8100/api/users"

# Test user creation
curl -X POST "http://localhost:8100/api/users" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "username": "testuser",
       "full_name": "Test User",
       "password": "testpass123",
       "plan": "free"
     }'
```

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=4715
export DB_NAME=veogen
export DB_USER=veogen
export DB_PASSWORD=veogen123

# Start production server
uvicorn server:app --host 0.0.0.0 --port 8100 --workers 4
```

## 🔐 Security

### Authentication
- Session-based authentication for administrators
- Secure session tokens with configurable expiration
- IP-based access restrictions (optional)

### Data Protection
- All database queries use parameterized statements
- Input validation on both client and server
- XSS protection with Content Security Policy
- CSRF protection for all state-changing operations

## 📊 Monitoring

### Performance Metrics
- API response times per endpoint
- Database query performance
- Memory and CPU usage
- Concurrent user connections

### Health Checks
```python
@app.get("/health")
async def health_check():
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        return {"status": "healthy", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection manually
psql -h localhost -p 4715 -U veogen -d veogen

# Verify credentials in environment
```

#### Frontend Not Loading
```bash
# Check if server is running
curl http://localhost:8100/health

# Check browser console for JavaScript errors
```

## 📈 Analytics

### Key Metrics to Track
- **User Growth**: Daily, weekly, monthly user registrations
- **User Engagement**: Login frequency and session duration
- **Feature Usage**: Most used features and user paths
- **Performance**: API response times and error rates

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Follow PEP 8 for Python, use ESLint for JavaScript
2. **Testing**: Add tests for all new features
3. **Documentation**: Update README and API docs for changes
4. **Security**: Review security implications of all changes

---

## 🎉 Conclusion

The VeoGen User Manager provides a comprehensive, modern solution for user administration that combines powerful functionality with an exceptional user experience. With its clean architecture, real-time capabilities, and beautiful interface, it serves as an essential tool for VeoGen platform administration.

**Ready to get started?** Follow the Quick Start guide and begin managing your VeoGen users with style! 🚀