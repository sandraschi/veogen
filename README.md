# VeoGen - AI Video Generator with Complete Monitoring Stack

VeoGen is a comprehensive AI-powered video generation platform with full observability, monitoring, and alerting capabilities built on Google's Veo AI technology.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM recommended
- 50GB+ free disk space

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd veogen

# Start the complete stack
./setup.sh       # Linux/Mac
# or
setup.bat        # Windows
```

## 📊 Monitoring Stack Overview

VeoGen includes a complete observability stack:

### Core Application
- **Frontend**: React-based UI (Port 3000)
- **Backend**: FastAPI Python service (Port 8000)
- **Database**: PostgreSQL with monitoring
- **Cache**: Redis with metrics

### Monitoring & Observability
- **Grafana**: Dashboards and visualization (Port 3001)
- **Prometheus**: Metrics collection and alerting (Port 9090)
- **Loki**: Log aggregation and analysis (Port 3100)
- **Promtail**: Log shipping agent
- **Alertmanager**: Alert routing and notifications (Port 9093)
- **Node Exporter**: System metrics (Port 9100)
- **cAdvisor**: Container metrics (Port 8080)

## 📈 Dashboards & Analytics

### Available Dashboards
1. **System Overview** (`/d/veogen-overview`)
   - Service health status
   - System performance metrics
   - Active job counts
   - Real-time status indicators

2. **Video Analytics** (`/d/veogen-video`)
   - Video generation success rates
   - Performance by style
   - Duration analytics
   - Queue monitoring

3. **Infrastructure Monitoring** (`/d/veogen-infrastructure`)
   - CPU and memory usage
   - Container resource consumption
   - Disk space monitoring
   - Network metrics

4. **Error Analysis** (`/d/veogen-errors`)
   - Error rates by component
   - Real-time error logs
   - Error categorization
   - Debugging insights

### Key Metrics Tracked
- **Video Generation**: Success rate, duration, queue size, active jobs
- **Movie Projects**: Project completion, scene generation, style performance
- **System Health**: CPU, memory, disk usage, network I/O
- **Application Performance**: Request latency, error rates, throughput
- **FFmpeg Operations**: Processing time, failure rates, resource usage
- **API Usage**: Gemini API calls, token consumption, response times

## 🔔 Alerting

### Configured Alerts
- **Critical**: Service downtime, high failure rates
- **Warning**: Performance degradation, resource constraints
- **Info**: High usage patterns, maintenance notices

### Alert Channels
- **Email**: Critical and warning alerts
- **Slack**: Real-time notifications (configure webhook)
- **Webhook**: Custom integrations with VeoGen backend

### Alert Rules
- Service health monitoring
- Resource utilization thresholds
- Error rate monitoring
- Performance degradation detection
- Storage usage alerts

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│    Frontend     │───▶│     Backend     │───▶│   Google Veo    │
│   (React)       │    │   (FastAPI)     │    │      API        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │
│    Grafana      │    │   Prometheus    │
│  (Dashboards)   │◀───│   (Metrics)     │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │
│      Loki       │    │  Alertmanager   │
│    (Logs)       │    │   (Alerts)      │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with your configuration:

```bash
# Google Cloud & API Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_API_KEY=your-google-api-key
GEMINI_API_KEY=your-gemini-api-key

# Database Configuration
DATABASE_URL=postgresql://veogen:veogen123@postgres:5432/veogen

# Redis Configuration  
REDIS_URL=redis://:veogen123@redis:6379

# Application Settings
DEBUG=false
MAX_CONCURRENT_GENERATIONS=5
MAX_QUEUE_SIZE=50
GENERATION_TIMEOUT=3600

# Monitoring Settings
GRAFANA_ADMIN_PASSWORD=veogen123
ALERTMANAGER_WEBHOOK_TOKEN=your-webhook-token
```

### Grafana Setup
1. Access Grafana at http://localhost:3001
2. Login with `admin` / `veogen123`
3. Dashboards are automatically provisioned
4. Data sources are pre-configured

### Alert Configuration
1. Update `monitoring/alertmanager.yml` with your notification preferences
2. Configure Slack webhooks for real-time notifications
3. Set up email SMTP settings for critical alerts

## 📝 Logging

### Structured Logging
VeoGen uses structured JSON logging for better analysis:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "video-generation",
  "message": "Video generation completed",
  "job_id": "job_123",
  "style": "cinematic",
  "duration": 45.2,
  "status": "completed"
}
```

