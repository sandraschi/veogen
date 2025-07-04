# VeoGen - AI Video Generation Platform

VeoGen is a comprehensive AI-powered video generation platform that enables users to create professional-quality videos and complete movies using Google's Veo 3 model. The platform combines single video generation capabilities with an advanced Movie Maker feature that produces multi-scene movies with frame-to-frame continuity.

## 📋 Project Overview

**Product**: VeoGen - AI Video Generator & Movie Maker  
**Technology Stack**: FastAPI, React, PostgreSQL, Docker, Google Veo 3  
**Status**: Active Development - Movie Maker Phase  
**Repository**: [VeoGen GitHub](https://github.com/veogen/veogen)  

## 🎯 Core Features

### Single Video Generation
- Text-to-video generation using Google Veo 3
- Multiple visual styles (Anime, Pixar, Wes Anderson, Cinematic, etc.)
- Customizable parameters (duration, aspect ratio, motion intensity)
- Reference image support
- Advanced controls (temperature, seed, negative prompts)

### Movie Maker (Advanced Feature)
- AI-powered script generation from basic concepts
- Multi-scene movie creation with frame-to-frame continuity
- Automatic scene breakdown into 8-second optimized clips
- Style consistency across all movie clips
- Budget management and cost estimation

### Platform Features
- User authentication and account management
- Real-time generation progress tracking
- Video gallery and library management
- API access for developers
- Comprehensive monitoring and analytics

## 🏗 System Architecture

### Frontend (React)
- **Location**: `/frontend/`
- **Technology**: React 18 + TypeScript + Tailwind CSS
- **Key Components**:
  - Video generation interface
  - Movie maker workflow
  - User dashboard and gallery
  - Settings and account management

### Backend (FastAPI)
- **Location**: `/backend/`
- **Technology**: Python 3.11+ with FastAPI
- **Key Services**:
  - Video generation API
  - Movie script generation
  - User management
  - File handling and storage

### Database
- **Technology**: PostgreSQL 15+ with Redis caching
- **Schema**: User accounts, video metadata, generation history
- **Location**: `/database/`

### Infrastructure
- **Containerization**: Docker with docker-compose
- **Monitoring**: Prometheus + Grafana + Alertmanager
- **Logging**: Structured logging with ELK stack integration
- **Deployment**: Multi-environment support (dev/staging/prod)

## 🎨 Visual Styles

VeoGen supports 9+ distinct visual styles:

1. **🎨 Anime** - Japanese animation aesthetic with vibrant colors
2. **🎭 Pixar** - 3D animated movie style with character focus
3. **🎪 Wes Anderson** - Symmetrical, pastel-colored, quirky cinematography
4. **🏺 Claymation** - Stop-motion clay animation texture
5. **🎪 Švankmajer** - Surreal, dark stop-motion style
6. **📺 Advertisement** - Clean, commercial-style presentation
7. **🎵 Music Video** - Dynamic, rhythm-focused cinematography
8. **🎬 Cinematic** - Hollywood blockbuster production value
9. **📰 Documentary** - Realistic, informational presentation

## 🎬 Movie Presets

Pre-configured movie types with optimized settings:

- **🎬 Short Film**: 5-10 clips (40-80 seconds, $0.50-2.50)
- **📺 Commercial**: 3-5 clips (24-40 seconds, $0.30-1.25)
- **🎵 Music Video**: 8-15 clips (64-120 seconds, $0.80-3.75)
- **🎭 Feature**: 20-50 clips (160-400 seconds, $2.00-12.50)
- **📖 Story**: 10-20 clips (80-160 seconds, $1.00-5.00)

## 💰 Pricing Model

### Free Tier
- 3 videos per month (up to 8 seconds each)
- Basic styles only
- Standard quality (720p)
- VeoGen watermark

### Pro Tier ($19.99/month)
- 50 videos per month
- All styles and presets
- High quality (1080p)
- No watermark
- Movie Maker access (up to 10 clips)

### Studio Tier ($49.99/month)
- 200 videos per month
- Ultra quality (4K when available)
- Movie Maker unlimited clips
- API access
- Priority support

## 🔧 Technical Implementation

### Google Veo 3 Integration
- **Service**: `/backend/app/services/gemini_service.py`
- **CLI Tool**: `/backend/app/services/gemini_cli.py`
- **Authentication**: Vertex AI credentials
- **Rate Limiting**: Built-in quota management

### Movie Continuity System
- **Frame Extraction**: FFmpeg-based frame extraction from video clips
- **Style Transfer**: Consistent visual style application
- **Seamless Transitions**: Minimal visual discontinuity between scenes
- **Quality Control**: Automated transition quality assessment

### Video Processing Pipeline
1. **Prompt Processing**: Text optimization for Veo 3
2. **Generation Request**: API call to Google Vertex AI
3. **Progress Tracking**: Real-time status updates
4. **Quality Check**: Automated quality assessment
5. **Storage**: Secure file storage and metadata
6. **Delivery**: Optimized video delivery to user

## 📊 Monitoring & Analytics

### Grafana Dashboards
- **VeoGen Overview**: Key metrics and system health
- **Video Analytics**: Generation statistics and user behavior
- **Infrastructure**: Server performance and resource usage
- **Error Analysis**: Error tracking and debugging

### Prometheus Metrics
- Video generation success rates
- Average generation times
- User activity metrics
- System performance indicators

### Alerting
- Failed generation alerts
- High error rate notifications
- System resource warnings
- User quota notifications

## 🚀 Development Workflow

### Getting Started
```bash
# Clone repository
git clone https://github.com/veogen/veogen.git
cd veogen

# Start development environment
docker-compose up -d

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Grafana: http://localhost:3001
```

### Key Commands
```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development
cd frontend
npm install
npm start

# Database setup
cd database
psql -U postgres -f init.sql
```

### Testing
```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up
```

## 📚 Documentation Structure

### Core Documentation
- [Product Requirements Document (PRD)](../../docs/PRD.md)
- [System Architecture](../../docs/architecture/system-architecture.md)
- [API Documentation](../../docs/components/backend-api.md)
- [Deployment Guide](../../docs/deployment/docker-architecture.md)

### Development Guides
- [Frontend Build Issues](../../docs/FRONTEND_BUILD_ISSUES.md)
- [Media Generation Integration](../../docs/MEDIA_GENERATION_INTEGRATION.md)
- [Monitoring Setup](../../docs/monitoring/logging-architecture.md)

### User Documentation
- [Quick Start Guide](user-guides/getting-started.md)
- [Movie Maker Tutorial](user-guides/movie-maker.md)
- [Visual Styles Guide](user-guides/visual-styles.md)
- [API Reference](api/README.md)

## 🎯 Current Status & Roadmap

### Phase 1: Foundation ✅ (Completed)
- Core video generation functionality
- Basic UI with responsive design
- Docker containerization
- API documentation and testing

### Phase 2: Movie Maker 🔄 (In Progress)
- Script generation engine
- Continuity system with FFmpeg
- Movie styles and presets
- Enhanced UI with movie workflow

### Phase 3: Polish & Scale 📋 (Planned)
- Advanced analytics and monitoring
- Multi-language support
- Performance optimizations
- Mobile app development

### Phase 4: Advanced Features 📋 (Future)
- Voice narration integration
- Music and sound effects
- Collaborative editing features
- Enterprise features and APIs

## 🔗 Related Resources

### Internal Documentation
- [Veo 3 Technical Guide](../../Artificial_Intelligence/image_and_video/veo_3.md)
- [AI Video Generation Best Practices](../../Artificial_Intelligence/video_generation_best_practices.md)
- [FFmpeg Integration Guide](technical/ffmpeg-integration.md)

### External Links
- [Google Veo 3 Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)

## 👥 Team & Contacts

### Development Team
- **Product Owner**: [Name]
- **Lead Developer**: [Name]
- **Frontend Developer**: [Name]
- **Backend Developer**: [Name]
- **DevOps Engineer**: [Name]

### Key Stakeholders
- **Business**: Product strategy and market requirements
- **Engineering**: Technical implementation and architecture
- **Design**: User experience and interface design
- **Marketing**: Go-to-market and user acquisition

---

*Last Updated: December 2024*  
*Next Review: January 2025*
