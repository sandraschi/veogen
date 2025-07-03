# VeoGen Docker Architecture & Containerization (Continued)

### **Container Security Configuration**

```yaml
# docker-compose.override.yml for security
version: '3.8'

services:
  backend:
    # Security options
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
      - /app/temp:noexec,nosuid,size=1g
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    user: "1001:1001"
    
    # Resource limits for security
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
          pids: 100
        reservations:
          cpus: '1.0'
          memory: 2G
    
    # Environment variable restrictions
    environment:
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
      - PYTHONPATH=/app
    
    # Network restrictions
    networks:
      - veogen-network
    
    # Health and liveness probes
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    # Database security
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
      - /var/run/postgresql:noexec,nosuid,size=100m
    cap_drop:
      - ALL
    cap_add:
      - SETUID
      - SETGID
      - DAC_OVERRIDE
    
    # Secure PostgreSQL configuration
    command: |
      postgres
      -c ssl=on
      -c ssl_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
      -c ssl_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
      -c log_statement=all
      -c log_min_duration_statement=0
      -c shared_preload_libraries=pg_stat_statements
```

### **Container Scanning Configuration**

```yaml
# .github/workflows/security-scan.yml
name: Container Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Backend Image
        run: docker build -t veogen/backend:test ./backend
        
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'veogen/backend:test'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
          
      - name: Run Snyk Container Security Test
        uses: snyk/actions/docker@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          image: veogen/backend:test
          args: --severity-threshold=medium
```

---

## 🚀 **Container Orchestration**

### **Docker Swarm Configuration**

```yaml
# docker-stack.yml for Docker Swarm
version: '3.8'

services:
  backend:
    image: veogen/backend:${VERSION:-latest}
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.role == worker
        preferences:
          - spread: node.labels.zone
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
        order: start-first
      rollback_config:
        parallelism: 1
        delay: 5s
        failure_action: pause
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://veogen:${POSTGRES_PASSWORD}@postgres:5432/veogen
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
    volumes:
      - backend_uploads:/app/uploads
      - backend_outputs:/app/outputs
      - backend_logs:/app/logs
    networks:
      - veogen-overlay
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.database == true
      restart_policy:
        condition: on-failure
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    environment:
      - POSTGRES_DB=veogen
      - POSTGRES_USER=veogen
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - veogen-overlay

networks:
  veogen-overlay:
    driver: overlay
    attachable: true
    ipam:
      config:
        - subnet: 10.0.1.0/24

volumes:
  postgres_data:
    driver: local
  backend_uploads:
    driver: local
  backend_outputs:
    driver: local
  backend_logs:
    driver: local
```

### **Kubernetes Deployment**

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: veogen
  labels:
    name: veogen
    environment: production

---
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: veogen-backend
  namespace: veogen
  labels:
    app: veogen-backend
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: veogen-backend
  template:
    metadata:
      labels:
        app: veogen-backend
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8001"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: veogen-backend
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 1001
        fsGroup: 1001
      containers:
      - name: backend
        image: veogen/backend:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        - containerPort: 8001
          name: metrics
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: veogen-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: veogen-secrets
              key: redis-url
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: veogen-secrets
              key: google-api-key
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
        - name: outputs
          mountPath: /app/outputs
        - name: logs
          mountPath: /app/logs
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: veogen-uploads-pvc
      - name: outputs
        persistentVolumeClaim:
          claimName: veogen-outputs-pvc
      - name: logs
        emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - veogen-backend
              topologyKey: kubernetes.io/hostname

---
# k8s/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: veogen-backend-service
  namespace: veogen
  labels:
    app: veogen-backend
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8001"
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  - port: 8001
    targetPort: 8001
    protocol: TCP
    name: metrics
  selector:
    app: veogen-backend

---
# k8s/backend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: veogen-backend-hpa
  namespace: veogen
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: veogen-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 60
```

---

## 📊 **Container Monitoring & Observability**

### **Monitoring Sidecar Pattern**

```yaml
# Sidecar monitoring configuration
services:
  backend:
    # Main application container
    image: veogen/backend:latest
    # ... main config ...
    
  backend-monitoring:
    # Monitoring sidecar
    image: prom/node-exporter:latest
    pid: "container:backend"
    network_mode: "container:backend"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.processes'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    depends_on:
      - backend
```

### **Container Health Checks**

```dockerfile
# Advanced health check implementation
FROM python:3.11-slim

# Install health check dependencies
RUN apt-get update && apt-get install -y curl netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copy health check script
COPY health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

