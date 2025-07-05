import google.generativeai as genai
from google.cloud import aiplatform
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from app.config import settings
from app.models.video_request import VideoGenerationRequest, VideoGenerationResponse
import tempfile
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.setup_gemini()
        self.setup_vertex_ai()
    
    def setup_gemini(self):
        """Initialize Gemini AI"""
        try:
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Gemini AI initialized successfully")
            else:
                logger.warning("GEMINI_API_KEY not found in environment")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise
    
    def setup_vertex_ai(self):
        """Initialize Vertex AI for Veo"""
        try:
            if settings.GOOGLE_CLOUD_PROJECT:
                aiplatform.init(
                    project=settings.GOOGLE_CLOUD_PROJECT,
                    location="us-central1"
                )
                logger.info("Vertex AI initialized successfully")
            else:
                logger.warning("GOOGLE_CLOUD_PROJECT not found in environment")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise
    
    async def enhance_prompt(self, user_prompt: str, video_style: str = "cinematic") -> str:
        """Use Gemini to enhance and optimize the video generation prompt"""
        try:
            enhancement_prompt = f"""
            You are an expert video generation prompt engineer. Take the user's basic request and enhance it into a detailed, professional video generation prompt.
            
            User's request: "{user_prompt}"
            Desired style: {video_style}
            
            Please enhance this into a detailed prompt that includes:
            - Visual composition and framing
            - Lighting and atmosphere
            - Movement and camera work
            - Color palette and mood
            - Technical quality specifications
            
            Keep the enhanced prompt under 500 characters while being descriptive and cinematic.
            Return only the enhanced prompt, nothing else.
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                enhancement_prompt
            )
            
            enhanced_prompt = response.text.strip()
            logger.info(f"Enhanced prompt: {enhanced_prompt}")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Failed to enhance prompt: {str(e)}")
            return user_prompt  # Return original if enhancement fails
    async def generate_video_with_veo(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """
        Generate video using Google's Veo 3 model
        
        Args:
            request: Video generation request parameters
            
        Returns:
            VideoGenerationResponse with generated video details
        """
        try:
            # Enhance the prompt using Gemini
            enhanced_prompt = await self.enhance_prompt(
                request.prompt, 
                request.style or "cinematic"
            )
            
            # Prepare Veo 3 generation parameters
            veo_params = {
                "prompt": enhanced_prompt,
                "aspect_ratio": request.aspect_ratio or "16:9",
                "duration_seconds": min(max(5, request.duration or 5), 60),  # 5-60s
                "style": request.style or "cinematic",
                "model": "veo-3"  # Explicitly use Veo 3
            }
            
            # Add reference image if provided
            if request.reference_image:
                veo_params["reference_image"] = request.reference_image
            
            # Generate video using Vertex AI
            video_response = await self._call_veo_api(veo_params)
            
            return VideoGenerationResponse(
                video_url=video_response.get("video_url"),
                status="completed",
                generation_time=video_response.get("generation_time"),
                enhanced_prompt=enhanced_prompt,
                parameters=veo_params
            )
            
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            raise
    
    async def _call_veo_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call the Veo API through Vertex AI"""
        try:
            # This is a placeholder for the actual Veo API call
            # The exact implementation depends on Google's Veo API structure
            
            # For now, we'll simulate the API call
            import time
            await asyncio.sleep(2)  # Simulate processing time
            
            # Use MCP media service for actual Veo generation
            from .mcp_media_service import mcp_media_service
            
            # Generate video using MCP service
            video_result = await mcp_media_service.generate_video(
                prompt=params["prompt"],
                duration=params["duration_seconds"],
                aspect_ratio=params["aspect_ratio"],
                style=params.get("style", "cinematic"),
                user_id=None  # Will be set by the calling service
            )
            
            if video_result and "video_path" in video_result:
                response = {
                    "video_url": video_result["video_path"],
                    "generation_time": video_result.get("generation_time", 0),
                    "status": "completed"
                }
            else:
                raise Exception("Video generation failed")
            
            logger.info("Veo API call completed successfully")
            return mock_response
            
        except Exception as e:
            logger.error(f"Veo API call failed: {str(e)}")
            raise
    
    async def get_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Check the status of a video generation job"""
        try:
            # Use MCP media service to check job status
            from .mcp_media_service import mcp_media_service
            
            job_status = await mcp_media_service.get_job_status(job_id)
            if job_status:
                return {
                    "job_id": job_id,
                    "status": job_status["status"],
                    "progress": job_status["progress"],
                    "estimated_completion": job_status.get("estimated_completion"),
                    "message": job_status.get("message")
                }
            else:
                return {
                    "job_id": job_id,
                    "status": "not_found",
                    "progress": 0,
                    "estimated_completion": None,
                    "message": "Job not found"
                }
        except Exception as e:
            logger.error(f"Failed to get job status: {str(e)}")
            raise

gemini_service = GeminiService()
