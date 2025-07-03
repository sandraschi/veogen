#!/bin/bash

# VeoGen Complete Monitoring Stack Startup Script
# This script initializes and starts the complete VeoGen application with full monitoring

set -e

echo "🚀 Starting VeoGen Complete Monitoring Stack..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p backend/logs
mkdir -p backend/uploads
mkdir -p backend/outputs
mkdir -p backend/temp
mkdir -p nginx/ssl

# Generate self-signed SSL certificates if they don't exist
if [ ! -f "nginx/ssl/cert.pem" ]; then
    print_status "Generating self-signed SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=VeoGen/CN=localhost" 2>/dev/null || {
        print_warning "OpenSSL not available, skipping SSL certificate generation"
    }
fi

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating default environment file..."
    cp backend/.env.example .env
    print_warning "Please update the .env file with your actual API keys and settings"
fi

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Build and start all services
print_status "Building and starting all services..."
docker-compose up --build -d

# Wait for services to be ready
print_status "Waiting for services to initialize..."
sleep 30

# Check service health
print_status "Checking service health..."

services=(
    "backend:8000"
    "frontend:3000"
    "grafana:3000"
    "prometheus:9090"
    "loki:3100"
    "alertmanager:9093"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if docker-compose exec -T "$name" curl -f "http://localhost:$port" >/dev/null 2>&1; then
        print_status "✅ $name is healthy"
    else
        print_warning "⚠️  $name may not be ready yet"
    fi
done

# Display access information
echo ""
echo "🎉 VeoGen Monitoring Stack is starting up!"
echo ""
echo "📊 Access URLs:"
echo "  - VeoGen Frontend:    http://localhost:3000"
echo "  - VeoGen API:         http://localhost:8000"
echo "  - API Documentation:  http://localhost:8000/docs"
echo "  - Grafana:           http://localhost:3001 (admin/veogen123)"
echo "  - Prometheus:        http://localhost:9090"
echo "  - Alertmanager:      http://localhost:9093"
echo "  - Loki:              http://localhost:3100"
echo ""
echo "📈 Grafana Dashboards:"
echo "  - System Overview:    http://localhost:3001/d/veogen-overview"
echo "  - Video Analytics:    http://localhost:3001/d/veogen-video"
echo "  - Infrastructure:     http://localhost:3001/d/veogen-infrastructure"
echo "  - Error Analysis:     http://localhost:3001/d/veogen-errors"
echo ""
echo "🔧 Monitoring Features:"
echo "  ✅ Comprehensive metrics collection"
echo "  ✅ Structured logging with Loki"
echo "  ✅ Real-time dashboards"
echo "  ✅ Alerting rules configured"
echo "  ✅ Container and system monitoring"
echo "  ✅ Error tracking and analysis"
echo ""

# Wait a bit more and then show final status
sleep 15

print_status "Final service status check..."
docker-compose ps

echo ""
print_status "🚀 VeoGen is ready! Check the URLs above to access the application and monitoring tools."
echo ""
print_warning "Note: It may take a few more minutes for all services to be fully operational."
print_warning "If you encounter issues, check logs with: docker-compose logs [service-name]"
echo ""
print_status "To stop all services: docker-compose down"
print_status "To view logs: docker-compose logs -f"
print_status "To restart: ./setup.sh"
