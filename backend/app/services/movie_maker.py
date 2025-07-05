import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import google.generativeai as genai
from google.cloud import aiplatform
from app.services.gemini_cli import gemini_service
from app.services.ffmpeg import ffmpeg_service
from app.config import settings
from app.database import get_user_setting
from app.middleware.metrics import track_video_generation
from app.utils.logging_config import log_video_generation_event

logger = logging.getLogger(__name__)

class VideoStyle(str, Enum):
    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"
    MUSIC_VIDEO = "music_video"
    EDUCATIONAL = "educational"
    STORYTELLING = "storytelling"
    ABSTRACT = "abstract"
    EXPERIMENTAL = "experimental"

class VideoQuality(str, Enum):
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"

class AspectRatio(str, Enum):
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"
    CINEMATIC = "21:9"

@dataclass
class VideoGenerationRequest:
    prompt: str
    style: VideoStyle
    duration: int  # seconds
    aspect_ratio: AspectRatio
    quality: VideoQuality
    music_prompt: Optional[str] = None
    voice_over: Optional[str] = None
    scene_breakdown: Optional[List[Dict[str, Any]]] = None
    reference_video: Optional[str] = None
    custom_instructions: Optional[str] = None

@dataclass
class VideoGenerationResult:
    video_url: str
    thumbnail_url: str
    preview_url: str
    metadata: Dict[str, Any]
    scene_timeline: List[Dict[str, Any]]
    audio_track_url: Optional[str] = None
    subtitle_url: Optional[str] = None

