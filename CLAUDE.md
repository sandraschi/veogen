# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VeoGen is a comprehensive AI-powered video generation platform built on Google's Veo AI technology. The architecture consists of:

- **Frontend**: React application (TypeScript) with Tailwind CSS, Material-UI, and modern state management
- **Backend**: FastAPI Python service with SQLAlchemy ORM, PostgreSQL database, and Redis caching
- **AI Services**: Google Veo for video generation, Gemini for text/chat, Imagen for images, Lyria for music
- **Monitoring Stack**: Grafana, Prometheus, Loki, Alertmanager for full observability
- **Infrastructure**: Docker Compose orchestration with comprehensive service mesh

## Key Features

- **Movie Maker**: Multi-scene video generation with frame continuity using FFmpeg
- **Text-to-Video**: 1-60 second video generation with multiple visual styles
- **Multi-modal AI**: Image generation, music creation, chat/text generation
- **User Management**: JWT authentication, secure API key storage, user settings
- **Production Monitoring**: Real-time metrics, alerts, and log aggregation

## Development Commands

### Quick Start
```bash
# Complete stack startup
./setup.sh          # Linux/Mac
setup.bat           # Windows

# Or manually with Docker Compose
docker-compose up -d
```

### Frontend Development
```bash
cd frontend
npm install
npm start           # Development server
npm run build       # Production build
npm test            # Run tests
npm run lint        # ESLint
npm run lint:fix    # Fix linting issues
npm run type-check  # TypeScript checking
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Frontend tests
cd frontend && npm test

# Backend tests (if pytest is configured)
cd backend && python -m pytest

# Health check
curl http://localhost:4700/health
```

### Database Operations
```bash
# Access PostgreSQL directly
docker-compose exec postgres psql -U veogen -d veogen

# Check database connection
curl http://localhost:4700/health
```

## Architecture Deep Dive

### Backend Structure
- **`app/main.py`**: FastAPI application entry point with middleware, routers, and lifecycle management
- **`app/config.py`**: Centralized configuration using Pydantic settings
- **`app/routers/`**: API route handlers for video, movie, music, image generation
- **`app/services/`**: Business logic services (video_service, movie_maker, gemini_service, etc.)
- **`app/models/`**: SQLAlchemy ORM models for database entities
- **`app/schemas/`**: Pydantic models for request/response validation
- **`app/utils/`**: Utility functions and shared components

### Frontend Structure
- **`src/pages/`**: Page components for different application sections
- **`src/components/`**: Reusable UI components
- **`src/services/`**: API communication services
- **`src/contexts/`**: React Context providers (AuthContext)
- **`src/hooks/`**: Custom React hooks
- **State Management**: Zustand for global state, React Query for server state

### Key Services Integration
- **FFmpeg Integration**: Video processing and frame continuity in movie maker
- **Google AI Services**: Veo for video, Gemini for text, Imagen for images
- **Authentication**: JWT-based with secure API key storage
- **Monitoring**: Prometheus metrics, Grafana dashboards, Loki logs

## Service Ports
- **Frontend**: 4710
- **Backend API**: 4700
- **Backend Metrics**: 4705
- **PostgreSQL**: 4715
- **Redis**: 4720
- **Grafana**: 4725
- **Prometheus**: 4740
- **Alertmanager**: 4745
- **Node Exporter**: 4750
- **cAdvisor**: 4755
- **Nginx**: 4760 (HTTP), 4765 (HTTPS)

## Environment Setup

Required environment variables (`.env`):
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-google-api-key
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=postgresql+asyncpg://veogen:veogen123@postgres:5432/veogen
REDIS_URL=redis://redis:6379
```

## Common Development Tasks

### Adding New AI Features
1. Create service in `backend/app/services/`
2. Add router in `backend/app/routers/`
3. Create corresponding frontend page/component
4. Update API client in `frontend/src/services/`

### Database Schema Changes
1. Modify models in `backend/app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

### Adding Monitoring
- Metrics are automatically collected via PrometheusMetricsMiddleware
- Custom metrics can be added using `prometheus_client`
- Dashboards are in `monitoring/grafana/dashboard-configs/`

## Production Considerations

- **Security**: API keys are encrypted, JWT tokens for authentication
- **Scaling**: Services can be scaled horizontally with Docker Compose
- **Monitoring**: Full observability stack with alerts and dashboards
- **Performance**: Redis caching, connection pooling, async operations
- **Resource Management**: Configurable limits for concurrent generations

## Troubleshooting

### Common Issues
- **Services won't start**: Check `docker-compose logs [service]`
- **API key issues**: Verify configuration in Settings page
- **Database connection**: Ensure PostgreSQL is running and accessible
- **Frontend build**: Check Node.js version and npm install

### Debug Commands
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service]

# Restart services
docker-compose restart [service]

# Health check
curl http://localhost:4700/health
```