# Multi-level health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Health check script content:
# #!/bin/bash
# set -e
# 
# # Check application health
# curl -f http://localhost:8000/health || exit 1
# 
# # Check database connectivity
# nc -z postgres 5432 || exit 1
# 
# # Check Redis connectivity
# nc -z redis 6379 || exit 1
# 
# # Check disk space
# df / | awk 'NR==2 {if ($5 > 90) exit 1}'
# 
# # Check memory usage
# free | awk 'NR==2{printf "%.2f\n", $3*100/$2}' | awk '{if ($1 > 90) exit 1}'
# 
# echo "All health checks passed"
```

### **Container Logging Strategy**

```yaml
# Centralized logging configuration
version: '3.8'

x-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service={{.Name}}"

services:
  backend:
    logging:
      <<: *default-logging
      options:
        max-size: "50m"
        max-file: "5"
        labels: "service=veogen-backend,environment=production"
        tag: "backend-{{.ID}}"
    
  # Log aggregator
  fluent-bit:
    image: fluent/fluent-bit:2.1.0
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./logging/fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf:ro
    ports:
      - "24224:24224"
    environment:
      - FLB_LOG_LEVEL=info
    networks:
      - veogen-network
    depends_on:
      - loki
```

---

## 🔄 **CI/CD Integration**

### **Build Pipeline**

```yaml
# .github/workflows/build.yml
name: Build and Push Container Images

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: veogen

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        component: [backend, frontend, worker]
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ github.repository }}/${{ matrix.component }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./${{ matrix.component }}
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILDKIT_INLINE_CACHE=1
            VERSION=${{ github.sha }}
```

### **Deployment Pipeline**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  workflow_run:
    workflows: ["Build and Push Container Images"]
    types:
      - completed
    branches: [main]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        
      - name: Deploy to Docker Swarm
        run: |
          echo "${{ secrets.DEPLOY_KEY }}" | base64 -d > deploy_key
          chmod 600 deploy_key
          
          # Update Docker stack
          ssh -i deploy_key -o StrictHostKeyChecking=no \
            deploy@${{ secrets.DEPLOY_HOST }} \
            "cd /opt/veogen && \
             docker stack deploy -c docker-stack.yml veogen --with-registry-auth"
             
      - name: Health Check
        run: |
          # Wait for deployment to stabilize
          sleep 60
          
          # Check service health
          curl -f https://api.veogen.com/health || exit 1
          curl -f https://veogen.com/health || exit 1
          
      - name: Rollback on Failure
        if: failure()
        run: |
          ssh -i deploy_key -o StrictHostKeyChecking=no \
            deploy@${{ secrets.DEPLOY_HOST }} \
            "docker service rollback veogen_backend"
```

---

## 📈 **Performance Optimization**

### **Container Resource Optimization**

```yaml
# Resource-optimized configuration
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
          pids: 1000
        reservations:
          cpus: '1.0'
          memory: 2G
    
    # JVM-style memory management for Python
    environment:
      - MALLOC_ARENA_MAX=2
      - PYTHONMALLOC=malloc
      - PYTHONPATH=/app
    
    # Optimize for container
    sysctls:
      - net.core.somaxconn=65535
      - net.ipv4.tcp_tw_reuse=1
    
    ulimits:
      nproc: 65535
      nofile:
        soft: 65535
        hard: 65535

  # Resource monitoring sidecar
  resource-monitor:
    image: google/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"
    command:
      - '--housekeeping_interval=10s'
      - '--max_housekeeping_interval=15s'
      - '--event_storage_event_limit=default=0'
      - '--event_storage_age_limit=default=0'
      - '--disable_metrics=percpu,sched,tcp,udp'
      - '--docker_only'
```

### **Network Optimization**

```yaml
# Network-optimized configuration
networks:
  veogen-network:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: veogen0
      com.docker.network.bridge.enable_ip_masquerade: "true"
      com.docker.network.bridge.enable_icc: "true"
      com.docker.network.bridge.host_binding_ipv4: "0.0.0.0"
      com.docker.network.driver.mtu: 1500
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1

services:
  backend:
    networks:
      veogen-network:
        ipv4_address: 172.20.0.10
    # Network optimization
    sysctls:
      - net.core.rmem_max=134217728
      - net.core.wmem_max=134217728
      - net.ipv4.tcp_rmem=4096 65536 134217728
      - net.ipv4.tcp_wmem=4096 65536 134217728
      - net.core.netdev_max_backlog=5000
```

This comprehensive Docker architecture documentation provides enterprise-grade containerization for VeoGen with:

- **Multi-stage optimized builds** for minimal production images
- **Security-first container design** with non-root users and read-only filesystems  
- **Comprehensive orchestration** support for Docker Swarm and Kubernetes
- **Advanced monitoring and observability** with sidecar patterns
- **CI/CD integration** with automated builds and deployments
- **Performance optimization** for production workloads
- **Health checking and auto-recovery** mechanisms
- **Resource management** and scaling strategies

The containerization strategy ensures VeoGen can be deployed reliably across development, staging, and production environments while maintaining security, performance, and operational excellence.
