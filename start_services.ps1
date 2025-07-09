cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"
Write-Host "Starting VeoGen Docker services..."
docker-compose up -d
Write-Host "Waiting for services to be ready..."
Start-Sleep 30
docker-compose ps
Write-Host "Services started!"
