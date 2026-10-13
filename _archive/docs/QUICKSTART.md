# VeoGen Monitoring Stack - Quick Start Guide

This guide will help you get the complete VeoGen monitoring stack up and running in minutes.

## 🎯 What You'll Get

After following this guide, you'll have:
- ✅ Complete VeoGen application running
- ✅ Real-time monitoring dashboards
- ✅ Automated alerting system
- ✅ Comprehensive logging
- ✅ Performance analytics
- ✅ Error tracking and debugging tools

## 🚀 5-Minute Setup

### Step 1: Prerequisites Check
```bash
# Check Docker is running
docker --version
docker-compose --version

# Ensure you have enough resources
# Minimum: 8GB RAM, 4 CPU cores, 50GB disk space
```

### Step 2: Start the Stack
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat
```

### Step 3: Verify Installation
After startup (2-3 minutes), check these URLs:

| Service | URL | Credentials |
|---------|-----|-------------|
| VeoGen App | http://localhost:3000 | - |
| API Docs | http://localhost:8000/docs | - |
| Grafana | http://localhost:3001 | admin/veogen123 |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |

## 📊 Monitoring Dashboard Tour

### 1. System Overview Dashboard
**URL**: http://localhost:3001/d/veogen-overview

**What you'll see**:
- 🟢 Service health indicators
- 📈 Real-time CPU and memory usage
- 🎬 Active video generations
- 🎭 Movie projects in progress
- ⚡ Performance metrics

**Key metrics**:
- Service uptime status
- System resource utilization
- Active job counts
- Queue sizes

### 2. Video Analytics Dashboard
**URL**: http://localhost:3001/d/veogen-video

**What you'll see**:
- 🎯 Success rates by video style
- ⏱️ Generation duration trends
- 📊 Performance comparisons
- 🔄 Processing queue status

**Key insights**:
- Which video styles perform best
- Average generation times
- Peak usage patterns
- Bottleneck identification

### 3. Infrastructure Dashboard
**URL**: http://localhost:3001/d/veogen-infrastructure

**What you'll see**:
- 🖥️ Host system metrics
- 🐳 Container resource usage
- 💾 Disk space monitoring
- 🌐 Network performance

**Monitor**:
- CPU usage per core
- Memory consumption
- Container health
- Storage utilization

### 4. Error Analysis Dashboard
**URL**: http://localhost:3001/d/veogen-errors

**What you'll see**:
- 🚨 Error rates by component
- 📝 Real-time error logs
- 📈 Error trend analysis
- 🔍 Debugging information

**Debug with**:
- Error categorization
- Component-specific failures
- Timeline correlation
- Log aggregation

## 🔔 Alert Configuration

### Quick Alert Setup

1. **Email Alerts** (5 minutes):
   ```bash
   # Edit alertmanager config
   nano monitoring/alertmanager.yml
   
   # Update SMTP settings
   smtp_smarthost: 'your-smtp-server:587'
   smtp_from: 'alerts@yourcompany.com'
   smtp_auth_username: 'your-email@yourcompany.com'
   smtp_auth_password: 'your-password'
   
   # Update recipient email
   to: 'admin@yourcompany.com'
   
   # Restart alertmanager
   docker-compose restart alertmanager
   ```

2. **Slack Integration** (3 minutes):
   ```bash
   # Get Slack webhook URL from your Slack admin
   # Update monitoring/alertmanager.yml
   api_url: 'YOUR_SLACK_WEBHOOK_URL'
   channel: '#veogen-alerts'
   
   # Restart alertmanager
   docker-compose restart alertmanager
   ```

### Pre-configured Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| Service Down | Service offline > 1min | Critical | Immediate notification |
| High CPU | CPU > 85% for 5min | Warning | Email alert |
| High Memory | Memory > 90% for 5min | Warning | Email alert |
| High Error Rate | Errors > 5% for 2min | Warning | Slack notification |
| Slow Generation | Gen time > 30min | Warning | Team notification |
| Large Queue | Queue > 20 jobs | Warning | Monitoring alert |

## 📈 Metrics Collection

### Automatic Metrics
VeoGen automatically collects:

**Application Metrics**:
- HTTP request rates and latency
- Video generation success/failure rates
- Movie project completion times
- Queue sizes and processing times
- API response times and error rates

**System Metrics**:
- CPU usage per core
- Memory utilization
- Disk I/O and space usage
- Network traffic
- Container resource consumption

**Business Metrics**:
- Videos generated per hour/day
- Popular video styles
- User activity patterns
- Revenue-related metrics (if configured)

### Custom Metrics
Add custom metrics to your code:

```python
from app.middleware.metrics import track_video_generation

