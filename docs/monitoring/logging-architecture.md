# VeoGen Monitoring Architecture Documentation (Continued)

### **Structured Logging Implementation (Continued)**

```python
def log_user_action(
    logger: logging.Logger,
    action: str,
    user_id: str,
    **kwargs
):
    """Log user actions with consistent structure"""
    logger.info(f"User action: {action}", extra={
        'event_type': 'user_action',
        'action': action,
        'user_id': user_id,
        **kwargs
    })

def log_error_with_context(
    logger: logging.Logger,
    error: Exception,
    context: Dict[str, Any] = None
):
    """Log errors with full context"""
    logger.error(f"Error occurred: {str(error)}", extra={
        'event_type': 'error',
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context or {},
    }, exc_info=True)

# Context manager for request tracking
from contextvars import ContextVar
import uuid

request_id_var: ContextVar[str] = ContextVar('request_id')
user_id_var: ContextVar[str] = ContextVar('user_id')
trace_id_var: ContextVar[str] = ContextVar('trace_id')

class RequestContext:
    """Context manager for request tracking"""
    
    def __init__(self, request_id: str = None, user_id: str = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.trace_id = str(uuid.uuid4())
    
    def __enter__(self):
        request_id_var.set(self.request_id)
        trace_id_var.set(self.trace_id)
        if self.user_id:
            user_id_var.set(self.user_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Context automatically cleared when exiting
        pass

# Usage in FastAPI middleware
from fastapi import Request

async def logging_middleware(request: Request, call_next):
    """Middleware to add request context to logs"""
    request_id = str(uuid.uuid4())
    user_id = getattr(request.state, 'user_id', None)
    
    with RequestContext(request_id, user_id):
        logger = logging.getLogger(__name__)
        
        # Log request start
        logger.info("Request started", extra={
            'event_type': 'request_start',
            'method': request.method,
            'url': str(request.url),
            'user_agent': request.headers.get('user-agent'),
            'ip_address': request.client.host if request.client else None
        })
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log request completion
            duration = time.time() - start_time
            logger.info("Request completed", extra={
                'event_type': 'request_end',
                'status_code': response.status_code,
                'duration': duration
            })
            
            return response
            
        except Exception as e:
            # Log request error
            duration = time.time() - start_time
            logger.error("Request failed", extra={
                'event_type': 'request_error',
                'error': str(e),
                'duration': duration
            }, exc_info=True)
            raise
```

---

## 🚨 **Alerting System (Alertmanager)**

### **Alertmanager Configuration**

