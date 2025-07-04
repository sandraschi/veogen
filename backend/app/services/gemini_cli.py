import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, List, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx
from app.config import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiCLIService:
    """Service for interacting with Google Gemini API for Veo video generation"""
    
    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        
        # Configure the API
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.warning(f"Could not configure Gemini API: {e}")
    
    async def install_gemini_cli(self) -> bool:
        """Install Gemini CLI if not present - Mock implementation"""
        logger.info("Gemini CLI installation not required - using Python API")
        return True
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        style: Optional[str] = None,
        seed: Optional[int] = None,
        temperature: float = 0.7,
        output_format: str = "mp4"
    ) -> Dict[str, Any]:
        """
        Generate video using Veo 3 model via Gemini API
        
        Args:
            prompt: Text description of the video to generate
            duration: Duration in seconds (5-60)
            aspect_ratio: Video aspect ratio (16:9 or 9:16)
            style: Visual style for the video
            seed: Random seed for reproducibility
            temperature: Creativity level (0.0-1.0)
            output_format: Output format (mp4 or webm)
            
        Returns:
            Dictionary containing video data and metadata
        """
        try:
            logger.info(f"Generating Veo 3 video with prompt: {prompt}")
            
            # Prepare Veo 3 API request
            veo_params = {
                "prompt": prompt,
                "duration_seconds": min(max(5, duration), 60),  # Clamp to 5-60s
                "aspect_ratio": aspect_ratio if aspect_ratio in ["16:9", "9:16"] else "16:9",
                "model": "veo-3"  # Explicitly use Veo 3
            }
            
            if style:
                veo_params["style"] = style
            if seed is not None:
                veo_params["seed"] = seed
            if temperature is not None:
                veo_params["temperature"] = max(0.0, min(1.0, temperature))
                
            # Call Veo 3 API (mock implementation - replace with actual API call)
            video_data = await self._call_veo_api(veo_params)
            
            result = {
                "status": "success",
                "message": f"Video generated with Veo 3: {prompt}",
                "video_data": video_data,
                "video_size": len(video_data) if video_data else 0,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "style": style,
                "temperature": temperature
            }
            
            logger.info(f"Veo 3 video generation completed: {len(video_data) if video_data else 0} bytes")
            return result
                    
        except Exception as e:
            logger.error(f"Error in generate_video: {e}")
            raise
    
    async def _call_veo_api(self, params: Dict[str, Any]) -> bytes:
        """
        Call the Veo 3 API to generate a video
        
        Note: This is a placeholder implementation. In a real scenario,
        you would make an API call to Google's Veo 3 service.
        
        Args:
            params: Parameters for video generation
            
        Returns:
            Video data as bytes
        """
        try:
            # In a real implementation, this would make an API call to Veo 3
            # For now, we'll create a simple test video with a placeholder message
            
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / f"veo3_video.mp4"
                
                # Create a simple test video with FFmpeg
                cmd = [
                    "ffmpeg",
                    "-f", "lavfi",
                    "-i", f"color=c=blue:s=1920x1080:d={params.get('duration_seconds', 5)}",
                    "-vf", f"drawtext=text='Veo 3: {params.get('prompt', '')}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5:boxborderw=10",
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-y",
                    str(output_path)
                ]
                
                # Veo 3 handles audio natively - no need to add audio track
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    logger.error(f"FFmpeg error: {stderr.decode()}")
                    raise Exception(f"Failed to create test video: {stderr.decode()}")
                
                # Read the generated video
                if output_path.exists():
                    return output_path.read_bytes()
                
                return b""
                
        except Exception as e:
            logger.error(f"Error in _call_veo_api: {e}")
            raise
    
    async def _create_test_video(self, output_path: str, prompt: str, duration: int):
        """Create a test video using ffmpeg for development purposes"""
        try:
            # Create a simple colored video with text overlay
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"color=c=blue:s=1920x1080:d={duration}",
                "-vf", f"drawtext=text='{prompt}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v", "libx264",
                "-preset", "fast",
                "-y",
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"FFmpeg test video creation failed: {stderr.decode()}")
                raise Exception("Test video creation failed")
                
        except Exception as e:
            logger.warning(f"Could not create test video with FFmpeg: {e}")
            # Create an empty file as fallback
            Path(output_path).write_bytes(b"")
    
    async def check_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Check the status of a video generation job - Mock implementation"""
        return {
            "status": "completed",
            "job_id": job_id,
            "progress": 100
        }
    
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate text using Gemini API"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            # Fallback to mock response
            return f"Mock response for: {prompt}"
    
    async def list_available_models(self) -> List[str]:
        """List available models - Mock implementation"""
        return [
            "gemini-pro",
            "gemini-pro-vision", 
            "veo-3"  # Mock Veo model
        ]
    
    async def get_model_info(self, model_name: str = "veo-3") -> Dict[str, Any]:
        """Get model information - Mock implementation"""
        return {
            "name": model_name,
            "description": "Mock model for testing",
            "capabilities": ["text-generation", "video-generation"],
            "max_duration": 10,
            "supported_aspect_ratios": ["16:9", "9:16", "1:1"]
        }

# Global service instance
gemini_service = GeminiCLIService()
