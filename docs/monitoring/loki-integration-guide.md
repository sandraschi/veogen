# Loki Integration Guide for VeoGen

## Overview

VeoGen uses Grafana Loki for centralized log aggregation and monitoring. Loki is a log aggregation system designed to be highly available and horizontally scalable, making it ideal for our distributed microservices architecture.

## Architecture

### Current Setup
- **Loki Version**: Latest stable (v2.9.x)
- **Storage**: Local filesystem with boltdb-shipper
- **Retention**: 30 days
- **Scraping**: Promtail agents on each service
- **Query Interface**: Grafana dashboards

### Components
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │   Database  │
│  (Promtail) │    │  (Promtail) │    │  (Promtail) │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                   ┌──────▼──────┐
                   │    Loki     │
                   │ (Aggregator)│
                   └──────┬──────┘
                          │
                   ┌──────▼──────┐
                   │   Grafana   │
                   │ (Dashboard) │
                   └─────────────┘
```

## VeoGen-Specific Experiences

### Current Status: Unstable Implementation
Despite following best practices and official documentation, our Loki implementation in VeoGen has proven to be consistently unstable. We have experienced:

- **Frequent crashes** (2-3 times per day)
- **Data corruption** requiring manual intervention
- **Performance degradation** over time
- **Resource exhaustion** despite adequate allocation
- **Intermittent connectivity** issues between services

### Our Implementation Attempts

#### Attempt 1: Basic Setup (Failed)
- Used default Loki configuration
- Crashed within hours due to memory issues
- No persistent storage configuration

#### Attempt 2: Resource-Limited Setup (Failed)
- Added memory limits (2GB)
- Implemented proper storage configuration
- Still experienced crashes and data corruption

#### Attempt 3: Production-Ready Setup (Failed)
- Full configuration with boltdb-shipper
- Proper networking and health checks
- Monitoring and alerting
- **Result**: Still unstable, requiring daily restarts

### Root Cause Analysis
After extensive troubleshooting, we believe the instability stems from:

1. **Docker Desktop Limitations**: Windows Docker Desktop has known issues with volume mounting and filesystem performance
2. **Resource Contention**: Loki competes with other services for limited system resources
3. **Filesystem Issues**: Windows filesystem performance with large log volumes
4. **Configuration Complexity**: Loki's configuration is complex and sensitive to environment differences

### Current Mitigation Strategy
We have implemented a "restart-on-failure" approach:
- Automatic container restart policies
- Daily scheduled restarts
- Backup and recovery procedures
- Monitoring to detect failures quickly

**Note**: This is not an ideal solution, but it keeps the system functional while we explore alternatives.

## Known Issues and Crashes

### 1. Memory Exhaustion
**Symptoms:**
- Loki container crashes with OOM errors
- High memory usage in monitoring stack
- Slow query performance

**Root Causes:**
- Large log volumes overwhelming memory limits
- Inefficient query patterns
- Insufficient memory allocation

**Mitigation Strategies:**
```yaml
# docker-compose.yml - Loki service
services:
  loki:
    image: grafana/loki:latest
    environment:
      - LOKI_CONFIG=/etc/loki/local-config.yaml
    volumes:
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    restart: unless-stopped
```

### 2. Storage Corruption
**Symptoms:**
- Loki fails to start after container restart
- Data directory corruption errors
- Missing log data

**Root Causes:**
- Improper shutdown procedures
- Filesystem issues
- Concurrent write conflicts

**Mitigation Strategies:**
```yaml
# loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    cache_ttl: 24h
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

compactor:
  working_directory: /loki/compactor
  shared_store: filesystem

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  max_cache_freshness_per_query: 10m
  split_queries_by_interval: 15m

query_range:
  align_queries_with_step: true
  max_retries: 5
  cache_results: true
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

frontend:
  compress_responses: true
  log_queries_longer_than: 5s
  downstream_url: http://localhost:3100
```

### 3. Network Connectivity Issues
**Symptoms:**
- Promtail agents unable to reach Loki
- Log ingestion failures
- Timeout errors

**Root Causes:**
- Docker network configuration issues
- Firewall rules blocking communication
- DNS resolution problems

**Mitigation Strategies:**
```yaml
# docker-compose.yml - Network configuration
networks:
  monitoring:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  loki:
    networks:
      - monitoring
    ports:
      - "3100:3100"
  
  promtail:
    networks:
      - monitoring
    depends_on:
      - loki
```

### 4. Query Performance Issues
**Symptoms:**
- Slow dashboard loading
- Query timeouts
- High CPU usage during queries

**Root Causes:**
- Large time ranges in queries
- Inefficient log parsing
- Missing indexes

**Mitigation Strategies:**
```yaml
# loki-config.yml - Performance tuning
limits_config:
  max_query_length: 721h
  max_query_parallelism: 32
  cardinality_limit: 100000
  max_streams_per_user: 0
  max_global_streams_per_user: 0
  ingestion_rate_mb: 32
  ingestion_burst_size_mb: 64

query_range:
  align_queries_with_step: true
  max_retries: 5
  cache_results: true
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100
```

## Monitoring and Alerting

### Health Checks
```yaml
# docker-compose.yml - Health check
services:
  loki:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3100/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Alerting Rules
