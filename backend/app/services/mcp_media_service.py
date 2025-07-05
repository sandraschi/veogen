"""
MCP Media Service for VeoGen
Integrates with official Google Gemini CLI MCP servers for media generation
"""

import asyncio
import json
import logging
import subprocess
import tempfile
import os
import aiohttp
import base64
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from ..database import get_db
from ..models.user_settings import UserSettings

logger = logging.getLogger(__name__)

class MCPMediaService:
    """Service for generating media using Google's MCP servers"""
    
    def __init__(self):
        self.db = get_db()
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.genmedia_bucket = os.getenv("GENMEDIA_BUCKET")
        
        # Job tracking for progress monitoring
        self.active_jobs = {}
        self.progress_callbacks = {}
        
        # MCP server configurations
        self.mcp_servers = {
            "veo": {
                "binary": "mcp-veo-go",
                "tools": ["veo_t2v", "veo_i2v"],
                "port": 8081
            },
            "imagen": {
                "binary": "mcp-imagen-go", 
                "tools": ["imagen_t2i"],
                "port": 8082
            },
            "lyria": {
                "binary": "mcp-lyria-go",
                "tools": ["lyria_generate_music"],
                "port": 8083
            },
            "chirp": {
                "binary": "mcp-chirp3-go",
                "tools": ["chirp_tts", "list_chirp_voices"],
                "port": 8084
            },
            "avtool": {
                "binary": "mcp-avtool-go",
                "tools": ["media_info", "convert_format", "create_gif"],
                "port": 8085
            }
        }
        
        self.active_servers = {}
        
    def _get_user_api_keys(self, user_id: int) -> Dict[str, str]:
        """Get API keys from user settings with fallback to environment variables"""
        try:
            # Try to get from user settings first
            user_settings = self.db.query(UserSettings).filter(
                UserSettings.user_id == user_id
            ).first()
            
            if user_settings:
                api_keys = {}
                
                # Get Google Cloud Project ID
                if user_settings.google_cloud_project:
                    api_keys["PROJECT_ID"] = user_settings.google_cloud_project
                elif self.project_id:
                    api_keys["PROJECT_ID"] = self.project_id
                    
                # Get Google Cloud Location
                if user_settings.google_cloud_location:
                    api_keys["LOCATION"] = user_settings.google_cloud_location
                else:
                    api_keys["LOCATION"] = self.location
                    
                # Get Google Cloud Storage Bucket
                if user_settings.google_cloud_bucket:
                    api_keys["GENMEDIA_BUCKET"] = user_settings.google_cloud_bucket
                elif self.genmedia_bucket:
                    api_keys["GENMEDIA_BUCKET"] = self.genmedia_bucket
                    
                # Get service account key path if available
                if user_settings.google_service_account_key:
                    api_keys["GOOGLE_APPLICATION_CREDENTIALS"] = user_settings.google_service_account_key
                    
                return api_keys
                
        except Exception as e:
            logger.warning(f"Could not get user API keys for user {user_id}: {e}")
            
        # Fallback to environment variables
        return {
            "PROJECT_ID": self.project_id,
            "LOCATION": self.location,
            "GENMEDIA_BUCKET": self.genmedia_bucket
        }
        
    async def start_mcp_server(self, server_type: str, user_id: Optional[int] = None) -> bool:
        """Start an MCP server for the specified media type"""
        if server_type not in self.mcp_servers:
            logger.error(f"Unknown MCP server type: {server_type}")
            return False
            
        server_config = self.mcp_servers[server_type]
        port = server_config["port"]
        
        try:
            # Check if server is already running
            if server_type in self.active_servers:
                return True
                
            # Start the MCP server
            cmd = [
                server_config["binary"],
                "--transport", "http",
                "--port", str(port)
            ]
            
            # Set environment variables with user-specific API keys
            env = os.environ.copy()
            
            if user_id:
                # Get user-specific API keys
                user_api_keys = self._get_user_api_keys(user_id)
                env.update(user_api_keys)
            else:
                # Use global environment variables
                env["PROJECT_ID"] = self.project_id
                env["LOCATION"] = self.location
                if self.genmedia_bucket:
                    env["GENMEDIA_BUCKET"] = self.genmedia_bucket
                
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(2)
            
            # Check if server is responding
            if await self._check_server_health(port):
                self.active_servers[server_type] = process
                logger.info(f"MCP server {server_type} started on port {port}")
                return True
            else:
                logger.error(f"Failed to start MCP server {server_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting MCP server {server_type}: {e}")
            return False
            
    async def _check_server_health(self, port: int) -> bool:
        """Check if MCP server is responding"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/health", timeout=5) as response:
                    return response.status == 200
        except:
            return False
            
    def _create_job_tracker(self, job_id: str, media_type: str, user_id: int) -> Dict[str, Any]:
        """Create a job tracker for monitoring progress"""
        job_info = {
            "job_id": job_id,
            "media_type": media_type,
            "user_id": user_id,
            "status": "processing",
            "progress": 0,
            "created_at": datetime.utcnow(),
            "started_at": datetime.utcnow(),
            "error_message": None,
            "result": None
        }
        self.active_jobs[job_id] = job_info
        return job_info
        
    def _update_job_progress(self, job_id: str, progress: int, status: str = None, message: str = None):
        """Update job progress and notify callbacks"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["progress"] = progress
            if status:
                self.active_jobs[job_id]["status"] = status
            if message:
                self.active_jobs[job_id]["message"] = message
                
            # Notify progress callback if registered
            if job_id in self.progress_callbacks:
                callback = self.progress_callbacks[job_id]
                try:
                    callback(progress, status, message)
                except Exception as e:
                    logger.error(f"Error in progress callback for job {job_id}: {e}")
                    
    async def _call_mcp_tool_with_progress(self, server_type: str, tool_name: str, params: Dict[str, Any], 
                                         job_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Call an MCP tool with progress tracking"""
        if server_type not in self.active_servers:
            if not await self.start_mcp_server(server_type, user_id):
                raise Exception(f"Failed to start MCP server {server_type}")
                
        port = self.mcp_servers[server_type]["port"]
        
        # Add progress token to params
        progress_token = str(uuid.uuid4())
        params["progressToken"] = progress_token
        
        # Prepare MCP request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        try:
            # Start progress monitoring task
            progress_task = asyncio.create_task(
                self._monitor_mcp_progress(port, progress_token, job_id)
            )
            
            # Make the MCP call
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:{port}/jsonrpc",
                    json=request,
                    timeout=600  # 10 minutes for media generation
                ) as response:
                    result = await response.json()
                    
                    # Cancel progress monitoring
                    progress_task.cancel()
                    
                    if "error" in result:
                        self._update_job_progress(job_id, 0, "failed", f"MCP tool error: {result['error']}")
                        raise Exception(f"MCP tool error: {result['error']}")
                        
                    return result.get("result", {})
                    
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            self._update_job_progress(job_id, 0, "failed", str(e))
            raise
            
    async def _monitor_mcp_progress(self, port: int, progress_token: str, job_id: str):
        """Monitor MCP progress notifications"""
        try:
            async with aiohttp.ClientSession() as session:
                # Subscribe to progress notifications
                async with session.get(f"http://localhost:{port}/notifications") as response:
                    async for line in response.content:
                        if line:
                            try:
                                notification = json.loads(line.decode())
                                if (notification.get("method") == "notifications/progress" and 
                                    notification.get("params", {}).get("progressToken") == progress_token):
                                    
                                    params = notification["params"]
                                    progress = params.get("progress", 0)
                                    status = params.get("status", "processing")
                                    message = params.get("message", "")
                                    
                                    self._update_job_progress(job_id, progress, status, message)
                                    
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Error monitoring MCP progress for job {job_id}: {e}")
            
    async def _call_mcp_tool(self, server_type: str, tool_name: str, params: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Call an MCP tool on the specified server (without progress tracking)"""
        if server_type not in self.active_servers:
            if not await self.start_mcp_server(server_type, user_id):
                raise Exception(f"Failed to start MCP server {server_type}")
                
        port = self.mcp_servers[server_type]["port"]
        
        # Prepare MCP request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:{port}/jsonrpc",
                    json=request,
                    timeout=300  # 5 minutes for non-media operations
                ) as response:
                    result = await response.json()
                    
                    if "error" in result:
                        raise Exception(f"MCP tool error: {result['error']}")
                        
                    return result.get("result", {})
                    
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            raise
            
    async def generate_video(self, prompt: str, duration: int = 10, aspect_ratio: str = "16:9", 
                           user_id: Optional[int] = None, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Generate video using Veo via MCP with progress tracking"""
        job_id = str(uuid.uuid4())
        
        try:
            # Create job tracker
            job_info = self._create_job_tracker(job_id, "video", user_id)
            
            # Register progress callback
            if progress_callback:
                self.progress_callbacks[job_id] = progress_callback
                
            # Update initial progress
            self._update_job_progress(job_id, 5, "processing", "Starting video generation...")
            
            params = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio
            }
            
            result = await self._call_mcp_tool_with_progress("veo", "veo_t2v", params, job_id, user_id)
            
            # Extract video URL from result
            video_url = result.get("video_url")
            if not video_url:
                raise Exception("No video URL returned from Veo")
                
            # Update job as completed
            job_info.update({
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.utcnow(),
                "result": {
                    "video_url": video_url,
                    "duration": duration,
                    "prompt": prompt
                }
            })
            
            self._update_job_progress(job_id, 100, "completed", "Video generation completed!")
            
            return {
                "status": "success",
                "job_id": job_id,
                "video_url": video_url,
                "duration": duration,
                "prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            self._update_job_progress(job_id, 0, "failed", str(e))
            return {
                "status": "error",
                "job_id": job_id,
                "error": str(e)
            }
            
    async def generate_image(self, prompt: str, aspect_ratio: str = "1:1", num_images: int = 1, 
                           user_id: Optional[int] = None, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Generate image using Imagen via MCP with progress tracking"""
        job_id = str(uuid.uuid4())
        
        try:
            # Create job tracker
            job_info = self._create_job_tracker(job_id, "image", user_id)
            
            # Register progress callback
            if progress_callback:
                self.progress_callbacks[job_id] = progress_callback
                
            # Update initial progress
            self._update_job_progress(job_id, 5, "processing", "Starting image generation...")
            
            params = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "num_images": num_images
            }
            
            result = await self._call_mcp_tool_with_progress("imagen", "imagen_t2i", params, job_id, user_id)
            
            # Extract image URLs from result
            image_urls = result.get("image_urls", [])
            if not image_urls:
                raise Exception("No image URLs returned from Imagen")
                
            # Update job as completed
            job_info.update({
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.utcnow(),
                "result": {
                    "image_urls": image_urls,
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio
                }
            })
            
            self._update_job_progress(job_id, 100, "completed", "Image generation completed!")
            
            return {
                "status": "success",
                "job_id": job_id,
                "image_urls": image_urls,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            self._update_job_progress(job_id, 0, "failed", str(e))
            return {
                "status": "error",
                "job_id": job_id,
                "error": str(e)
            }
            
    async def generate_music(self, prompt: str, duration: int = 30, 
                           user_id: Optional[int] = None, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Generate music using Lyria via MCP with progress tracking"""
        job_id = str(uuid.uuid4())
        
        try:
            # Create job tracker
            job_info = self._create_job_tracker(job_id, "music", user_id)
            
            # Register progress callback
            if progress_callback:
                self.progress_callbacks[job_id] = progress_callback
                
            # Update initial progress
            self._update_job_progress(job_id, 5, "processing", "Starting music generation...")
            
            params = {
                "prompt": prompt,
                "duration": duration
            }
            
            result = await self._call_mcp_tool_with_progress("lyria", "lyria_generate_music", params, job_id, user_id)
            
            # Extract music URL from result
            music_url = result.get("music_url")
            if not music_url:
                raise Exception("No music URL returned from Lyria")
                
            # Update job as completed
            job_info.update({
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.utcnow(),
                "result": {
                    "music_url": music_url,
                    "duration": duration,
                    "prompt": prompt
                }
            })
            
            self._update_job_progress(job_id, 100, "completed", "Music generation completed!")
            
            return {
                "status": "success",
                "job_id": job_id,
                "music_url": music_url,
                "duration": duration,
                "prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Error generating music: {e}")
            self._update_job_progress(job_id, 0, "failed", str(e))
            return {
                "status": "error",
                "job_id": job_id,
                "error": str(e)
            }
            
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a generation job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                "job_id": job["job_id"],
                "media_type": job["media_type"],
                "user_id": job["user_id"],
                "status": job["status"],
                "progress": job["progress"],
                "message": job.get("message"),
                "created_at": job["created_at"].isoformat(),
                "started_at": job["started_at"].isoformat(),
                "completed_at": job.get("completed_at", "").isoformat() if job.get("completed_at") else None,
                "error_message": job.get("error_message"),
                "result": job.get("result")
            }
        return None
        
    async def list_user_jobs(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all jobs for a user"""
        user_jobs = [
            job for job in self.active_jobs.values()
            if job["user_id"] == user_id
        ]
        
        # Sort by creation date (newest first)
        user_jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        return [
            {
                "job_id": job["job_id"],
                "media_type": job["media_type"],
                "status": job["status"],
                "progress": job["progress"],
                "message": job.get("message"),
                "created_at": job["created_at"].isoformat(),
                "completed_at": job.get("completed_at", "").isoformat() if job.get("completed_at") else None,
                "result": job.get("result")
            }
            for job in user_jobs[:limit]
        ]
        
    async def download_media_file(self, job_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Download a completed media file"""
        job = self.active_jobs.get(job_id)
        if not job or job["user_id"] != user_id:
            return None
            
        if job["status"] != "completed" or not job.get("result"):
            return None
            
        result = job["result"]
        
        # Extract file URL based on media type
        if job["media_type"] == "video":
            file_url = result.get("video_url")
        elif job["media_type"] == "image":
            file_url = result.get("image_urls", [None])[0]
        elif job["media_type"] == "music":
            file_url = result.get("music_url")
        else:
            return None
            
        if not file_url:
            return None
            
        try:
            # Download the file
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Determine file extension
                        if job["media_type"] == "video":
                            ext = ".mp4"
                        elif job["media_type"] == "image":
                            ext = ".png"
                        elif job["media_type"] == "music":
                            ext = ".mp3"
                        else:
                            ext = ".bin"
                            
                        filename = f"{job_id}{ext}"
                        
                        return {
                            "filename": filename,
                            "content": content,
                            "content_type": response.headers.get("content-type", "application/octet-stream"),
                            "size": len(content)
                        }
                        
        except Exception as e:
            logger.error(f"Error downloading media file for job {job_id}: {e}")
            return None
            
    async def generate_speech(self, text: str, voice: str = "en-US-Neural2-F", 
                            user_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate speech using Chirp 3 HD via MCP"""
        try:
            params = {
                "text": text,
                "voice": voice
            }
            
            result = await self._call_mcp_tool("chirp", "chirp_tts", params, user_id)
            
            # Extract audio data from result
            audio_data = result.get("audio_data")
            if not audio_data:
                raise Exception("No audio data returned from Chirp")
                
            return {
                "status": "success",
                "audio_data": audio_data,
                "voice": voice,
                "text": text
            }
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def get_available_voices(self, user_id: Optional[int] = None) -> List[str]:
        """Get list of available Chirp voices"""
        try:
            result = await self._call_mcp_tool("chirp", "list_chirp_voices", {}, user_id)
            return result.get("voices", [])
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
            
    async def stop_all_servers(self):
        """Stop all active MCP servers"""
        for server_type, process in self.active_servers.items():
            try:
                process.terminate()
                await process.wait()
                logger.info(f"Stopped MCP server {server_type}")
            except Exception as e:
                logger.error(f"Error stopping MCP server {server_type}: {e}")
                
        self.active_servers.clear()

# Global instance
mcp_media_service = MCPMediaService() 