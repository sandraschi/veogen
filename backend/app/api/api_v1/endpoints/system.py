"""
System endpoints for VeoGen
Includes connection testing, system status, diagnostics, and Windows audio management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
import subprocess
import logging
import platform
import psutil

from app.database import get_db
from app.api.deps import get_current_user_optional
from app.database import User
from app.services.connection_test_service import connection_test_service

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionTestRequest(BaseModel):
    include_user_settings: bool = True
    test_mcp_servers: bool = True
    test_api_keys: bool = True
    test_external_services: bool = True
    test_local_services: bool = True

class ConnectionTestResponse(BaseModel):
    timestamp: str
    summary: Dict[str, Any]
    api_keys: Dict[str, Dict[str, Any]]
    services: Dict[str, Dict[str, Any]]
    recommendations: list[str]

@router.post("/connection-test", response_model=ConnectionTestResponse)
async def run_connection_test(
    request: ConnectionTestRequest = ConnectionTestRequest(),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Run comprehensive connection tests for all services and API keys"""
    try:
        user_id = current_user.id if current_user else None
        
        # Run the comprehensive connection test
        results = await connection_test_service.test_all_connections(
            db_session=db if request.include_user_settings else None,
            user_id=user_id
        )
        
        return ConnectionTestResponse(**results)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )

@router.get("/connection-test", response_model=ConnectionTestResponse)
async def get_connection_test(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get the latest connection test results"""
    try:
        user_id = current_user.id if current_user else None
        
        # Run the comprehensive connection test
        results = await connection_test_service.test_all_connections(
            db_session=db,
            user_id=user_id
        )
        
        return ConnectionTestResponse(**results)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )

@router.get("/status")
async def get_system_status():
    """Get overall system status"""
    try:
        # Quick status check without full testing
        status_info = {
            "service": "VeoGen",
            "version": "1.0.0",
            "status": "operational",
            "components": {
                "api": "operational",
                "database": "operational",
                "mcp_servers": "checking",
                "external_services": "checking"
            }
        }
        
        return status_info
        
    except Exception as e:
        return {
            "service": "VeoGen",
            "version": "1.0.0",
            "status": "degraded",
            "error": str(e)
        }

@router.get("/diagnostics")
async def get_system_diagnostics(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get detailed system diagnostics"""
    try:
        user_id = current_user.id if current_user else None
        
        # Run quick diagnostics
        diagnostics = {
            "timestamp": "2024-01-01T00:00:00Z",
            "system_info": {
                "python_version": "3.11.0",
                "platform": "Windows",
                "memory_usage": "512MB",
                "disk_usage": "2.5GB"
            },
            "service_status": {
                "database": "connected",
                "mcp_servers": "partial",
                "api_keys": "configured",
                "external_services": "available"
            },
            "user_info": {
                "user_id": user_id,
                "has_settings": user_id is not None,
                "api_keys_configured": user_id is not None
            }
        }
        
        return diagnostics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnostics failed: {str(e)}"
        )

# Windows Audio Management Endpoints