```yaml
# monitoring/alertmanager.yml
global:
  # SMTP settings for email alerts
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'veogen-alerts@yourdomain.com'
  smtp_auth_username: 'veogen-alerts@yourdomain.com'
  smtp_auth_password: 'your-app-password'
  smtp_require_tls: true
  
  # Slack settings
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

# Templates for notifications
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Route tree for alert routing
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s      # Wait time before sending initial notification
  group_interval: 5m   # Wait time before sending updates for the same group
  repeat_interval: 12h # Wait time before resending the same alert
  receiver: 'default-receiver'
  
  routes:
    # Critical alerts - immediate notification
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 0s
      repeat_interval: 5m
      routes:
        - match:
            service: 'veogen-backend'
          receiver: 'backend-critical'
        - match:
            service: 'database'
          receiver: 'database-critical'
    
    # Warning alerts - standard notification
    - match:
        severity: warning
      receiver: 'warning-alerts'
      repeat_interval: 1h
    
    # Info alerts - low priority
    - match:
        severity: info
      receiver: 'info-alerts'
      repeat_interval: 4h
    
    # Business alerts - special handling
    - match:
        type: business
      receiver: 'business-alerts'
      repeat_interval: 30m

# Receivers define how to send notifications
receivers:
  - name: 'default-receiver'
    webhook_configs:
      - url: 'http://backend:8000/api/v1/alerts/webhook'
        send_resolved: true
        http_config:
          bearer_token: 'your-webhook-token'
        title: 'VeoGen Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@yourdomain.com'
        subject: '🚨 CRITICAL: VeoGen Alert - {{ .GroupLabels.alertname }}'
        html: |
          <h2>🚨 Critical Alert</h2>
          <table>
            <tr><th>Alert</th><th>Severity</th><th>Started</th><th>Description</th></tr>
            {{ range .Alerts }}
            <tr>
              <td>{{ .Annotations.summary }}</td>
              <td>{{ .Labels.severity }}</td>
              <td>{{ .StartsAt }}</td>
              <td>{{ .Annotations.description }}</td>
            </tr>
            {{ end }}
          </table>
          <p><a href="http://localhost:3001">View Grafana Dashboard</a></p>
    
    slack_configs:
      - api_url: '{{ .GlobalSlackAPIURL }}'
        channel: '#veogen-critical'
        title: '🚨 Critical VeoGen Alert'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Annotations.summary }}
          *Severity:* {{ .Labels.severity }}
          *Service:* {{ .Labels.service }}
          *Started:* {{ .StartsAt }}
          *Description:* {{ .Annotations.description }}
          {{ end }}
        color: 'danger'
        actions:
          - type: button
            text: 'View Dashboard'
            url: 'http://localhost:3001'
          - type: button
            text: 'View Logs'
            url: 'http://localhost:3001/explore'

  - name: 'backend-critical'
    email_configs:
      - to: 'backend-team@yourdomain.com'
        subject: '🚨 Backend Critical Alert - {{ .GroupLabels.alertname }}'
        body: |
          Backend service critical alert:
          
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Service: {{ .Labels.service }}
          Instance: {{ .Labels.instance }}
          Started: {{ .StartsAt }}
          Description: {{ .Annotations.description }}
          {{ end }}
          
          Immediate action required!
    
    webhook_configs:
      - url: 'http://backend:8000/api/v1/alerts/backend-critical'
        send_resolved: true

  - name: 'database-critical'
    email_configs:
      - to: 'dba-team@yourdomain.com'
        subject: '🚨 Database Critical Alert - {{ .GroupLabels.alertname }}'
        body: |
          Database critical alert:
          
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Database: {{ .Labels.job }}
          Instance: {{ .Labels.instance }}
          Started: {{ .StartsAt }}
          Description: {{ .Annotations.description }}
          {{ end }}

  - name: 'warning-alerts'
    email_configs:
      - to: 'team@yourdomain.com'
        subject: '⚠️ Warning: VeoGen Alert - {{ .GroupLabels.alertname }}'
        body: |
          Warning alert from VeoGen:
          
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Severity: {{ .Labels.severity }}
          Service: {{ .Labels.service }}
          Started: {{ .StartsAt }}
          Description: {{ .Annotations.description }}
          {{ end }}
    
    slack_configs:
      - channel: '#veogen-warnings'
        title: '⚠️ VeoGen Warning'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Annotations.summary }}
          *Service:* {{ .Labels.service }}
          *Description:* {{ .Annotations.description }}
          {{ end }}
        color: 'warning'

  - name: 'info-alerts'
    slack_configs:
      - channel: '#veogen-info'
        title: 'ℹ️ VeoGen Info'
        text: |
          {{ range .Alerts }}
          {{ .Annotations.summary }}
          {{ end }}
        color: 'good'

  - name: 'business-alerts'
    email_configs:
      - to: 'business-team@yourdomain.com'
        subject: '📊 Business Alert: {{ .GroupLabels.alertname }}'
        body: |
          Business metric alert:
          
          {{ range .Alerts }}
          Metric: {{ .Annotations.summary }}
          Value: {{ .Annotations.value }}
          Threshold: {{ .Annotations.threshold }}
          Started: {{ .StartsAt }}
          {{ end }}

# Inhibition rules - suppress alerts based on other active alerts
inhibit_rules:
  # If service is down, don't alert on high response times
  - source_match:
      severity: 'critical'
      alertname: 'VeoGenServiceDown'
    target_match:
      severity: 'warning'
    equal: ['service', 'instance']
  
  # If database is down, don't alert on connection errors
  - source_match:
      severity: 'critical'
      alertname: 'DatabaseDown'
    target_match:
      alertname: 'DatabaseConnectionErrors'
    equal: ['instance']
  
  # During maintenance windows
  - source_match:
      alertname: 'MaintenanceMode'
    target_match_re:
      alertname: '.*'
    equal: ['service']

# Mute specific alerts during maintenance
mute_time_intervals:
  - name: 'maintenance-window'
    time_intervals:
      - times:
          - start_time: '02:00'
            end_time: '04:00'
        days_of_month: ['1']  # First day of each month
        location: 'UTC'
```