### Log Categories
- **Application Logs**: General application events
- **Video Generation**: Video processing specific logs
- **Movie Maker**: Movie project logs
- **FFmpeg**: Video processing operation logs
- **Error Logs**: Centralized error tracking

## 🚨 Troubleshooting

### Common Issues

**Services won't start**
```bash
# Check Docker status
docker ps
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]
```

**High resource usage**
- Monitor with `docker stats`
- Check Grafana infrastructure dashboard
- Adjust resource limits in docker-compose.yml

**Missing metrics**
- Verify Prometheus targets: http://localhost:9090/targets
- Check Grafana data source configuration
- Restart Prometheus: `docker-compose restart prometheus`

**Logs not appearing**
- Check Promtail status: `docker-compose logs promtail`
- Verify Loki connectivity: http://localhost:3100/ready
- Check log file permissions in backend/logs/

### Performance Optimization

**For High Load**
- Increase `MAX_CONCURRENT_GENERATIONS`
- Scale backend service: `docker-compose up --scale backend=3`
- Add Redis cluster for better caching
- Use external PostgreSQL for better performance

**For Resource Constraints**
- Disable unnecessary dashboards
- Reduce metric retention periods
- Limit log retention in Loki
- Use sampling for high-frequency metrics

## 📚 API Documentation

### Core Endpoints
- `GET /`: API information
- `GET /health`: Health check
- `GET /metrics`: Prometheus metrics
- `POST /api/v1/video/generate`: Generate single video
- `POST /api/v1/movie/create`: Create movie project

### Monitoring Endpoints
- `GET /api/v1/metrics`: Application metrics
- `GET /api/v1/health/detailed`: Detailed health status
- `POST /api/v1/alerts/webhook`: Alert webhook receiver

Full API documentation: http://localhost:8000/docs

## 🔐 Security

### Default Credentials
- **Grafana**: admin / veogen123
- **Database**: veogen / veogen123
- **Redis**: veogen123

**⚠️ Change all default passwords in production!**

### Security Features
- JWT token authentication (configure in .env)
- CORS protection
- Rate limiting (configure per endpoint)
- SSL/TLS support (certificate generation included)
- Docker security best practices

## 🔄 Maintenance

### Regular Tasks
```bash
# Update all services
docker-compose pull
docker-compose up -d

# Clean up old containers and images
docker system prune -f

# Backup database
docker-compose exec postgres pg_dump -U veogen veogen > backup.sql

# View logs
docker-compose logs -f --tail=100
```

### Monitoring Maintenance
```bash
# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload

# Clear Grafana cache
docker-compose restart grafana

# Rotate logs
docker-compose exec backend logrotate /etc/logrotate.conf
```

## 🌟 Features

### Video Generation
- Multiple AI styles (cinematic, realistic, animated, artistic)
- Real-time progress tracking
- Queue management
- Automatic retry on failures
- Comprehensive metrics and logging

### Movie Maker
- Multi-scene movie creation
- Style consistency across scenes
- Project management
- Progress tracking per scene
- Advanced timeline features

### Monitoring & Observability
- Real-time dashboards
- Proactive alerting
- Comprehensive logging
- Performance analytics
- Error tracking and debugging
- Resource utilization monitoring

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and monitoring for new features
5. Submit a pull request

### Adding New Metrics
```python
from app.middleware.metrics import track_custom_metric

# In your service
track_custom_metric('operation_type', 'status', duration=123.45)
```

### Adding New Dashboards
1. Create dashboard JSON in `monitoring/grafana/dashboard-configs/`
2. Restart Grafana: `docker-compose restart grafana`
3. Dashboard will be automatically imported

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: /docs folder
- **API Docs**: http://localhost:8000/docs
- **Monitoring**: http://localhost:3001

---

**VeoGen** - AI Video Generation with Enterprise-Grade Monitoring
