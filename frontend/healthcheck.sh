#!/bin/sh
# Simple healthcheck for the frontend container
# Exit with 0 if the application is running, non-zero otherwise

# Check if nginx is running
if ! pgrep nginx > /dev/null; then
  echo "Nginx is not running"
  exit 1
fi

# Check if the application is serving content
if ! wget --spider --timeout=5 --tries=1 http://localhost:3000/ 2>/dev/null; then
  echo "Application is not responding"
  exit 1
fi

exit 0