# Track video generation
track_video_generation(
    style="cinematic",
    status="completed", 
    duration=45.2
)
```

## 🔍 Log Analysis

### Log Categories
VeoGen organizes logs into categories:

1. **Application Logs**: `/app/logs/app.log`
   - General application events
   - User actions
   - System events

2. **Video Generation**: `/app/logs/video_generation.log`
   - Job start/completion
   - Progress updates
   - Generation errors

3. **Movie Maker**: `/app/logs/movie_maker.log`
   - Project events
   - Scene processing
   - Rendering status

4. **FFmpeg Operations**: `/app/logs/ffmpeg.log`
   - Video processing
   - Format conversions
   - Encoding details

5. **Error Logs**: `/app/logs/error.log`
   - All errors centralized
   - Stack traces
   - Debug information

### Searching Logs in Grafana

1. Go to **Explore** in Grafana
2. Select **Loki** data source
3. Use these queries:

```
# All errors in the last hour
{job="veogen-backend"} |= "ERROR"

# Video generation logs
{job="veogen-backend"} |= "video_generation"

# Specific job tracking
{job="veogen-backend"} |= "job_id=abc123"

# Performance issues
{job="veogen-backend"} |= "slow" or "timeout"
```

## 🎯 Performance Monitoring

### Key Performance Indicators (KPIs)

**Operational KPIs**:
- Service uptime: Target 99.9%
- Average response time: Target <200ms
- Error rate: Target <1%
- Queue processing time: Target <5min

**Business KPIs**:
- Videos generated per day
- Success rate by style
- User satisfaction metrics
- Resource efficiency ratios

### Performance Optimization

**Monitor these metrics**:
1. **Response Time**: Track API endpoint latency
2. **Throughput**: Requests processed per second
3. **Error Rate**: Failed requests percentage
4. **Resource Usage**: CPU, memory, disk utilization
5. **Queue Metrics**: Backlog size and processing rate

**Optimization actions**:
- Scale services based on load
- Optimize slow queries
- Implement caching strategies
- Monitor resource bottlenecks

## 🚨 Troubleshooting Common Issues

### Issue: Services Won't Start
```bash
# Check Docker resources
docker system df
docker system events

# Check logs
docker-compose logs backend
docker-compose logs grafana
```

### Issue: No Metrics in Grafana
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify metrics endpoint
curl http://localhost:8000/metrics

# Restart Prometheus
docker-compose restart prometheus
```

### Issue: Missing Logs
```bash
# Check Promtail status
docker-compose logs promtail

# Verify log files exist
ls -la backend/logs/

# Test Loki connection
curl http://localhost:3100/ready
```

### Issue: Alerts Not Working
```bash
# Check alertmanager config
docker-compose exec alertmanager cat /etc/alertmanager/alertmanager.yml

# Test alert rules
curl http://localhost:9090/api/v1/rules

# Check alert status
curl http://localhost:9093/api/v1/alerts
```

## 🔧 Advanced Configuration

### Scaling for Production

1. **High Availability**:
   ```yaml
   # In docker-compose.yml
   backend:
     deploy:
       replicas: 3
       resources:
         limits:
           cpus: '2.0'
           memory: 4G
   ```

2. **External Databases**:
   ```bash
   # Use managed PostgreSQL and Redis
   DATABASE_URL=postgresql://user:pass@external-db:5432/veogen
   REDIS_URL=redis://external-redis:6379
   ```

3. **Load Balancing**:
   - Configure nginx for load balancing
   - Use external load balancer
   - Implement health checks

### Custom Dashboards

Create custom dashboards for your needs:

1. **Business Dashboard**: Revenue, users, conversions
2. **Operations Dashboard**: Deployments, incidents, SLA
3. **Development Dashboard**: Code metrics, build times
4. **Executive Dashboard**: High-level KPIs, trends

## 📚 Next Steps

### 1. Customize for Your Environment
- Update environment variables in `.env`
- Configure your API keys
- Set up your notification channels
- Customize alert thresholds

### 2. Integrate with Your Systems
- Connect to your CI/CD pipeline
- Integrate with incident management
- Link to your ticketing system
- Connect business metrics

### 3. Advanced Monitoring
- Set up distributed tracing
- Implement user journey tracking
- Monitor business KPIs
- Create custom alerting rules

### 4. Security & Compliance
- Enable authentication
- Implement audit logging
- Set up data retention policies
- Configure backup strategies

## 🎉 You're Ready!

Your VeoGen monitoring stack is now fully operational. You have:

- ✅ Real-time visibility into your application
- ✅ Proactive alerting for issues
- ✅ Comprehensive logging for debugging
- ✅ Performance analytics for optimization
- ✅ Infrastructure monitoring for capacity planning

**Happy monitoring!** 🚀

---

For more detailed information, see the main [README.md](README.md) file.