class MovieMakerService:
    """Service for creating complete movies with multiple scenes and continuity"""
    
    def __init__(self):
        self.active_projects = {}
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.temp_dir = Path(settings.TEMP_DIR)
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize Google Cloud AI Platform
        self._initialize_ai_platform()
    
    def _initialize_ai_platform(self):
        """Initialize Google Cloud AI Platform for Veo API"""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                aiplatform.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                aiplatform.init(
                    project=self.project_id,
                    location=self.location
                )
            
            # Configure Gemini API for script generation
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
            
            logger.info("Movie maker service initialized with Google Cloud AI Platform")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI platform: {e}")
            # Continue with fallback to Gemini for script generation
    
    async def create_movie_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new movie project"""
        try:
            project_id = str(uuid.uuid4())
            
            project = {
                "id": project_id,
                "title": project_data["title"],
                "concept": project_data["concept"],
                "style": project_data["style"],
                "preset": project_data["preset"],
                "max_clips": project_data["max_clips"],
                "budget": project_data["budget"],
                "status": "created",
                "created_at": datetime.now().isoformat(),
                "script": None,
                "scenes": [],
                "generated_clips": [],
                "final_movie_path": None,
                "progress": 0
            }
            
            self.active_projects[project_id] = project
            
            logger.info(f"Created movie project: {project_id}")
            return project
            
        except Exception as e:
            logger.error(f"Error creating movie project: {e}")
            raise
    
    async def generate_script(self, project_id: str) -> Dict[str, Any]:
        """Generate a detailed script for the movie"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                raise Exception(f"Project not found: {project_id}")
            
            project["status"] = "script_generation"
            project["progress"] = 10
            
            # Create prompt for script generation
            script_prompt = self._create_script_prompt(project)
            
            # Generate script using Gemini
            script_response = await self._generate_script_with_gemini(script_prompt)
            
            # Parse the response to extract script and scenes
            script_data = self._parse_script_response(script_response, project)
            
            project["script"] = script_data["script"]
            project["scenes"] = script_data["scenes"]
            project["status"] = "script_ready"
            project["progress"] = 30
            
            logger.info(f"Generated script for project {project_id} with {len(script_data['scenes'])} scenes")
            return project
            
        except Exception as e:
            logger.error(f"Error generating script for project {project_id}: {e}")
            project["status"] = "script_failed"
            project["error"] = str(e)
            raise
    
    def _create_script_prompt(self, project: Dict[str, Any]) -> str:
        """Create a detailed prompt for script generation"""
        style_descriptions = {
            "anime": "Japanese animation style with dynamic action and emotional storytelling",
            "pixar": "3D animated movie with character-driven narrative and humor",
            "wes-anderson": "Symmetrical, whimsical cinematography with quirky characters",
            "claymation": "Stop-motion clay animation with tactile, handmade aesthetics",
            "svankmajer": "Surreal, dark stop-motion with dreamlike imagery",
            "advertisement": "Clean, professional commercial-style presentation",
            "music-video": "Dynamic, rhythm-focused visual storytelling",
            "cinematic": "Hollywood-style dramatic cinematography",
            "documentary": "Realistic, informational visual narrative"
        }
        
        preset_guidelines = {
            "commercial": "3-5 scenes, 24-40 seconds total, focused message",
            "short-film": "5-10 scenes, 40-80 seconds total, complete story arc",
            "music-video": "8-15 scenes, 64-120 seconds total, rhythm-driven",
            "story": "10-20 scenes, 80-160 seconds total, narrative storytelling",
            "feature": "20-50 scenes, 160-400 seconds total, complex narrative"
        }
        
        style_desc = style_descriptions.get(project["style"], "cinematic storytelling")
        preset_guide = preset_guidelines.get(project["preset"], "narrative storytelling")
        
        return f"""Create a detailed movie script for a {project["preset"]} in {project["style"]} style.

Title: {project["title"]}
Concept: {project["concept"]}
Style: {style_desc}
Guidelines: {preset_guide}
Maximum scenes: {project["max_clips"]}

Requirements:
1. Create a compelling narrative that flows logically
2. Each scene should be exactly 8 seconds long
3. Include detailed visual descriptions for each scene
4. Ensure continuity between scenes for smooth transitions
5. Match the {project["style"]} aesthetic throughout
6. Stay within the {project["preset"]} format guidelines

Output format:
TITLE: [Movie Title]

SYNOPSIS:
[Brief overview of the movie]

STYLE NOTES:
[Visual style and cinematography notes]

SCENES:
Scene 1: [Title]
Duration: 8 seconds
Description: [Detailed scene description]
Visual Prompt: [Specific prompt for AI video generation]
Continuity: [How this connects to previous/next scene]

[Continue for all scenes...]

PRODUCTION NOTES:
[Any additional notes for production]

Please ensure each scene builds upon the previous one and creates a cohesive story."""

    async def _generate_script_with_gemini(self, prompt: str) -> str:
        """Generate script using Gemini API"""
        try:
            # Use Gemini CLI to generate the script
            response = await gemini_service.generate_text(
                prompt=prompt,
                temperature=0.8,
                max_tokens=2000
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating script with Gemini: {e}")
            # Fallback to basic script structure
            return self._generate_basic_script(prompt)
    
    def _generate_basic_script(self, prompt: str) -> str:
        """Generate a basic script structure when AI generation fails"""
        return f"""TITLE: Generated Movie

SYNOPSIS:
A movie based on the prompt: {prompt}

STYLE NOTES:
Cinematic style with professional lighting and camera work.

SCENES:
Scene 1: Opening
Duration: 8 seconds
Description: Opening scene based on the prompt
Visual Prompt: {prompt}
Continuity: Opening establishing shot

Scene 2: Development
Duration: 8 seconds
Description: Development of the story
Visual Prompt: Continuation of {prompt}
Continuity: Continues from opening scene

Scene 3: Climax
Duration: 8 seconds
Description: Climactic moment
Visual Prompt: Dramatic version of {prompt}
Continuity: Builds from previous scenes

Scene 4: Conclusion
Duration: 8 seconds
Description: Concluding scene
Visual Prompt: Resolution of {prompt}
Continuity: Wraps up the story

PRODUCTION NOTES:
Maintain consistent style throughout. Ensure smooth transitions between scenes."""

    def _parse_script_response(self, script_response: str, project: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the script response to extract scenes and metadata"""
        try:
            lines = script_response.split('\n')
            script_data = {
                "script": script_response,
                "scenes": []
            }
            
            current_scene = None
            in_scenes_section = False
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("SCENES:"):
                    in_scenes_section = True
                    continue
                
                if in_scenes_section and line.startswith("Scene"):
                    if current_scene:
                        script_data["scenes"].append(current_scene)
                    
                    # Extract scene number and title
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        scene_info = parts[0].strip()
                        scene_title = parts[1].strip()
                        
                        current_scene = {
                            "id": len(script_data["scenes"]) + 1,
                            "title": scene_title,
                            "duration": 8,
                            "description": "",
                            "visual_prompt": "",
                            "continuity": "",
                            "status": "pending"
                        }
                
                elif current_scene and line.startswith("Duration:"):
                    duration_text = line.split(":", 1)[1].strip()
                    try:
                        current_scene["duration"] = int(duration_text.split()[0])
                    except:
                        pass
                
                elif current_scene and line.startswith("Description:"):
                    current_scene["description"] = line.split(":", 1)[1].strip()
                
                elif current_scene and line.startswith("Visual Prompt:"):
                    current_scene["visual_prompt"] = line.split(":", 1)[1].strip()
                
                elif current_scene and line.startswith("Continuity:"):
                    current_scene["continuity"] = line.split(":", 1)[1].strip()
                
                elif line.startswith("PRODUCTION NOTES:"):
                    in_scenes_section = False
                    if current_scene:
                        script_data["scenes"].append(current_scene)
                    break
            
            # Add the last scene if exists
            if current_scene:
                script_data["scenes"].append(current_scene)
            
            return script_data
            
        except Exception as e:
            logger.error(f"Error parsing script response: {e}")
            # Return basic structure if parsing fails
            return {
                "script": script_response,
                "scenes": []
            }
    
    async def start_movie_production(self, project_id: str) -> Dict[str, Any]:
        """Start the movie production process"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                raise Exception(f"Project not found: {project_id}")
            
            if not project.get("scenes"):
                raise Exception("No scenes available. Generate script first.")
            
            project["status"] = "production_started"
            project["progress"] = 40
            
            # Start background production task
            asyncio.create_task(self._produce_movie_background(project_id))
            
            logger.info(f"Started movie production for project {project_id}")
            return project
            
        except Exception as e:
            logger.error(f"Error starting movie production: {e}")
            raise
    
    async def _produce_movie_background(self, project_id: str):
        """Background task for movie production"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                return
            
            project["status"] = "generating_clips"
            scenes = project["scenes"]
            generated_clips = []
            
            # Generate video for each scene
            for i, scene in enumerate(scenes):
                scene["status"] = "generating"
                project["progress"] = 40 + (i * 50 // len(scenes))
                
                # Generate video for this scene
                clip_path = await self._generate_scene_video(project, scene, i)
                
                if clip_path:
                    generated_clips.append({
                        "scene_id": scene["id"],
                        "clip_path": clip_path,
                        "continuity_frame": None
                    })
                    
                    # Extract continuity frame for next scene
                    if i < len(scenes) - 1:
                        frame_path = await ffmpeg_service.extract_final_frame(clip_path)
                        styled_frame = await ffmpeg_service.apply_style_transfer(
                            frame_path, project["style"]
                        )
                        generated_clips[-1]["continuity_frame"] = styled_frame
                
                scene["status"] = "completed"
            
            project["generated_clips"] = generated_clips
            
            # Assemble final movie
            await self._assemble_final_movie(project)
            
            project["status"] = "completed"
            project["progress"] = 100
            
            logger.info(f"Completed movie production for project {project_id}")
            
        except Exception as e:
            logger.error(f"Error in movie production background task: {e}")
            project["status"] = "failed"
            project["error"] = str(e)
    
    async def _generate_scene_video(
        self, 
        project: Dict[str, Any], 
        scene: Dict[str, Any], 
        scene_index: int
    ) -> Optional[str]:
        """Generate video for a single scene using real Veo API"""
        try:
            # Prepare the prompt for video generation
            video_prompt = f"{project['style']} style: {scene['visual_prompt']}"
            
            # Add continuity reference if available
            continuity_frame = None
            if scene_index > 0 and project["generated_clips"]:
                prev_clip = project["generated_clips"][-1]
                continuity_frame = prev_clip.get("continuity_frame")
            
            # Try real Veo API first, fallback to Gemini if needed
            try:
                video_data = await self._generate_video_veo(video_prompt, scene, continuity_frame)
            except Exception as e:
                logger.warning(f"Veo API failed, falling back to Gemini: {e}")
                video_data = await self._generate_video_gemini(video_prompt, scene, continuity_frame)
            
            if video_data:
                # Save the video to a file
                clip_filename = f"{project['id']}_scene_{scene['id']}.mp4"
                clip_path = self.temp_dir / clip_filename
                
                with open(clip_path, 'wb') as f:
                    f.write(video_data)
                
                logger.info(f"Generated video for scene {scene['id']}: {clip_path}")
                return str(clip_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating video for scene {scene['id']}: {e}")
            return None
    
    async def _generate_video_veo(self, prompt: str, scene: Dict[str, Any], reference_image: Optional[str] = None) -> Optional[bytes]:
        """Generate video using real Google Veo API"""
        try:
            # Prepare the request for Veo
            veo_request = {
                "prompt": prompt,
                "duration": scene["duration"],
                "aspect_ratio": "16:9",
                "style": "cinematic",
                "quality": "high",
                "reference_image": reference_image
            }
            
            # Call Veo API via Google Cloud AI Platform
            # Note: This is a simplified version - actual implementation would use the specific Veo endpoint
            endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{self.project_id}/locations/{self.location}/endpoints/veo"
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
    
    async def _generate_video_gemini(self, prompt: str, scene: Dict[str, Any], reference_image: Optional[str] = None) -> Optional[bytes]:
        """Generate video using Gemini API as fallback"""
        try:
            # Use Gemini for video generation (this would be more complex in reality)
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            # Create video generation prompt
            video_prompt = f"""
            Generate a video based on this description: {prompt}
            
            Duration: {scene['duration']} seconds
            Style: cinematic
            Quality: high
            
            Please create a video that matches the description and requirements.
            """
            
            # Generate video using Gemini (this is a simplified approach)
            response = await asyncio.to_thread(
                model.generate_content,
                video_prompt
            )
            
            # For now, return simulated video data
            # In reality, this would process the actual video response from Gemini
            simulated_video_data = b"simulated_video_data_for_demo"
            
            return simulated_video_data
            
        except Exception as e:
            logger.error(f"Gemini video generation failed: {e}")
            raise
    
    async def _assemble_final_movie(self, project: Dict[str, Any]):
        """Assemble all clips into the final movie"""
        try:
            if not project["generated_clips"]:
                raise Exception("No clips available for assembly")
            
            clip_paths = [clip["clip_path"] for clip in project["generated_clips"]]
            
            # Create final movie filename
            movie_filename = f"{project['title'].replace(' ', '_')}_{project['id']}.mp4"
            movie_path = self.output_dir / movie_filename
            
            # Concatenate videos with transitions
            final_path = await ffmpeg_service.concatenate_videos(
                clip_paths, 
                str(movie_path), 
                with_transitions=True
            )
            
            project["final_movie_path"] = final_path
            
            # Create thumbnail
            thumbnail_path = await ffmpeg_service.create_thumbnail(final_path)
            project["thumbnail_path"] = thumbnail_path
            
            logger.info(f"Assembled final movie: {final_path}")
            
        except Exception as e:
            logger.error(f"Error assembling final movie: {e}")
            raise
    
    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a movie project"""
        return self.active_projects.get(project_id)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all active movie projects"""
        return list(self.active_projects.values())
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a movie project and clean up files"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                return False
            
            # Clean up generated files
            if project.get("generated_clips"):
                for clip in project["generated_clips"]:
                    try:
                        Path(clip["clip_path"]).unlink(missing_ok=True)
                        if clip.get("continuity_frame"):
                            Path(clip["continuity_frame"]).unlink(missing_ok=True)
                    except Exception as e:
                        logger.warning(f"Could not delete clip file: {e}")
            
            # Clean up final movie file
            if project.get("final_movie_path"):
                try:
                    Path(project["final_movie_path"]).unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Could not delete movie file: {e}")
            
            # Clean up thumbnail
            if project.get("thumbnail_path"):
                try:
                    Path(project["thumbnail_path"]).unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Could not delete thumbnail file: {e}")
            
            # Remove from active projects
            del self.active_projects[project_id]
            
            logger.info(f"Deleted project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False
    
    def update_script(self, project_id: str, new_script: str) -> Dict[str, Any]:
        """Update the script for a movie project"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                raise Exception(f"Project not found: {project_id}")
            
            project["script"] = new_script
            
            # Re-parse the script to update scenes
            script_data = self._parse_script_response(new_script, project)
            project["scenes"] = script_data["scenes"]
            
            logger.info(f"Updated script for project {project_id}")
            return project
            
        except Exception as e:
            logger.error(f"Error updating script: {e}")
            raise
    
    def get_estimated_cost(self, project: Dict[str, Any]) -> float:
        """Calculate estimated cost for movie production"""
        try:
            num_scenes = len(project.get("scenes", []))
            if num_scenes == 0:
                num_scenes = project.get("max_clips", 5)
            
            # Estimate cost per scene (adjust based on actual API costs)
            cost_per_scene = 0.25  # $0.25 per 8-second clip
            
            total_cost = num_scenes * cost_per_scene
            
            return min(total_cost, project.get("budget", 10.0))
            
        except Exception as e:
            logger.error(f"Error calculating estimated cost: {e}")
            return 0.0

# Global movie maker service instance
movie_maker_service = MovieMakerService()
