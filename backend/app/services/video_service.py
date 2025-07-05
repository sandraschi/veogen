"""
Video Generation Service for VeoGen
Uses Google's Gemini CLI with MCP servers for video generation
"""

import asyncio
import logging
import tempfile
import os
from typing import Dict, Any, Optional
from pathlib import Path

from .mcp_media_service import mcp_media_service

logger = logging.getLogger(__name__)

class VideoService:
    """Service for video generation using Google's Veo model via MCP"""
    
    def __init__(self):
        self.mcp_service = mcp_media_service
        
    async def generate_video(self, prompt: str, duration: int = 10, aspect_ratio: str = "16:9", 
                           style: str = "cinematic", seed: Optional[int] = None, 
                           temperature: float = 0.7, user_id: Optional[int] = None,
                           progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Generate video using Google's Veo model via MCP
        
        Args:
            prompt: Text description of the video to generate
            duration: Video duration in seconds (1-10)
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
            style: Video style (cinematic, realistic, artistic, etc.)
            seed: Random seed for reproducible results
            temperature: Creativity level (0.0-1.0)
            user_id: User ID for API key management
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary with generation results
        """
        try:
            logger.info(f"Starting video generation for user {user_id}: {prompt[:50]}...")
            
            # Enhance prompt with style
            enhanced_prompt = f"{prompt}, {style} style"
            
            # Generate video using MCP service
            result = await self.mcp_service.generate_video(
                prompt=enhanced_prompt,
                duration=duration,
                aspect_ratio=aspect_ratio,
                user_id=user_id,
                progress_callback=progress_callback
            )
            
            if result["status"] == "success":
                logger.info(f"Video generation completed successfully: {result['job_id']}")
                return {
                    "status": "success",
                    "job_id": result["job_id"],
                    "video_url": result["video_url"],
                    "duration": result["duration"],
                    "enhanced_prompt": enhanced_prompt,
                    "parameters": {
                        "style": style,
                        "seed": seed,
                        "temperature": temperature,
                        "aspect_ratio": aspect_ratio
                    }
                }
            else:
                logger.error(f"Video generation failed: {result.get('error')}")
                return {
                    "status": "error",
                    "job_id": result.get("job_id"),
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error in video generation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def get_generation_status(self, job_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get the status of a video generation job
        
        Args:
            job_id: Job ID to check
            user_id: User ID for authorization
            
        Returns:
            Job status information
        """
        try:
            job_status = await self.mcp_service.get_job_status(job_id)
            
            if not job_status:
                return {
                    "status": "not_found",
                    "job_id": job_id,
                    "error": "Job not found"
                }
                
            # Check if user is authorized to view this job
            if user_id and job_status["user_id"] != user_id:
                return {
                    "status": "unauthorized",
                    "job_id": job_id,
                    "error": "Not authorized to view this job"
                }
                
            return job_status
            
        except Exception as e:
            logger.error(f"Error getting generation status: {e}")
            return {
                "status": "error",
                "job_id": job_id,
                "error": str(e)
            }
            
    async def list_user_jobs(self, user_id: int, limit: int = 50) -> Dict[str, Any]:
        """
        List all video generation jobs for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of jobs to return
            
        Returns:
            List of user's video jobs
        """
        try:
            jobs = await self.mcp_service.list_user_jobs(user_id, limit)
            
            # Filter for video jobs only
            video_jobs = [
                job for job in jobs 
                if job["media_type"] == "video"
            ]
            
            return {
                "status": "success",
                "jobs": video_jobs,
                "total": len(video_jobs)
            }
            
        except Exception as e:
            logger.error(f"Error listing user jobs: {e}")
            return {
                "status": "error",
                "error": str(e),
                "jobs": []
            }
            
    async def download_video(self, job_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Download a completed video file
        
        Args:
            job_id: Job ID
            user_id: User ID for authorization
            
        Returns:
            Video file data or None if not found/authorized
        """
        try:
            return await self.mcp_service.download_media_file(job_id, user_id)
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
            
    async def delete_job(self, job_id: str, user_id: int) -> Dict[str, Any]:
        """
        Delete a video generation job
        
        Args:
            job_id: Job ID to delete
            user_id: User ID for authorization
            
        Returns:
            Deletion result
        """
        try:
            # Check if job exists and user is authorized
            job_status = await self.mcp_service.get_job_status(job_id)
            
            if not job_status:
                return {
                    "status": "not_found",
                    "job_id": job_id,
                    "error": "Job not found"
                }
                
            if job_status["user_id"] != user_id:
                return {
                    "status": "unauthorized",
                    "job_id": job_id,
                    "error": "Not authorized to delete this job"
                }
                
            # Remove from active jobs
            if job_id in self.mcp_service.active_jobs:
                del self.mcp_service.active_jobs[job_id]
                
            # Remove progress callback
            if job_id in self.mcp_service.progress_callbacks:
                del self.mcp_service.progress_callbacks[job_id]
                
            logger.info(f"Deleted video job {job_id} for user {user_id}")
            
            return {
                "status": "success",
                "job_id": job_id,
                "message": "Job deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting job: {e}")
            return {
                "status": "error",
                "job_id": job_id,
                "error": str(e)
            }
            
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of video generation service
        
        Returns:
            Health status information
        """
        try:
            # Check if MCP servers are available
            veo_available = await self.mcp_service.start_mcp_server("veo")
            
            return {
                "status": "healthy" if veo_available else "degraded",
                "mcp_veo_available": veo_available,
                "active_jobs": len([
                    job for job in self.mcp_service.active_jobs.values()
                    if job["media_type"] == "video" and job["status"] == "processing"
                ])
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "mcp_veo_available": False,
                "active_jobs": 0
            }

# Global instance
video_service = VideoService() 