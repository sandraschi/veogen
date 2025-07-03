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

logger = logging.getLogger(__name__)

class GeminiCLIService:
    """Service for interacting with Google Gemini CLI for Veo video generation"""
    
    def __init__(self):
        self.cli_path = self._find_gemini_cli()
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        
    def _find_gemini_cli(self) -> str:
        """Find the Gemini CLI executable"""
        # Check if gemini-cli is in PATH
        try:
            result = subprocess.run(
                ["gemini-cli", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return "gemini-cli"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check common installation paths
        possible_paths = [
            "/usr/local/bin/gemini-cli",
            "/opt/google-cloud-sdk/bin/gemini-cli",
            "C:\\Program Files\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gemini-cli.exe",
            "C:\\Program Files (x86)\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gemini-cli.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default to assuming it's in PATH (will fail if not installed)
        return "gemini-cli"
    
    async def install_gemini_cli(self) -> bool:
        """Install Gemini CLI if not present"""
        try:
            # Check if already installed
            result = await asyncio.create_subprocess_exec(
                self.cli_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            if result.returncode == 0:
                logger.info("Gemini CLI already installed")
                return True
                
        except Exception as e:
            logger.warning(f"Gemini CLI not found: {e}")
        
        try:
            # Install via pip
            logger.info("Installing Gemini CLI...")
            result = await asyncio.create_subprocess_exec(
                "pip", "install", "google-generativeai[cli]",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info("Gemini CLI installed successfully")
                return True
            else:
                logger.error(f"Failed to install Gemini CLI: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error installing Gemini CLI: {e}")
            return False
    
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
        """Generate video using Gemini CLI and Veo model"""
        
        try:
            # Create temporary directory for output
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / f"generated_video.{output_format}"
                
                # Build command
                cmd = [
                    self.cli_path,
                    "generate-video",
                    "--prompt", prompt,
                    "--duration", str(duration),
                    "--aspect-ratio", aspect_ratio,
                    "--output", str(output_path),
                    "--model", "veo-3",
                    "--project", self.project_id,
                    "--location", self.location,
                    "--format", "json"
                ]
                
                if style:
                    cmd.extend(["--style", style])
                
                if seed is not None:
                    cmd.extend(["--seed", str(seed)])
                
                cmd.extend(["--temperature", str(temperature)])
                
                logger.info(f"Executing command: {' '.join(cmd)}")
                
                # Execute command
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=temp_dir
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    # Parse output
                    try:
                        result = json.loads(stdout.decode())
                        
                        # Read generated video file
                        if output_path.exists():
                            with open(output_path, 'rb') as f:
                                video_data = f.read()
                            
                            result['video_data'] = video_data
                            result['video_size'] = len(video_data)
                            
                        return result
                        
                    except json.JSONDecodeError:
                        # Fallback if JSON parsing fails
                        return {
                            "status": "success",
                            "message": stdout.decode(),
                            "video_path": str(output_path) if output_path.exists() else None
                        }
                else:
                    error_msg = stderr.decode()
                    logger.error(f"Gemini CLI error: {error_msg}")
                    raise Exception(f"Video generation failed: {error_msg}")
                    
        except Exception as e:
            logger.error(f"Error in generate_video: {e}")
            raise
    
    async def check_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Check the status of a video generation job"""
        try:
            cmd = [
                self.cli_path,
                "check-status",
                "--job-id", job_id,
                "--project", self.project_id,
                "--format", "json"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return json.loads(stdout.decode())
            else:
                error_msg = stderr.decode()
                logger.error(f"Status check error: {error_msg}")
                raise Exception(f"Status check failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            raise
    
    async def list_available_models(self) -> List[str]:
        """List available Veo models"""
        try:
            cmd = [
                self.cli_path,
                "list-models",
                "--project", self.project_id,
                "--format", "json"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                return [model['name'] for model in result.get('models', [])]
            else:
                logger.warning(f"Could not list models: {stderr.decode()}")
                return ["veo-3"]  # Default fallback
                
        except Exception as e:
            logger.warning(f"Error listing models: {e}")
            return ["veo-3"]  # Default fallback
    
    async def get_model_info(self, model_name: str = "veo-3") -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            cmd = [
                self.cli_path,
                "model-info",
                "--model", model_name,
                "--project", self.project_id,
                "--format", "json"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return json.loads(stdout.decode())
            else:
                logger.warning(f"Could not get model info: {stderr.decode()}")
                return {
                    "name": model_name,
                    "description": "Google Veo video generation model",
                    "max_duration": 60,
                    "supported_formats": ["mp4", "webm"],
                    "supported_ratios": ["16:9", "9:16", "1:1"]
                }
                
        except Exception as e:
            logger.warning(f"Error getting model info: {e}")
            return {
                "name": model_name,
                "description": "Google Veo video generation model",
                "max_duration": 60,
                "supported_formats": ["mp4", "webm"],
                "supported_ratios": ["16:9", "9:16", "1:1"]
            }

# Global instance
gemini_service = GeminiCLIService()
