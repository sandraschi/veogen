import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from app.services.gemini_cli import gemini_service
from app.services.ffmpeg import ffmpeg_service
from app.config import settings

logger = logging.getLogger(__name__)

class MovieMakerService:
    """Service for creating complete movies with multiple scenes and continuity"""
    
    def __init__(self):
        self.active_projects = {}
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.temp_dir = Path(settings.TEMP_DIR)
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
    
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
            # Fallback to mock script if Gemini fails
            return self._generate_mock_script(prompt)
    
    def _generate_mock_script(self, prompt: str) -> str:
        """Generate a mock script for testing purposes"""
        return """TITLE: The Magic Forest Adventure

SYNOPSIS:
A young explorer discovers a magical forest where ordinary objects come to life, leading to an enchanting adventure filled with wonder and discovery.

STYLE NOTES:
Cinematic style with warm, golden lighting and sweeping camera movements. Focus on natural beauty and magical realism.

SCENES:
Scene 1: The Discovery
Duration: 8 seconds
Description: A young person walks through a misty forest path, sunlight filtering through ancient trees
Visual Prompt: Cinematic shot of person walking on forest path, golden hour lighting, mist between trees, magical atmosphere
Continuity: Opening establishing shot

Scene 2: The Magic Awakens
Duration: 8 seconds
Description: The explorer touches an old tree trunk and it begins to glow with soft, ethereal light
Visual Prompt: Close-up of hand touching glowing tree bark, magical particles floating, warm light emanating from wood
Continuity: Continues from forest path, focus shifts to magical elements

Scene 3: Forest Comes Alive
Duration: 8 seconds
Description: Various forest elements - flowers, leaves, small creatures - begin to move and dance with life
Visual Prompt: Wide shot of forest clearing with animated flowers swaying, leaves dancing in air, magical creatures appearing
Continuity: Magic spreads from the tree throughout the forest

Scene 4: The Journey Begins
Duration: 8 seconds
Description: The explorer follows a trail of glowing footprints deeper into the enchanted woodland
Visual Prompt: Following shot of person walking on glowing path, magical footprints lighting up ahead, mystical forest around
Continuity: Explorer moves deeper into the magical realm

Scene 5: Wonder and Discovery
Duration: 8 seconds
Description: The explorer reaches a clearing where floating lights dance around ancient stone circles
Visual Prompt: Aerial view of circular stone formation with floating orbs of light, person standing in center, mystical energy
Continuity: Journey leads to the heart of the forest's magic

PRODUCTION NOTES:
- Maintain warm, golden color palette throughout
- Ensure smooth transitions between scenes
- Focus on magical realism and wonder
- Use continuity frames to show progression through the forest"""

    def _parse_script_response(self, script_response: str, project: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the generated script into structured data"""
        try:
            scenes = []
            current_scene = None
            
            lines = script_response.split('\n')
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('Scene ') and ':' in line:
                    # Save previous scene if exists
                    if current_scene:
                        scenes.append(current_scene)
                    
                    # Start new scene
                    scene_title = line.split(':', 1)[1].strip()
                    current_scene = {
                        "id": len(scenes) + 1,
                        "title": scene_title,
                        "duration": 8,
                        "description": "",
                        "visual_prompt": "",
                        "continuity_notes": "",
                        "status": "pending"
                    }
                
                elif line.startswith('Description:') and current_scene:
                    current_scene["description"] = line.replace('Description:', '').strip()
                
                elif line.startswith('Visual Prompt:') and current_scene:
                    current_scene["visual_prompt"] = line.replace('Visual Prompt:', '').strip()
                
                elif line.startswith('Continuity:') and current_scene:
                    current_scene["continuity_notes"] = line.replace('Continuity:', '').strip()
            
            # Add the last scene
            if current_scene:
                scenes.append(current_scene)
            
            # Limit scenes to max_clips
            if len(scenes) > project["max_clips"]:
                scenes = scenes[:project["max_clips"]]
            
            return {
                "script": script_response,
                "scenes": scenes
            }
            
        except Exception as e:
            logger.error(f"Error parsing script response: {e}")
            # Return fallback scene structure
            return {
                "script": script_response,
                "scenes": [
                    {
                        "id": 1,
                        "title": "Opening Scene",
                        "duration": 8,
                        "description": project["concept"][:100] + "...",
                        "visual_prompt": f"{project['style']} style scene showing {project['concept']}",
                        "continuity_notes": "Opening scene",
                        "status": "pending"
                    }
                ]
            }
    
    async def start_movie_production(self, project_id: str) -> Dict[str, Any]:
        """Start the movie production process"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                raise Exception(f"Project not found: {project_id}")
            
            if not project.get("scenes"):
                raise Exception("No scenes available for production")
            
            project["status"] = "production"
            project["progress"] = 40
            
            # Start background task for video generation
            asyncio.create_task(self._produce_movie_background(project_id))
            
            logger.info(f"Started movie production for project {project_id}")
            return project
            
        except Exception as e:
            logger.error(f"Error starting movie production: {e}")
            raise
    
    async def _produce_movie_background(self, project_id: str):
        """Background task for movie production"""
        try:
            project = self.active_projects[project_id]
            scenes = project["scenes"]
            generated_clips = []
            
            for i, scene in enumerate(scenes):
                # Update progress
                progress = 40 + (i / len(scenes)) * 50
                project["progress"] = int(progress)
                
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
        """Generate video for a single scene"""
        try:
            # Prepare the prompt for video generation
            video_prompt = f"{project['style']} style: {scene['visual_prompt']}"
            
            # Add continuity reference if available
            continuity_frame = None
            if scene_index > 0 and project["generated_clips"]:
                prev_clip = project["generated_clips"][-1]
                continuity_frame = prev_clip.get("continuity_frame")
            
            # Generate video using the existing video generation service
            video_request = {
                "prompt": video_prompt,
                "style": project["style"],
                "duration": scene["duration"],
                "aspect_ratio": "16:9",
                "temperature": 0.7,
                "reference_image": continuity_frame
            }
            
            # Use gemini_service to generate the video
            result = await gemini_service.generate_video(**video_request)
            
            if result and "video_data" in result:
                # Save the video to a file
                clip_filename = f"{project['id']}_scene_{scene['id']}.mp4"
                clip_path = self.temp_dir / clip_filename
                
                with open(clip_path, 'wb') as f:
                    f.write(result["video_data"])
                
                logger.info(f"Generated video for scene {scene['id']}: {clip_path}")
                return str(clip_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating video for scene {scene['id']}: {e}")
            return None
    
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