```yaml
# monitoring/rules/veogen_alerts.yml
groups:
  - name: loki_alerts
    rules:
      - alert: LokiDown
        expr: up{job="loki"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Loki is down"
          description: "Loki has been down for more than 1 minute"

      - alert: LokiHighMemory
        expr: container_memory_usage_bytes{container="loki"} > 1.5e9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Loki high memory usage"
          description: "Loki memory usage is above 1.5GB"

      - alert: LokiHighCPU
        expr: rate(container_cpu_usage_seconds_total{container="loki"}[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Loki high CPU usage"
          description: "Loki CPU usage is above 80%"
```

## Troubleshooting Guide

### Common Commands
```bash
# Check Loki status
curl http://localhost:3100/ready

# Check Loki metrics
curl http://localhost:3100/metrics

# Check Loki configuration
curl http://localhost:3100/config

# Check storage status
curl http://localhost:3100/storage

# Check ring status
curl http://localhost:3100/ring
```

### Log Analysis
```bash
# View Loki logs
docker logs veogen-loki-1

# Check Promtail logs
docker logs veogen-promtail-1

# Check storage directory
ls -la monitoring/loki-data/

# Check for corrupted files
find monitoring/loki-data/ -name "*.db" -exec file {} \;
```

### Recovery Procedures

#### 1. Memory Issues
```bash
# Restart with increased memory
docker-compose down
docker-compose up -d loki

# Check memory usage
docker stats veogen-loki-1
```

#### 2. Storage Corruption
```bash
# Backup current data
cp -r monitoring/loki-data monitoring/loki-data-backup

# Clear corrupted data
rm -rf monitoring/loki-data/boltdb-shipper-cache/*
rm -rf monitoring/loki-data/chunks/*

# Restart Loki
docker-compose restart loki
```

#### 3. Network Issues
```bash
# Check network connectivity
docker exec veogen-promtail-1 curl -f http://loki:3100/ready

# Restart network
docker-compose down
docker network prune
docker-compose up -d
```

## Best Practices

### 1. Resource Allocation
- Allocate sufficient memory (2GB+ for production)
- Use CPU limits to prevent resource exhaustion
- Monitor disk space for log storage

### 2. Configuration
- Use external configuration files
- Implement proper retention policies
- Configure appropriate limits for your workload

### 3. Monitoring
- Set up comprehensive alerting
- Monitor Loki's own metrics
- Track query performance

### 4. Backup and Recovery
- Regular backups of configuration
- Document recovery procedures
- Test recovery processes

## Reference Links

### Official Documentation
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Loki Configuration](https://grafana.com/docs/loki/latest/configuration/)
- [Loki API Reference](https://grafana.com/docs/loki/latest/api/)

### GitHub Repositories
- [Loki Main Repository](https://github.com/grafana/loki)
- [Promtail Repository](https://github.com/grafana/loki/tree/main/clients/cmd/promtail)
- [Loki Helm Charts](https://github.com/grafana/helm-charts)

### Community Resources
- [Loki Community Forum](https://community.grafana.com/c/loki/30)
- [Loki GitHub Issues](https://github.com/grafana/loki/issues)
- [Loki GitHub Discussions](https://github.com/grafana/loki/discussions)

### Common Solutions
- [Loki Troubleshooting Guide](https://grafana.com/docs/loki/latest/operations/troubleshooting/)
- [Loki Performance Tuning](https://grafana.com/docs/loki/latest/operations/storage/)
- [Loki Best Practices](https://grafana.com/docs/loki/latest/best-practices/)

### Related Tools
- [Grafana](https://grafana.com/docs/grafana/latest/)
- [Prometheus](https://prometheus.io/docs/)
- [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/)

## Version History

- **v2.9.x** (Current): Latest stable release with improved performance
- **v2.8.x**: Previous stable release
- **v2.7.x**: Legacy version (not recommended)

## Alternative Solutions Under Consideration

### 1. Simplified Logging
- **Fluentd/Fluent Bit**: Lighter weight log aggregation
- **Filebeat**: Simple log shipping to Elasticsearch
- **Direct file logging**: Bypass aggregation entirely

### 2. Cloud-Based Solutions
- **Grafana Cloud**: Managed Loki service
- **Datadog**: Comprehensive logging and monitoring
- **AWS CloudWatch**: Native AWS logging

### 3. Local Alternatives
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Graylog**: Open-source log management
- **Simple file-based logging**: With log rotation

### 4. Hybrid Approach
- **Development**: Simple file logging
- **Production**: Cloud-based logging service
- **Staging**: Lightweight local solution

## Lessons Learned

### What Didn't Work
- Following official documentation blindly
- Assuming Docker Desktop would handle production workloads
- Complex configurations without proper testing
- Ignoring platform-specific limitations

### What We Should Have Done
- Start with simpler logging solutions
- Test thoroughly on target platform before production
- Consider cloud-based solutions from the beginning
- Implement proper monitoring before adding complexity

### Recommendations for Future Projects
1. **Start Simple**: Begin with basic file logging
2. **Platform Testing**: Test on actual deployment platform
3. **Cloud First**: Consider managed services for production
4. **Incremental Complexity**: Add features gradually
5. **Monitoring First**: Implement monitoring before logging

## Support

For issues specific to our VeoGen implementation:
1. Check this documentation first
2. Review the troubleshooting guide
3. Check official Loki documentation
4. Search GitHub issues for similar problems
5. Contact the development team

**Important**: Our experience suggests that Loki may not be suitable for Windows Docker Desktop environments. Consider alternatives listed above.

For general Loki issues:
1. Check the [Loki Community Forum](https://community.grafana.com/c/loki/30)
2. Search [GitHub Issues](https://github.com/grafana/loki/issues)
3. Review [Stack Overflow](https://stackoverflow.com/questions/tagged/loki) tags 