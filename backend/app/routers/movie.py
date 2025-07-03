from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, List, Dict, Any
import logging
from app.services.movie_maker import movie_maker_service
from app.models.movie_request import (
    MovieProjectRequest,
    MovieProjectResponse,
    MovieStatusResponse,
    ScriptUpdateRequest
)
import uuid
from datetime import datetime
import os

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/create", response_model=MovieProjectResponse)
async def create_movie_project(
    request: MovieProjectRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new movie project
    """
    try:
        project = await movie_maker_service.create_movie_project(request.dict())
        
        if request.auto_generate_script:
            background_tasks.add_task(
                generate_script_background,
                project["id"]
            )
        
        return MovieProjectResponse(
            project_id=project["id"],
            title=project["title"],
            status=project["status"],
            progress=project["progress"],
            created_at=project["created_at"],
            estimated_cost=movie_maker_service.get_estimated_cost(project)
        )
        
    except Exception as e:
        logger.error(f"Movie project creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Movie project creation failed: {str(e)}"
        )

async def generate_script_background(project_id: str):
    """Background task for script generation"""
    try:
        await movie_maker_service.generate_script(project_id)
        logger.info(f"Script generation completed for project {project_id}")
    except Exception as e:
        logger.error(f"Background script generation failed for project {project_id}: {str(e)}")

@router.post("/{project_id}/script")
async def generate_or_update_script(
    project_id: str,
    request: Optional[ScriptUpdateRequest] = None
):
    """
    Generate or update the script for a movie project
    """
    try:
        if request and request.script_content:
            project = movie_maker_service.update_script(project_id, request.script_content)
        else:
            project = await movie_maker_service.generate_script(project_id)
        
        return {
            "project_id": project["id"],
            "script": project["script"],
            "scenes": project["scenes"],
            "status": project["status"],
            "progress": project["progress"]
        }
        
    except Exception as e:
        logger.error(f"Script generation/update failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Script operation failed: {str(e)}"
        )

@router.post("/{project_id}/produce")
async def start_movie_production(
    project_id: str,
    background_tasks: BackgroundTasks
):
    """
    Start movie production process
    """
    try:
        project = await movie_maker_service.start_movie_production(project_id)
        
        return {
            "project_id": project["id"],
            "status": project["status"],
            "progress": project["progress"],
            "message": "Movie production started",
            "scenes_count": len(project.get("scenes", []))
        }
        
    except Exception as e:
        logger.error(f"Movie production start failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Movie production failed: {str(e)}"
        )

@router.get("/{project_id}/status", response_model=MovieStatusResponse)
async def get_movie_status(project_id: str):
    """
    Get the status of a movie project
    """
    try:
        project = movie_maker_service.get_project_status(project_id)
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail="Movie project not found"
            )
        
        return MovieStatusResponse(
            project_id=project["id"],
            title=project["title"],
            status=project["status"],
            progress=project["progress"],
            scenes_total=len(project.get("scenes", [])),
            scenes_completed=len([s for s in project.get("scenes", []) if s.get("status") == "completed"]),
            estimated_cost=movie_maker_service.get_estimated_cost(project),
            created_at=project["created_at"],
            error_message=project.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )

@router.get("/{project_id}/download")
async def download_movie(project_id: str):
    """
    Download the completed movie
    """
    try:
        project = movie_maker_service.get_project_status(project_id)
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail="Movie project not found"
            )
        
        if project["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail="Movie is not completed yet"
            )
        
        movie_path = project.get("final_movie_path")
        if not movie_path or not os.path.exists(movie_path):
            raise HTTPException(
                status_code=404,
                detail="Movie file not found"
            )
        
        def generate_movie_stream():
            with open(movie_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        
        return StreamingResponse(
            generate_movie_stream(),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={project['title'].replace(' ', '_')}.mp4"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Movie download failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Movie download failed: {str(e)}"
        )

@router.get("/projects")
async def list_movie_projects():
    """
    List all movie projects
    """
    try:
        projects = movie_maker_service.list_projects()
        
        return {
            "projects": [
                {
                    "project_id": project["id"],
                    "title": project["title"],
                    "status": project["status"],
                    "progress": project["progress"],
                    "created_at": project["created_at"],
                    "style": project["style"],
                    "preset": project["preset"],
                    "scenes_count": len(project.get("scenes", []))
                }
                for project in projects
            ]
        }
        
    except Exception as e:
        logger.error(f"Projects list failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Projects list failed: {str(e)}"
        )

@router.delete("/{project_id}")
async def delete_movie_project(project_id: str):
    """
    Delete a movie project
    """
    try:
        success = movie_maker_service.delete_project(project_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Movie project not found"
            )
        
        return {"message": "Movie project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project deletion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Project deletion failed: {str(e)}"
        )

@router.get("/styles")
async def get_movie_styles():
    """
    Get available movie styles
    """
    return {
        "styles": [
            {
                "id": "anime",
                "name": "🎨 Anime",
                "description": "Japanese animation style with vibrant colors"
            },
            {
                "id": "pixar",
                "name": "🎭 Pixar",
                "description": "3D animated movie style with character focus"
            },
            {
                "id": "wes-anderson",
                "name": "🎪 Wes Anderson",
                "description": "Symmetrical, pastel-colored cinematography"
            },
            {
                "id": "claymation",
                "name": "🏺 Claymation",
                "description": "Stop-motion clay animation texture"
            },
            {
                "id": "svankmajer",
                "name": "🎪 Švankmajer",
                "description": "Surreal, dark stop-motion style"
            },
            {
                "id": "advertisement",
                "name": "📺 Advertisement",
                "description": "Clean, commercial-style presentation"
            },
            {
                "id": "music-video",
                "name": "🎵 Music Video",
                "description": "Dynamic, rhythm-focused cinematography"
            },
            {
                "id": "cinematic",
                "name": "🎬 Cinematic",
                "description": "Hollywood blockbuster production value"
            },
            {
                "id": "documentary",
                "name": "📰 Documentary",
                "description": "Realistic, informational presentation"
            }
        ]
    }

@router.get("/presets")
async def get_movie_presets():
    """
    Get available movie presets
    """
    return {
        "presets": [
            {
                "id": "commercial",
                "name": "📺 Commercial",
                "clips": "3-5",
                "duration": "24-40s",
                "cost": "$0.30-1.25",
                "description": "Short promotional videos"
            },
            {
                "id": "short-film",
                "name": "🎬 Short Film",
                "clips": "5-10",
                "duration": "40-80s",
                "cost": "$0.50-2.50",
                "description": "Complete narrative stories"
            },
            {
                "id": "music-video",
                "name": "🎵 Music Video",
                "clips": "8-15",
                "duration": "64-120s",
                "cost": "$0.80-3.75",
                "description": "Dynamic visual music content"
            },
            {
                "id": "story",
                "name": "📖 Story",
                "clips": "10-20",
                "duration": "80-160s",
                "cost": "$1.00-5.00",
                "description": "Extended narrative content"
            },
            {
                "id": "feature",
                "name": "🎭 Feature",
                "clips": "20-50",
                "duration": "160-400s",
                "cost": "$2.00-12.50",
                "description": "Long-form movie content"
            }
        ]
    }

@router.get("/health")
async def movie_maker_health():
    """
    Health check for movie maker service
    """
    try:
        active_projects = len(movie_maker_service.list_projects())
        
        return {
            "status": "healthy",
            "service": "movie_maker",
            "active_projects": active_projects,
            "ffmpeg_available": True,  # Could add actual check
            "features": [
                "script_generation",
                "scene_continuity",
                "style_transfer",
                "video_concatenation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Movie maker health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "movie_maker"
        }
