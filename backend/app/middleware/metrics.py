"""
Prometheus metrics middleware for VeoGen API
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import Match
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
import psutil
import os

logger = logging.getLogger(__name__)

# Create custom registry
REGISTRY = CollectorRegistry()

# Application info
APP_INFO = Info('veogen_app_info', 'VeoGen application information', registry=REGISTRY)
APP_INFO.info({
    'version': os.getenv('APP_VERSION', '1.0.0'),
    'environment': os.getenv('ENVIRONMENT', 'development'),
    'service': 'veogen-backend'
})

# HTTP metrics
HTTP_REQUESTS_TOTAL = Counter(
    'veogen_http_requests_total',
    'Total HTTP requests by method, endpoint and status',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

HTTP_REQUEST_DURATION = Histogram(
    'veogen_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

HTTP_REQUEST_SIZE = Histogram(
    'veogen_http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=REGISTRY
)

HTTP_RESPONSE_SIZE = Histogram(
    'veogen_http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Video generation metrics
VIDEO_GENERATIONS_TOTAL = Counter(
    'veogen_video_generations_total',
    'Total video generations by status',
    ['status', 'style'],
    registry=REGISTRY
)

VIDEO_GENERATION_DURATION = Histogram(
    'veogen_video_generation_duration_seconds',
    'Video generation duration in seconds',
    ['style'],
    buckets=[10, 30, 60, 120, 300, 600, 1200, 1800, 3600],
    registry=REGISTRY
)

VIDEO_QUEUE_SIZE = Gauge(
    'veogen_video_queue_size',
    'Current video generation queue size',
    registry=REGISTRY
)

VIDEO_ACTIVE_GENERATIONS = Gauge(
    'veogen_active_video_generations',
    'Currently active video generations',
    registry=REGISTRY
)

# Movie maker metrics
MOVIE_PROJECTS_TOTAL = Counter(
    'veogen_movie_projects_total',
    'Total movie projects by status',
    ['status', 'style'],
    registry=REGISTRY
)

MOVIE_SCENES_TOTAL = Counter(
    'veogen_movie_scenes_total',
    'Total movie scenes generated',
    ['project_style', 'scene_type'],
    registry=REGISTRY
)

MOVIE_PROJECT_DURATION = Histogram(
    'veogen_movie_project_duration_seconds',
    'Movie project completion duration in seconds',
    ['style'],
    buckets=[300, 600, 1200, 1800, 3600, 7200, 14400, 28800],
    registry=REGISTRY
)

ACTIVE_MOVIE_PROJECTS = Gauge(
    'veogen_active_movie_projects',
    'Currently active movie projects',
    registry=REGISTRY
)

# FFmpeg metrics
FFMPEG_OPERATIONS_TOTAL = Counter(
    'veogen_ffmpeg_operations_total',
    'Total FFmpeg operations by type and status',
    ['operation_type', 'status'],
    registry=REGISTRY
)

FFMPEG_OPERATION_DURATION = Histogram(
    'veogen_ffmpeg_operation_duration_seconds',
    'FFmpeg operation duration in seconds',
    ['operation_type'],
    registry=REGISTRY
)

# File system metrics
FILE_STORAGE_BYTES = Gauge(
    'veogen_file_storage_bytes',
    'File storage usage in bytes by type',
    ['storage_type'],
    registry=REGISTRY
)

FILE_OPERATIONS_TOTAL = Counter(
    'veogen_file_operations_total',
    'Total file operations by type and status',
    ['operation_type', 'status'],
    registry=REGISTRY
)

# System metrics
SYSTEM_CPU_USAGE = Gauge(
    'veogen_system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=REGISTRY
)

SYSTEM_MEMORY_USAGE = Gauge(
    'veogen_system_memory_usage_bytes',
    'System memory usage in bytes',
    ['type'],
    registry=REGISTRY
)

SYSTEM_DISK_USAGE = Gauge(
    'veogen_system_disk_usage_bytes',
    'System disk usage in bytes',
    ['mount_point', 'type'],
    registry=REGISTRY
)

# Gemini API metrics
GEMINI_API_CALLS_TOTAL = Counter(
    'veogen_gemini_api_calls_total',
    'Total Gemini API calls by status',
    ['status', 'model'],
    registry=REGISTRY
)

GEMINI_API_DURATION = Histogram(
    'veogen_gemini_api_duration_seconds',
    'Gemini API call duration in seconds',
    ['model'],
    registry=REGISTRY
)

GEMINI_TOKENS_TOTAL = Counter(
    'veogen_gemini_tokens_total',
    'Total tokens used by type',
    ['type', 'model'],
    registry=REGISTRY
)

# Error metrics
ERROR_TOTAL = Counter(
    'veogen_errors_total',
    'Total errors by type and severity',
    ['error_type', 'severity', 'component'],
    registry=REGISTRY
)

def get_route_name(request: Request) -> str:
    """Extract route name from request"""
    try:
        for route in request.app.routes:
            match, _ = route.matches({"type": "http", "path": request.url.path, "method": request.method})
            if match == Match.FULL:
                return route.path
        return request.url.path
    except Exception:
        return request.url.path

def update_system_metrics():
    """Update system-level metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)
        SYSTEM_CPU_USAGE.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY_USAGE.labels(type='used').set(memory.used)
        SYSTEM_MEMORY_USAGE.labels(type='available').set(memory.available)
        SYSTEM_MEMORY_USAGE.labels(type='total').set(memory.total)
        
        # Disk usage
        for partition in psutil.disk_partitions():
            try:
                disk_usage = psutil.disk_usage(partition.mountpoint)
                SYSTEM_DISK_USAGE.labels(mount_point=partition.mountpoint, type='used').set(disk_usage.used)
                SYSTEM_DISK_USAGE.labels(mount_point=partition.mountpoint, type='free').set(disk_usage.free)
                SYSTEM_DISK_USAGE.labels(mount_point=partition.mountpoint, type='total').set(disk_usage.total)
            except (PermissionError, OSError):
                continue
                
        # File storage metrics
        storage_paths = {
            'uploads': '/app/uploads',
            'outputs': '/app/outputs', 
            'temp': '/app/temp',
            'logs': '/app/logs'
        }
        
        for storage_type, path in storage_paths.items():
            if os.path.exists(path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        try:
                            filepath = os.path.join(dirpath, filename)
                            total_size += os.path.getsize(filepath)
                        except (OSError, IOError):
                            continue
                FILE_STORAGE_BYTES.labels(storage_type=storage_type).set(total_size)
                
    except Exception as e:
        logger.warning(f"Failed to update system metrics: {e}")

class PrometheusMetricsMiddleware:
    """Middleware to collect Prometheus metrics"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            await self.app(scope, receive, send)
            return
            
        method = request.method
        endpoint = get_route_name(request)
        
        # Start timer
        start_time = time.time()
        
        # Get request size
        request_size = 0
        if "content-length" in request.headers:
            try:
                request_size = int(request.headers["content-length"])
            except ValueError:
                pass
                
        # Process request
        response_data = {}
        status_code = 500
        response_size = 0
        
        async def send_wrapper(message):
            nonlocal status_code, response_size
            if message["type"] == "http.response.start":
                status_code = message["status"]
                # Get response size from headers if available
                for name, value in message.get("headers", []):
                    if name == b"content-length":
                        try:
                            response_size = int(value.decode())
                        except (ValueError, UnicodeDecodeError):
                            pass
            elif message["type"] == "http.response.body":
                if "body" in message:
                    response_size += len(message["body"])
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            status_code = 500
            logger.error(f"Request failed: {e}")
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Update metrics
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code)
            ).inc()
            
            HTTP_REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            if request_size > 0:
                HTTP_REQUEST_SIZE.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(request_size)
                
            if response_size > 0:
                HTTP_RESPONSE_SIZE.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(response_size)
            
            # Update system metrics periodically
            if int(time.time()) % 30 == 0:  # Every 30 seconds
                update_system_metrics()

async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    update_system_metrics()
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )

# Utility functions for services to use
def track_video_generation(style: str, status: str, duration: float = None):
    """Track video generation metrics"""
    VIDEO_GENERATIONS_TOTAL.labels(status=status, style=style).inc()
    if duration is not None and status == "completed":
        VIDEO_GENERATION_DURATION.labels(style=style).observe(duration)

def track_movie_project(style: str, status: str, duration: float = None):
    """Track movie project metrics"""
    MOVIE_PROJECTS_TOTAL.labels(status=status, style=style).inc()
    if duration is not None and status == "completed":
        MOVIE_PROJECT_DURATION.labels(style=style).observe(duration)

def track_movie_scene(project_style: str, scene_type: str):
    """Track movie scene generation"""
    MOVIE_SCENES_TOTAL.labels(project_style=project_style, scene_type=scene_type).inc()

def track_ffmpeg_operation(operation_type: str, status: str, duration: float = None):
    """Track FFmpeg operation metrics"""
    FFMPEG_OPERATIONS_TOTAL.labels(operation_type=operation_type, status=status).inc()
    if duration is not None and status == "completed":
        FFMPEG_OPERATION_DURATION.labels(operation_type=operation_type).observe(duration)

def track_gemini_api_call(model: str, status: str, duration: float, input_tokens: int = 0, output_tokens: int = 0):
    """Track Gemini API call metrics"""
    GEMINI_API_CALLS_TOTAL.labels(status=status, model=model).inc()
    GEMINI_API_DURATION.labels(model=model).observe(duration)
    if input_tokens > 0:
        GEMINI_TOKENS_TOTAL.labels(type="input", model=model).inc(input_tokens)
    if output_tokens > 0:
        GEMINI_TOKENS_TOTAL.labels(type="output", model=model).inc(output_tokens)

def track_file_operation(operation_type: str, status: str):
    """Track file operation metrics"""
    FILE_OPERATIONS_TOTAL.labels(operation_type=operation_type, status=status).inc()

def track_error(error_type: str, severity: str, component: str):
    """Track error metrics"""
    ERROR_TOTAL.labels(error_type=error_type, severity=severity, component=component).inc()

def set_queue_size(size: int):
    """Set current queue size"""
    VIDEO_QUEUE_SIZE.set(size)

def set_active_generations(count: int):
    """Set active generation count"""
    VIDEO_ACTIVE_GENERATIONS.set(count)

def set_active_movie_projects(count: int):
    """Set active movie project count"""
    ACTIVE_MOVIE_PROJECTS.set(count)
