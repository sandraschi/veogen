# Fix: VeoGen Backend Restarting Issue

## Problem
The veogen backend is restarting because the `unified-monitoring` external network doesn't exist yet.

## Solution Options

### Option 1: Create the Network First (Recommended)

1. **Create the unified-monitoring network:**
   ```powershell
   .\create-monitoring-network.ps1
   ```

2. **Or manually create it:**
   ```powershell
   docker network create --driver bridge --subnet 172.20.0.0/16 configs_unified-monitoring
   ```

3. **Then start veogen:**
   ```powershell
   docker compose up -d
   ```

### Option 2: Start Unified Monitoring Stack First

1. **Start the unified monitoring stack (creates the network):**
   ```powershell
   cd D:\Dev\repos\mcp-central-docs\monitoring\configs
   docker compose -f docker-compose.unified-monitoring.yml up -d
   ```

2. **Then start veogen:**
   ```powershell
   cd D:\Dev\repos\veogen
   docker compose up -d
   ```

### Option 3: Temporary Workaround (No Monitoring)

If you need veogen running immediately without monitoring:

```powershell
docker compose -f docker-compose.yml -f docker-compose.no-monitoring.yml up -d
```

This will start veogen without the unified-monitoring network. You can add monitoring later.

## Verify Fix

After applying a solution, check backend status:

```powershell
docker compose ps backend
docker compose logs backend --tail=50
```

The backend should start successfully and stay running.