### **Comprehensive Alert Rules**

```yaml
# monitoring/rules/veogen_alerts.yml
groups:
  - name: veogen_system_alerts
    interval: 30s
    rules:
      - alert: VeoGenServiceDown
        expr: up{job=~"veogen-.*"} == 0
        for: 1m
        labels:
          severity: critical
          service: "{{ $labels.job }}"
          team: infrastructure
        annotations:
          summary: "VeoGen service {{ $labels.job }} is down"
          description: |
            Service {{ $labels.job }} on instance {{ $labels.instance }} 
            has been down for more than 1 minute.
            Impact: Service unavailable to users.
          runbook_url: "https://wiki.company.com/runbooks/service-down"
          dashboard_url: "http://localhost:3001/d/veogen-overview"
          
      - alert: HighCPUUsage
        expr: |
          100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "High CPU usage detected on {{ $labels.instance }}"
          description: |
            CPU usage is {{ $value }}% on {{ $labels.instance }} for more than 5 minutes.
            This may impact application performance.
          
      - alert: HighMemoryUsage
        expr: |
          (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "High memory usage detected on {{ $labels.instance }}"
          description: |
            Memory usage is {{ $value }}% on {{ $labels.instance }} for more than 5 minutes.
            Available memory: {{ query "node_memory_MemAvailable_bytes{instance=\"$labels.instance\"}" | first | value | humanize }}B
          
      - alert: DiskSpaceRunningLow
        expr: |
          (node_filesystem_size_bytes{fstype!="tmpfs"} - node_filesystem_free_bytes{fstype!="tmpfs"}) / node_filesystem_size_bytes{fstype!="tmpfs"} * 100 > 85
        for: 10m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "Disk space running low on {{ $labels.mountpoint }}"
          description: |
            Disk usage is {{ $value }}% on {{ $labels.mountpoint }} ({{ $labels.instance }}).
            Free space: {{ query "node_filesystem_free_bytes{instance=\"$labels.instance\",mountpoint=\"$labels.mountpoint\"}" | first | value | humanize }}B
          
      - alert: DiskSpaceCritical
        expr: |
          (node_filesystem_size_bytes{fstype!="tmpfs"} - node_filesystem_free_bytes{fstype!="tmpfs"}) / node_filesystem_size_bytes{fstype!="tmpfs"} * 100 > 95
        for: 5m
        labels:
          severity: critical
          team: infrastructure
        annotations:
          summary: "Critical disk space on {{ $labels.mountpoint }}"
          description: |
            Disk usage is {{ $value }}% on {{ $labels.mountpoint }} ({{ $labels.instance }}).
            System may become unstable. Immediate action required.

  - name: veogen_application_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          rate(veogen_http_requests_total{status=~"5.."}[5m]) / rate(veogen_http_requests_total[5m]) * 100 > 5
        for: 2m
        labels:
          severity: warning
          service: "{{ $labels.job }}"
          team: backend
        annotations:
          summary: "High error rate detected on {{ $labels.endpoint }}"
          description: |
            Error rate is {{ $value }}% for endpoint {{ $labels.endpoint }}.
            This indicates potential issues with the application.
          
      - alert: CriticalErrorRate
        expr: |
          rate(veogen_http_requests_total{status=~"5.."}[5m]) / rate(veogen_http_requests_total[5m]) * 100 > 20
        for: 1m
        labels:
          severity: critical
          service: "{{ $labels.job }}"
          team: backend
        annotations:
          summary: "Critical error rate on {{ $labels.endpoint }}"
          description: |
            Error rate is {{ $value }}% for endpoint {{ $labels.endpoint }}.
            Service is severely degraded. Immediate attention required.
          
      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.95, rate(veogen_http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
          service: api
          team: backend
        annotations:
          summary: "Slow API response times"
          description: |
            95th percentile response time is {{ $value }}s for {{ $labels.endpoint }}.
            Users may experience slow performance.
          
      - alert: SlowVideoGeneration
        expr: |
          histogram_quantile(0.95, rate(veogen_video_generation_duration_seconds_bucket[10m])) > 1800
        for: 5m
        labels:
          severity: warning
          service: video-generation
          team: ai-services
        annotations:
          summary: "Video generation is taking too long"
          description: |
            95th percentile generation time is {{ $value }} seconds.
            Users may experience delayed video generation.
          
      - alert: VideoGenerationFailureRate
        expr: |
          rate(veogen_video_generations_total{status="failed"}[10m]) / rate(veogen_video_generations_total[10m]) * 100 > 10
        for: 5m
        labels:
          severity: critical
          service: video-generation
          team: ai-services
        annotations:
          summary: "High video generation failure rate"
          description: |
            Video generation failure rate is {{ $value }}%.
            This may indicate issues with AI services or infrastructure.
          
      - alert: LargeVideoQueue
        expr: veogen_video_queue_size > 50
        for: 5m
        labels:
          severity: warning
          service: video-generation
          team: ai-services
        annotations:
          summary: "Large video generation queue"
          description: |
            Video queue size is {{ $value }} jobs.
            Consider scaling up processing capacity.

  - name: veogen_database_alerts
    interval: 30s
    rules:
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
          service: database
          team: infrastructure
        annotations:
          summary: "PostgreSQL database is down"
          description: |
            PostgreSQL database is not responding.
            All application functions will be impacted.
          
      - alert: DatabaseConnectionsHigh
        expr: |
          pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
          service: database
          team: backend
        annotations:
          summary: "High number of database connections"
          description: |
            Database has {{ $value }} active connections.
            This may indicate connection leaks or high load.
          
      - alert: DatabaseSlowQueries
        expr: |
          rate(pg_stat_statements_mean_time_ms[5m]) > 1000
        for: 5m
        labels:
          severity: warning
          service: database
          team: backend
        annotations:
          summary: "Slow database queries detected"
          description: |
            Average query time is {{ $value }}ms.
            This may impact application performance.

  - name: veogen_business_alerts
    interval: 60s
    rules:
      - alert: LowVideoGenerationRate
        expr: |
          rate(veogen_video_generations_total{status="completed"}[1h]) < 5
        for: 10m
        labels:
          severity: info
          type: business
          team: product
        annotations:
          summary: "Low video generation rate"
          description: |
            Only {{ $value }} videos generated per hour.
            This may indicate low user engagement or technical issues.
          
      - alert: HighVideoFailureRate
        expr: |
          rate(veogen_video_generations_total{status="failed"}[1h]) / rate(veogen_video_generations_total[1h]) * 100 > 5
        for: 15m
        labels:
          severity: warning
          type: business
          team: ai-services
        annotations:
          summary: "High business impact from video failures"
          description: |
            {{ $value }}% of video generations are failing.
            This directly impacts user experience and revenue.
          
      - alert: UnusualUserActivity
        expr: |
          increase(veogen_user_activity_total[1h]) > 1000 or increase(veogen_user_activity_total[1h]) < 10
        for: 30m
        labels:
          severity: info
          type: business
          team: product
        annotations:
          summary: "Unusual user activity detected"
          description: |
            User activity is {{ $value }} events in the last hour.
            This may indicate unusual traffic patterns.

  - name: veogen_security_alerts
    interval: 30s
    rules:
      - alert: HighFailedLoginAttempts
        expr: |
          rate(veogen_user_activity_total{action="failed_login"}[5m]) * 300 > 10
        for: 2m
        labels:
          severity: warning
          team: security
        annotations:
          summary: "High number of failed login attempts"
          description: |
            {{ $value }} failed login attempts in the last 5 minutes.
            This may indicate a brute force attack.
          
      - alert: UnauthorizedAPIAccess
        expr: |
          rate(veogen_http_requests_total{status="401"}[5m]) * 300 > 20
        for: 5m
        labels:
          severity: warning
          team: security
        annotations:
          summary: "High number of unauthorized API requests"
          description: |
            {{ $value }} unauthorized requests in the last 5 minutes.
            This may indicate an API attack or misconfigured clients.
```