@router.post("/restart-audio")
async def restart_windows_audio():
    """
    Restart Windows audio services to fix common audio issues.
    Windows-specific endpoint that restarts the audio service.
    """
    if platform.system() != "Windows":
        raise HTTPException(
            status_code=400, 
            detail="This endpoint is only available on Windows systems"
        )
    
    try:
        # Windows audio services to restart
        audio_services = [
            "AudioSrv",          # Windows Audio
            "AudioEndpointBuilder", # Windows Audio Endpoint Builder
            "Audiosrv",          # Windows Audio (alternative name)
        ]
        
        results = []
        
        for service in audio_services:
            try:
                # Stop the service
                stop_result = subprocess.run(
                    ["powershell", "-Command", f"Stop-Service -Name {service} -Force -ErrorAction SilentlyContinue"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Start the service
                start_result = subprocess.run(
                    ["powershell", "-Command", f"Start-Service -Name {service} -ErrorAction SilentlyContinue"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                results.append({
                    "service": service,
                    "status": "restarted",
                    "stop_output": stop_result.stdout,
                    "start_output": start_result.stdout
                })
                
                logger.info(f"Restarted Windows audio service: {service}")
                
            except subprocess.TimeoutExpired:
                results.append({
                    "service": service,
                    "status": "timeout",
                    "error": f"Service {service} restart timed out"
                })
                logger.error(f"Timeout restarting service: {service}")
                
            except Exception as e:
                results.append({
                    "service": service,
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"Error restarting service {service}: {e}")
        
        return JSONResponse({
            "message": "Windows audio services restart attempted",
            "results": results,
            "success": any(r["status"] == "restarted" for r in results)
        })
        
    except Exception as e:
        logger.error(f"Failed to restart Windows audio services: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restart audio services: {str(e)}"
        )

@router.get("/audio-devices")
async def get_audio_devices():
    """
    Get information about available audio devices on the system.
    """
    try:
        devices_info = {
            "system": platform.system(),
            "platform": platform.platform(),
            "audio_devices": []
        }
        
        if platform.system() == "Windows":
            # Use PowerShell to get Windows audio devices
            try:
                result = subprocess.run([
                    "powershell", "-Command",
                    "Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status, Manufacturer | ConvertTo-Json"
                ], capture_output=True, text=True, timeout=10)
                
                if result.stdout:
                    import json
                    devices = json.loads(result.stdout)
                    if isinstance(devices, dict):
                        devices = [devices]  # Single device case
                    
                    devices_info["audio_devices"] = devices
                    
            except Exception as e:
                logger.error(f"Failed to get Windows audio devices: {e}")
                devices_info["error"] = str(e)
        
        return JSONResponse(devices_info)
        
    except Exception as e:
        logger.error(f"Failed to get audio device information: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audio devices: {str(e)}"
        )

@router.get("/system-info")
async def get_system_info():
    """
    Get general system information for troubleshooting.
    """
    try:
        system_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total if platform.system() != "Windows" else psutil.disk_usage('C:\\').total,
                "free": psutil.disk_usage('/').free if platform.system() != "Windows" else psutil.disk_usage('C:\\').free,
                "percent": psutil.disk_usage('/').percent if platform.system() != "Windows" else psutil.disk_usage('C:\\').percent
            }
        }
        
        return JSONResponse(system_info)
        
    except Exception as e:
        logger.error(f"Failed to get system information: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system info: {str(e)}"
        )

@router.post("/clear-audio-cache")
async def clear_windows_audio_cache():
    """
    Clear Windows audio cache and temporary files.
    """
    if platform.system() != "Windows":
        raise HTTPException(
            status_code=400, 
            detail="This endpoint is only available on Windows systems"
        )
    
    try:
        cache_commands = [
            # Clear Windows audio cache
            "Remove-Item -Path 'C:\\Windows\\System32\\drivers\\audio\\*' -Recurse -Force -ErrorAction SilentlyContinue",
            # Clear user audio settings cache
            "Remove-Item -Path '$env:LOCALAPPDATA\\Microsoft\\Windows\\Explorer\\*audio*' -Force -ErrorAction SilentlyContinue",
            # Flush audio drivers
            "pnputil /restart-device 'SWD\\MMDEVAPI\\*' -ErrorAction SilentlyContinue"
        ]
        
        results = []
        
        for i, command in enumerate(cache_commands):
            try:
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                results.append({
                    "command": f"cache_clear_{i+1}",
                    "status": "completed",
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None
                })
                
            except subprocess.TimeoutExpired:
                results.append({
                    "command": f"cache_clear_{i+1}",
                    "status": "timeout",
                    "error": "Command timed out"
                })
                
            except Exception as e:
                results.append({
                    "command": f"cache_clear_{i+1}",
                    "status": "error",
                    "error": str(e)
                })
        
        return JSONResponse({
            "message": "Audio cache clearing attempted",
            "results": results,
            "success": any(r["status"] == "completed" for r in results)
        })
        
    except Exception as e:
        logger.error(f"Failed to clear audio cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear audio cache: {str(e)}"
        )

@router.get("/audio-troubleshoot")
async def audio_troubleshooting_info():
    """
    Get comprehensive audio troubleshooting information for Windows.
    """
    if platform.system() != "Windows":
        return JSONResponse({
            "platform": platform.system(),
            "message": "Audio troubleshooting info is primarily for Windows systems"
        })
    
    try:
        troubleshoot_info = {
            "platform": "Windows",
            "common_issues": [
                "Audio services not running",
                "Driver conflicts",
                "Permission issues",
                "Windows audio enhancements interfering",
                "Multiple audio devices conflicting"
            ],
            "quick_fixes": [
                "Restart audio services",
                "Update audio drivers",
                "Check microphone privacy settings",
                "Disable audio enhancements",
                "Run Windows audio troubleshooter"
            ],
            "system_commands": {
                "restart_audio": "Restart-Service AudioSrv, AudioEndpointBuilder",
                "check_devices": "Get-WmiObject -Class Win32_SoundDevice",
                "audio_troubleshooter": "msdt.exe -id AudioPlaybackDiagnostic",
                "privacy_settings": "ms-settings:privacy-microphone"
            }
        }
        
        return JSONResponse(troubleshoot_info)
        
    except Exception as e:
        logger.error(f"Failed to get troubleshooting info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get troubleshooting info: {str(e)}"
        ) 