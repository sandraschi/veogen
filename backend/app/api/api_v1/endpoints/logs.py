"""
Logs endpoints for VeoGen
Provides access to application logs for monitoring and debugging
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import os
import json
import re
from pathlib import Path

from app.api.deps import get_current_user
from app.database import User

router = APIRouter()

class LogEntry(BaseModel):
    id: str
    timestamp: str
    level: str
    component: str
    message: str
    details: Optional[Dict[str, Any]] = None

class LogsResponse(BaseModel):
    logs: List[LogEntry]
    total_count: int
    filtered_count: int
    available_levels: List[str]
    available_components: List[str]

# Log file mappings
LOG_FILES = {
    "app": "app.log",
    "error": "error.log", 
    "ffmpeg": "ffmpeg.log",
    "movie_maker": "movie_maker.log",
    "video_generation": "video_generation.log"
}

def get_logs_directory():
    """Get the logs directory path"""
    return Path(__file__).parent.parent.parent.parent.parent / "logs"

def parse_log_line(line: str, component: str) -> Optional[LogEntry]:
    """Parse a single log line into a LogEntry"""
    try:
        line = line.strip()
        if not line:
            return None
            
        # Try to parse structured log format (JSON)
        if line.startswith('{'):
            try:
                data = json.loads(line)
                return LogEntry(
                    id=f"{component}_{data.get('timestamp', datetime.now().isoformat())}_{hash(line) % 10000}",
                    timestamp=data.get('timestamp', datetime.now().isoformat()),
                    level=data.get('level', 'info').lower(),
                    component=component,
                    message=data.get('message', ''),
                    details=data.get('details')
                )
            except json.JSONDecodeError:
                pass
        
        # Parse standard log format: TIMESTAMP LEVEL MESSAGE
        patterns = [
            r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+(\w+)\s+(.+)',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\[(\w+)\]\s+(.+)',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+(\w+)\s+(.+)',
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+(\w+):\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                timestamp_str, level, message = match.groups()
                
                # Normalize timestamp
                try:
                    if 'T' not in timestamp_str and ' ' in timestamp_str:
                        timestamp_str = timestamp_str.replace(' ', 'T')
                    if not timestamp_str.endswith('Z') and '+' not in timestamp_str and '-' not in timestamp_str[-6:]:
                        timestamp_str += 'Z'
                    # Validate timestamp
                    datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    timestamp_str = datetime.now().isoformat() + 'Z'
                
                return LogEntry(
                    id=f"{component}_{timestamp_str}_{hash(line) % 10000}",
                    timestamp=timestamp_str,
                    level=level.lower(),
                    component=component,
                    message=message.strip(),
                    details=None
                )
        
        # Fallback: treat entire line as message with current timestamp
        return LogEntry(
            id=f"{component}_{datetime.now().isoformat()}Z_{hash(line) % 10000}",
            timestamp=datetime.now().isoformat() + 'Z',
            level='info',
            component=component,
            message=line,
            details=None
        )
        
    except Exception as e:
        # Return a log entry about the parsing error
        return LogEntry(
            id=f"{component}_parse_error_{hash(line) % 10000}",
            timestamp=datetime.now().isoformat() + 'Z',
            level='error',
            component='log_parser',
            message=f"Failed to parse log line: {str(e)}",
            details={'original_line': line[:200]}
        )

def read_log_file(component: str, max_lines: int = 1000) -> List[LogEntry]:
    """Read and parse a log file"""
    logs_dir = get_logs_directory()
    log_file = logs_dir / LOG_FILES.get(component, f"{component}.log")
    
    entries = []
    if not log_file.exists():
        return entries
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Get the last max_lines lines
        recent_lines = lines[-max_lines:] if len(lines) > max_lines else lines
        
        for line in recent_lines:
            entry = parse_log_line(line, component)
            if entry:
                entries.append(entry)
                
    except Exception as e:
        # Return an error entry if file reading fails
        entries.append(LogEntry(
            id=f"{component}_read_error_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat() + 'Z',
            level='error',
            component='log_reader',
            message=f"Failed to read log file {log_file}: {str(e)}",
            details={'file_path': str(log_file)}
        ))
    
    return entries

@router.get("/", response_model=LogsResponse)
async def get_logs(
    component: Optional[str] = Query(None, description="Filter by component (app, error, ffmpeg, movie_maker, video_generation)"),
    level: Optional[str] = Query(None, description="Filter by log level (debug, info, warning, error)"),
    search: Optional[str] = Query(None, description="Search in log messages"),
    limit: int = Query(1000, description="Maximum number of logs to return", le=5000),
    current_user: User = Depends(get_current_user)
):
    """Get application logs with filtering and pagination"""
    try:
        all_logs = []
        
        # Determine which components to read
        components_to_read = [component] if component and component in LOG_FILES else list(LOG_FILES.keys())
        
        # Read logs from all specified components
        for comp in components_to_read:
            comp_logs = read_log_file(comp, max_lines=limit // len(components_to_read) + 100)
            all_logs.extend(comp_logs)
        
        # Sort by timestamp (newest first)
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply filters
        filtered_logs = all_logs
        
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level.lower()]
        
        if search:
            search_lower = search.lower()
            filtered_logs = [
                log for log in filtered_logs 
                if search_lower in log.message.lower() or search_lower in log.component.lower()
            ]
        
        # Apply limit
        result_logs = filtered_logs[:limit]
        
        # Get available levels and components
        available_levels = list(set(log.level for log in all_logs))
        available_components = list(set(log.component for log in all_logs))
        
        return LogsResponse(
            logs=result_logs,
            total_count=len(all_logs),
            filtered_count=len(filtered_logs),
            available_levels=sorted(available_levels),
            available_components=sorted(available_components)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch logs: {str(e)}"
        )

@router.get("/components")
async def get_log_components(
    current_user: User = Depends(get_current_user)
):
    """Get available log components"""
    logs_dir = get_logs_directory()
    
    components = []
    for component, filename in LOG_FILES.items():
        log_file = logs_dir / filename
        components.append({
            "name": component,
            "filename": filename,
            "exists": log_file.exists(),
            "size": log_file.stat().st_size if log_file.exists() else 0,
            "modified": log_file.stat().st_mtime if log_file.exists() else None
        })
    
    return {"components": components}

@router.get("/tail/{component}")
async def tail_logs(
    component: str,
    lines: int = Query(100, description="Number of recent lines to return", le=1000),
    current_user: User = Depends(get_current_user)
):
    """Get the most recent logs from a specific component (tail-like functionality)"""
    if component not in LOG_FILES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component '{component}' not found. Available: {list(LOG_FILES.keys())}"
        )
    
    try:
        recent_logs = read_log_file(component, max_lines=lines)
        
        return {
            "component": component,
            "lines_requested": lines,
            "lines_returned": len(recent_logs),
            "logs": recent_logs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to tail logs for {component}: {str(e)}"
        )

@router.get("/stream/{component}")
async def stream_logs(
    component: str,
    current_user: User = Depends(get_current_user)
):
    """Stream live logs from a component (returns recent logs for polling)"""
    if component not in LOG_FILES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component '{component}' not found"
        )
    
    # For now, return recent logs. In the future, this could be a WebSocket endpoint
    try:
        recent_logs = read_log_file(component, max_lines=50)
        
        return {
            "component": component,
            "timestamp": datetime.now().isoformat() + 'Z',
            "logs": recent_logs,
            "streaming": False,  # Indicate this is not true streaming yet
            "note": "Use polling for real-time updates. WebSocket streaming coming soon."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream logs for {component}: {str(e)}"
        )