---

## 📊 **Grafana Dashboard Configuration**

### **Dashboard Provisioning**

```yaml
# monitoring/grafana/dashboards/dashboards.yml
apiVersion: 1

providers:
  - name: 'VeoGen Dashboards'
    orgId: 1
    folder: 'VeoGen'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards

  - name: 'Infrastructure Dashboards'
    orgId: 1
    folder: 'Infrastructure'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards/infrastructure

  - name: 'Business Dashboards'
    orgId: 1
    folder: 'Business'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards/business
```

### **Data Source Configuration**

```yaml
# monitoring/grafana/datasources/datasources.yml
apiVersion: 1

deleteDatasources:
  - name: Loki
    orgId: 1
  - name: Prometheus
    orgId: 1

datasources:
  # Primary Loki instance for logs
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
    version: 1
    editable: true
    jsonData:
      maxLines: 1000
      derivedFields:
        - datasourceUid: prometheus
          matcherRegex: "job_id=([^\\s]+)"
          name: JobID
          url: "/d/veogen-jobs/veogen-jobs?var-job_id=${__value.raw}"
        - datasourceUid: prometheus
          matcherRegex: "request_id=([^\\s]+)"
          name: RequestID
          url: "/d/veogen-requests/veogen-requests?var-request_id=${__value.raw}"
        - datasourceUid: prometheus
          matcherRegex: "user_id=([^\\s]+)"
          name: UserID
          url: "/d/veogen-users/veogen-users?var-user_id=${__value.raw}"

  # Primary Prometheus instance for metrics
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    version: 1
    editable: true
    uid: prometheus
    jsonData:
      httpMethod: GET
      manageAlerts: true
      prometheusType: Prometheus
      prometheusVersion: 2.40.0
      cacheLevel: 'High'
      disableRecordingRules: false
      incrementalQueryOverlapWindow: 10m
      exemplarTraceIdDestinations:
        - name: trace_id
          datasourceUid: jaeger

  # Specialized log datasource for errors
  - name: VeoGen Error Logs
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
    version: 1
    editable: true
    uid: veogen-error-logs
    jsonData:
      maxLines: 5000
      derivedFields:
        - datasourceUid: prometheus
          matcherRegex: "level=(ERROR|CRITICAL)"
          name: Error Details
          url: "/d/veogen-errors/veogen-errors?var-level=${__value.raw}"

  # Business metrics datasource
  - name: Business Metrics
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: false
    version: 1
    editable: true
    uid: business-metrics
    jsonData:
      httpMethod: GET
      manageAlerts: false
      prometheusType: Prometheus
      exemplarTraceIdDestinations: []

# Test data source connections
testDatasources:
  - name: Prometheus
    url: http://prometheus:9090/api/v1/query?query=up
  - name: Loki
    url: http://loki:3100/ready
```

This comprehensive monitoring architecture provides enterprise-grade observability for VeoGen with:

- **Complete metrics collection** from application, infrastructure, and business layers
- **Structured logging** with automatic correlation and context
- **Intelligent alerting** with multi-channel notifications and escalation
- **Rich visualization** with interactive dashboards and real-time monitoring
- **Operational excellence** through automated monitoring and proactive alerting

The monitoring stack enables teams to maintain high availability, quickly identify and resolve issues, and continuously optimize performance while providing valuable insights into user behavior and business metrics.
