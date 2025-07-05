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
from google.cloud import aiplatform
from app.database import get_user_setting

logger = logging.getLogger(__name__)

class GeminiCLIService:
    """Service for interacting with Google Gemini via CLI and MCP tools"""
    
    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self.initialized = False
        self.mcp_server_url = "http://localhost:3000"  # Default MCP media server
        self._initialize_apis()
    
    def _get_api_key_from_user_settings(self, db_session=None, user_id=None, key_name="gemini_api_key"):
        """Get API key from user settings first, then environment variables"""
        try:
            if db_session and user_id:
                # Try to get from user settings first
                user_key = get_user_setting(db_session, user_id, key_name)
                if user_key:
                    return user_key
        except Exception as e:
            logger.warning(f"Could not get API key from user settings: {e}")
        
        # Fall back to environment variables
        if key_name == "gemini_api_key":
            return settings.GEMINI_API_KEY
        elif key_name == "google_api_key":
            return settings.GOOGLE_API_KEY
        elif key_name == "google_cloud_project":
            return settings.GOOGLE_CLOUD_PROJECT
        
        return None
    
    async def initialize(self, db_session=None, user_id=None):
        """Initialize Gemini CLI service with user settings"""
        try:
            # Initialize APIs
            self._initialize_apis(db_session, user_id)
            
            # Check if Gemini CLI is available
            cli_available = await self.check_gemini_cli_available()
            if cli_available:
                logger.info("Gemini CLI is available for enhanced functionality")
            else:
                logger.warning("Gemini CLI not available, using API fallback")
            
            # Check MCP server availability
            mcp_available = await self.check_mcp_server_available()
            if mcp_available:
                logger.info("MCP media server is available")
            else:
                logger.warning("MCP media server not available")
            
            self.initialized = True
            logger.info("Gemini CLI service initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini CLI service: {e}")
            # Continue with basic functionality
    
    def _initialize_apis(self, db_session=None, user_id=None):
        """Initialize Google Cloud AI Platform and Gemini APIs"""
        try:
            # Get API keys from user settings or environment
            gemini_key = self._get_api_key_from_user_settings(db_session, user_id, "gemini_api_key")
            google_key = self._get_api_key_from_user_settings(db_session, user_id, "google_api_key")
            project_id = self._get_api_key_from_user_settings(db_session, user_id, "google_cloud_project") or self.project_id
            
            # Initialize Google Cloud AI Platform
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                aiplatform.init(
                    project=project_id,
                    location=self.location,
                    credentials=settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                aiplatform.init(
                    project=project_id,
                    location=self.location
                )
            
            # Configure Gemini API
            if gemini_key:
                genai.configure(api_key=gemini_key)
            
            logger.info("APIs initialized with Google Cloud AI Platform")
            
        except Exception as e:
            logger.error(f"Failed to initialize APIs: {e}")
            # Continue with fallback to Gemini for text generation
    
    async def install_gemini_cli(self) -> bool:
        """Install Gemini CLI if not present"""
        try:
            # Check if gemini CLI is available (this could be the official Google CLI or a compatible one)
            result = await asyncio.create_subprocess_exec(
                "gemini", "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info("Gemini CLI already available")
                return True
            
            # Try alternative CLI names
            for cli_name in ["gemini-cli", "google-gemini", "gemini"]:
                result = await asyncio.create_subprocess_exec(
                    cli_name, "--help",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    logger.info(f"Found Gemini CLI: {cli_name}")
                    return True
            
            logger.warning("Gemini CLI not found - media generation will use fallback methods")
            return False
                
        except Exception as e:
            logger.error(f"Error checking Gemini CLI: {e}")
            return False

    async def _call_mcp_media_server(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call the MCP media server for generation"""
        try:
            url = f"{self.mcp_server_url}/{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": settings.GOOGLE_API_KEY or ""
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=params, headers=headers, timeout=300.0)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error calling MCP media server: {e}")
            raise

    async def _call_gemini_cli_with_mcp(self, prompt: str, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call Gemini CLI with MCP tools for media generation"""
        try:
            # Prepare the command for Gemini CLI with MCP tool
            cmd = ["gemini", prompt, "--tool", tool_name]
            
            if params:
                cmd.extend(["--params", json.dumps(params)])
            
            logger.info(f"Calling Gemini CLI with MCP tool: {' '.join(cmd)}")
            
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Gemini CLI error: {stderr.decode()}")
                raise Exception(f"Gemini CLI failed: {stderr.decode()}")
            
            # Parse the output
            output = stdout.decode().strip()
            
            try:
                # Try to parse as JSON
                return json.loads(output)
            except json.JSONDecodeError:
                # Return as text if not JSON
                return {"text": output, "raw_output": output}
            
        except Exception as e:
            logger.error(f"Error calling Gemini CLI with MCP: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        style: Optional[str] = None,
        seed: Optional[int] = None,
        temperature: float = 0.7,
        output_format: str = "mp4",
        db_session=None,
        user_id=None
    ) -> Dict[str, Any]:
        """
        Generate video using Veo 3 model via Gemini CLI with MCP tools
        
        Args:
            prompt: Text description of the video to generate
            duration: Duration in seconds (5-60)
            aspect_ratio: Video aspect ratio (16:9 or 9:16)
            style: Visual style for the video
            seed: Random seed for reproducibility
            temperature: Creativity level (0.0-1.0)
            output_format: Output format (mp4 or webm)
            db_session: Database session for user settings
            user_id: User ID for getting API keys from settings
            
        Returns:
            Dictionary containing video data and metadata
        """
        try:
            logger.info(f"Generating Veo 3 video with prompt: {prompt}")
            
            # Re-initialize with user settings if provided
            if db_session and user_id and not self.initialized:
                self._initialize_apis(db_session, user_id)
            
            # Try Gemini CLI with MCP first, then fallback to direct MCP server, then API
            try:
                # Use Gemini CLI with MCP tool
                params = {
                    "prompt": prompt,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "style": style,
                    "temperature": temperature
                }
                
                result = await self._call_gemini_cli_with_mcp(
                    f"Generate a {duration}-second video: {prompt}",
                    "googleMediaV3.generate_video",
                    params
                )
                
                api_used = "gemini_cli_mcp"
                
            except Exception as e:
                logger.warning(f"Gemini CLI with MCP failed, trying direct MCP server: {e}")
                try:
                    # Try direct MCP server call
                    result = await self._call_mcp_media_server("generate/video", {
                        "prompt": prompt,
                        "duration": duration,
                        "resolution": "1080p",
                        "style": style
                    })
                    api_used = "mcp_direct"
                    
                except Exception as e2:
                    logger.warning(f"Direct MCP server failed, falling back to API: {e2}")
                    # Fallback to direct API call
                    video_data = await self._call_veo_api_real(prompt, duration, aspect_ratio, style, seed, temperature, db_session, user_id)
                    result = {
                        "video_data": video_data,
                        "status": "success"
                    }
                    api_used = "veo_api_direct"
            
            # Ensure we have video data
            if "video_data" not in result and "videoUrl" in result:
                # Download video from URL
                video_url = result["videoUrl"]
                async with httpx.AsyncClient() as client:
                    video_response = await client.get(video_url)
                    video_response.raise_for_status()
                    result["video_data"] = video_response.content
            
            final_result = {
                "status": "success",
                "message": f"Video generated with Veo 3: {prompt}",
                "video_data": result.get("video_data", b""),
                "video_size": len(result.get("video_data", b"")),
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "style": style,
                "temperature": temperature,
                "api_used": api_used
            }
            
            logger.info(f"Veo 3 video generation completed: {len(final_result['video_data'])} bytes")
            return final_result
                    
        except Exception as e:
            logger.error(f"Error in generate_video: {e}")
            raise
    
    async def _call_veo_api_real(
        self, 
        prompt: str, 
        duration: int, 
        aspect_ratio: str, 
        style: Optional[str] = None, 
        seed: Optional[int] = None, 
        temperature: float = 0.7,
        db_session=None,
        user_id=None
    ) -> bytes:
        """
        Call the real Veo 3 API via Google Cloud AI Platform
        
        Args:
            prompt: Text description of the video to generate
            duration: Duration in seconds
            aspect_ratio: Video aspect ratio
            style: Visual style for the video
            seed: Random seed for reproducibility
            temperature: Creativity level
            db_session: Database session for user settings
            user_id: User ID for getting API keys from settings
            
        Returns:
            Video data as bytes
        """
        try:
            # Get project ID from user settings or environment
            project_id = self._get_api_key_from_user_settings(db_session, user_id, "google_cloud_project") or self.project_id
            
            # Prepare the request for Veo
            veo_request = {
                "prompt": prompt,
                "duration_seconds": min(max(5, duration), 60),  # Clamp to 5-60s
                "aspect_ratio": aspect_ratio if aspect_ratio in ["16:9", "9:16"] else "16:9",
                "model": "veo-3"
            }
            
            if style:
                veo_request["style"] = style
            if seed is not None:
                veo_request["seed"] = seed
            if temperature is not None:
                veo_request["temperature"] = max(0.0, min(1.0, temperature))
            
            # Call Veo API via Google Cloud AI Platform
            endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{project_id}/locations/{self.location}/endpoints/veo"
            )
            
            # Make prediction request
            response = await asyncio.to_thread(
                endpoint.predict,
                instances=[veo_request]
            )
            
            # Extract video data from response
            video_data = response.predictions[0]
            
            # Convert to bytes if needed
            if isinstance(video_data, str):
                import base64
                video_data = base64.b64decode(video_data)
            
            return video_data
            
        except Exception as e:
            logger.error(f"Real Veo API call failed: {e}")
            raise
    
    async def _call_veo_api_test(self, prompt: str, duration: int, aspect_ratio: str) -> bytes:
        """
        Create a test video using FFmpeg for development purposes
        
        Args:
            prompt: Text description of the video to generate
            duration: Duration in seconds
            aspect_ratio: Video aspect ratio
            
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
                    "-i", f"color=c=blue:s=1920x1080:d={duration}",
                    "-vf", f"drawtext=text='Veo 3: {prompt}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5:boxborderw=10",
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
            logger.error(f"Error in _call_veo_api_test: {e}")
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
        """Check the status of a video generation job"""
        try:
            # Use MCP media service to check job status
            from .mcp_media_service import mcp_media_service
            
            job_status = await mcp_media_service.get_job_status(job_id)
            if job_status:
                return {
                    "status": job_status["status"],
                    "job_id": job_id,
                    "progress": job_status["progress"],
                    "message": job_status.get("message"),
                    "result": job_status.get("result")
                }
            else:
                return {
                    "status": "not_found",
                    "job_id": job_id,
                    "progress": 0,
                    "error": "Job not found"
                }
        except Exception as e:
            logger.error(f"Error checking generation status: {e}")
            return {
                "status": "error",
                "job_id": job_id,
                "progress": 0,
                "error": str(e)
            }
    
    async def _call_gemini_cli_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Call Gemini CLI for text generation
        
        Args:
            prompt: Text prompt for generation
            temperature: Creativity level
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            # Try Gemini CLI with MCP first
            result = await self._call_gemini_cli_with_mcp(
                prompt,
                "googleMediaV3.generate_text",
                {"temperature": temperature, "max_tokens": max_tokens}
            )
            
            if "text" in result:
                return result["text"]
            elif "raw_output" in result:
                return result["raw_output"]
            else:
                return str(result)
            
        except Exception as e:
            logger.error(f"Error calling Gemini CLI for text: {e}")
            raise

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        db_session=None,
        user_id=None
    ) -> str:
        """Generate text using Gemini CLI with MCP tools"""
        try:
            # Re-initialize with user settings if provided
            if db_session and user_id and not self.initialized:
                self._initialize_apis(db_session, user_id)
            
            # Try Gemini CLI with MCP first, then fallback to API
            try:
                response = await self._call_gemini_cli_text(prompt, temperature, max_tokens)
                return response
            except Exception as e:
                logger.warning(f"Gemini CLI with MCP failed, falling back to API: {e}")
                # Fallback to API
                model = genai.GenerativeModel('gemini-pro')
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt
                )
                return response.text
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            # Fallback to basic response
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    async def check_gemini_cli_available(self) -> bool:
        """Check if Gemini CLI is available and working"""
        try:
            # Check for various possible CLI names
            for cli_name in ["gemini", "gemini-cli", "google-gemini"]:
                result = await asyncio.create_subprocess_exec(
                    cli_name, "--help",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    logger.info(f"Gemini CLI is available: {cli_name}")
                    return True
            
            logger.warning("Gemini CLI not found")
            return False
                
        except Exception as e:
            logger.warning(f"Error checking Gemini CLI availability: {e}")
            return False

    async def check_mcp_server_available(self) -> bool:
        """Check if MCP media server is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.mcp_server_url}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info("MCP media server is available")
                    return True
                else:
                    logger.warning(f"MCP media server returned status: {response.status_code}")
                    return False
        except Exception as e:
            logger.warning(f"MCP media server not available: {e}")
            return False

    async def _call_gemini_cli_models(self) -> List[str]:
        """Call Gemini CLI to list available models"""
        try:
            # Try to get models via MCP tools
            result = await self._call_gemini_cli_with_mcp(
                "List available models",
                "googleMediaV3.list_models"
            )
            
            if "models" in result:
                return result["models"]
            else:
                # Fallback to basic list
                return ["gemini-pro", "gemini-pro-vision", "veo-3", "imagen-3", "lyria"]
            
        except Exception as e:
            logger.error(f"Error calling Gemini CLI for models: {e}")
            raise

    async def list_available_models(self, db_session=None, user_id=None) -> List[str]:
        """List available models using Gemini CLI with MCP tools"""
        try:
            # Re-initialize with user settings if provided
            if db_session and user_id and not self.initialized:
                self._initialize_apis(db_session, user_id)
            
            # Try Gemini CLI with MCP first, then fallback to API
            try:
                models = await self._call_gemini_cli_models()
                return models
            except Exception as e:
                logger.warning(f"Gemini CLI models failed, falling back to API: {e}")
                # Fallback to API
                models = genai.list_models()
                model_names = [model.name for model in models]
                
                # Add media generation models
                model_names.extend(["veo-3", "imagen-3", "lyria"])
                
                return model_names
                
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            # Fallback to basic list
            return [
                "gemini-pro",
                "gemini-pro-vision", 
                "veo-3",
                "imagen-3",
                "lyria"
            ]
    
    async def get_model_info(self, model_name: str = "veo-3", db_session=None, user_id=None) -> Dict[str, Any]:
        """Get model information"""
        try:
            # Re-initialize with user settings if provided
            if db_session and user_id and not self.initialized:
                self._initialize_apis(db_session, user_id)
            
            if model_name == "veo-3":
                return {
                    "name": model_name,
                    "description": "Google's Veo 3 video generation model",
                    "capabilities": ["text-generation", "video-generation"],
                    "max_duration": 60,
                    "supported_aspect_ratios": ["16:9", "9:16", "1:1"],
                    "supported_formats": ["mp4", "webm"]
                }
            else:
                # Get info for other models
                models = genai.list_models()
                for model in models:
                    if model.name == model_name:
                        return {
                            "name": model.name,
                            "description": model.description,
                            "capabilities": model.supported_generation_methods,
                            "display_name": model.display_name
                        }
                
                # Fallback for unknown models
                return {
                    "name": model_name,
                    "description": "Unknown model",
                    "capabilities": ["text-generation"],
                    "max_duration": 10,
                    "supported_aspect_ratios": ["16:9", "9:16", "1:1"]
                }
                
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                "name": model_name,
                "description": "Model information unavailable",
                "capabilities": ["text-generation"],
                "max_duration": 10,
                "supported_aspect_ratios": ["16:9", "9:16", "1:1"]
            }

    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        resolution: str = "1024x1024",
        db_session=None,
        user_id=None
    ) -> Dict[str, Any]:
        """Generate image using Imagen via Gemini CLI with MCP tools"""
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            
            # Re-initialize with user settings if provided
            if db_session and user_id and not self.initialized:
                self._initialize_apis(db_session, user_id)
            
            # Try Gemini CLI with MCP first, then fallback to direct MCP server
            try:
                params = {
                    "prompt": prompt,
                    "style": style,
                    "resolution": resolution
                }
                
                result = await self._call_gemini_cli_with_mcp(
                    f"Generate an image: {prompt}",
                    "googleMediaV3.generate_image",
                    params
                )
                
                api_used = "gemini_cli_mcp"
                
            except Exception as e:
                logger.warning(f"Gemini CLI with MCP failed, trying direct MCP server: {e}")
                try:
                    result = await self._call_mcp_media_server("generate/image", {
                        "prompt": prompt,
                        "style": style,
                        "resolution": resolution
                    })
                    api_used = "mcp_direct"
                    
                except Exception as e2:
                    logger.warning(f"Direct MCP server failed: {e2}")
                    raise
            
            # Ensure we have image data
            if "image_data" not in result and "imageUrl" in result:
                # Download image from URL
                image_url = result["imageUrl"]
                async with httpx.AsyncClient() as client:
                    image_response = await client.get(image_url)
                    image_response.raise_for_status()
                    result["image_data"] = image_response.content
            
            return {
                "status": "success",
                "message": f"Image generated: {prompt}",
                "image_data": result.get("image_data", b""),
                "image_size": len(result.get("image_data", b"")),
                "resolution": resolution,
                "style": style,
                "api_used": api_used
            }
                    
        except Exception as e:
            logger.error(f"Error in generate_image: {e}")
            raise

    async def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        style: Optional[str] = None,
        db_session=None,
        user_id=None
    ) -> Dict[str, Any]:
        """Generate music using Lyria via Gemini CLI with MCP tools"""
        try:
            logger.info(f"Generating music with prompt: {prompt}")
            
            # Re-initialize with user settings if provided
            if db_session and user_id and not self.initialized:
                self._initialize_apis(db_session, user_id)
            
            # Try Gemini CLI with MCP first, then fallback to direct MCP server
            try:
                params = {
                    "prompt": prompt,
                    "duration": duration,
                    "style": style
                }
                
                result = await self._call_gemini_cli_with_mcp(
                    f"Generate music: {prompt}",
                    "googleMediaV3.generate_music",
                    params
                )
                
                api_used = "gemini_cli_mcp"
                
            except Exception as e:
                logger.warning(f"Gemini CLI with MCP failed, trying direct MCP server: {e}")
                try:
                    result = await self._call_mcp_media_server("generate/music", {
                        "prompt": prompt,
                        "duration": duration,
                        "style": style
                    })
                    api_used = "mcp_direct"
                    
                except Exception as e2:
                    logger.warning(f"Direct MCP server failed: {e2}")
                    raise
            
            # Ensure we have music data
            if "music_data" not in result and "musicUrl" in result:
                # Download music from URL
                music_url = result["musicUrl"]
                async with httpx.AsyncClient() as client:
                    music_response = await client.get(music_url)
                    music_response.raise_for_status()
                    result["music_data"] = music_response.content
            
            return {
                "status": "success",
                "message": f"Music generated: {prompt}",
                "music_data": result.get("music_data", b""),
                "music_size": len(result.get("music_data", b"")),
                "duration": duration,
                "style": style,
                "api_used": api_used
            }
                    
        except Exception as e:
            logger.error(f"Error in generate_music: {e}")
            raise

# Global service instance
gemini_service = GeminiCLIService()
