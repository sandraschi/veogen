"""
Endpoints for Flow Studio orchestration.
"""

from typing import List, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models.flow import FlowProject, FlowScene
from app.services.flow_service import flow_service
from app.services.scene_describer_service import scene_describer_service

router = APIRouter()


class FlowScenePayload(BaseModel):
    """Slim scene representation for UI."""

    id: str
    title: str
    order_index: int
    duration_seconds: int
    status: str
    veo_job_id: Optional[str] = None
    prompt: Optional[str] = None
    style: Optional[str] = None
    aspect_ratio: Optional[str] = None
    poster_frame_url: Optional[str] = None
    checklist: dict = Field(default_factory=dict)
    captions: List[str] = Field(default_factory=list)

    @classmethod
    def from_model(cls, scene: FlowScene) -> "FlowScenePayload":
        return cls(
            id=scene.id,
            title=scene.title,
            order_index=scene.order_index,
            duration_seconds=scene.duration_seconds,
            status=scene.status,
            veo_job_id=scene.veo_job_id,
            prompt=scene.prompt,
            style=scene.style,
            aspect_ratio=scene.aspect_ratio,
            poster_frame_url=scene.poster_frame_url,
            checklist=scene.checklist or {},
            captions=[caption.caption for caption in scene.captions[:3]],
        )


class FlowIngredientPayload(BaseModel):
    id: str
    name: str
    ingredient_type: str
    description: Optional[str] = None

    @classmethod
    def from_model(cls, ingredient):
        return cls(
            id=ingredient.id,
            name=ingredient.name,
            ingredient_type=ingredient.ingredient_type,
            description=ingredient.description,
        )


class FlowProjectPayload(BaseModel):
    """Project representation for UI."""

    id: str
    title: str
    status: str
    synopsis: Optional[str] = None
    region: Optional[str] = None
    poster_frame_url: Optional[str] = None
    scenes: List[FlowScenePayload] = Field(default_factory=list)
    ingredients: List[FlowIngredientPayload] = Field(default_factory=list)

    @classmethod
    def from_model(cls, project: FlowProject) -> "FlowProjectPayload":
        return cls(
            id=project.id,
            title=project.title,
            status=project.status,
            synopsis=project.synopsis,
            region=project.region,
            poster_frame_url=project.poster_frame_url,
            scenes=[FlowScenePayload.from_model(scene) for scene in project.scenes],
            ingredients=[FlowIngredientPayload.from_model(ing) for ing in project.ingredients],
        )


@router.get("/projects", response_model=List[FlowProjectPayload])
async def list_flow_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return projects mirrored from Flow."""
    if not settings.FLOW_ENABLED:
        raise HTTPException(status_code=503, detail="Flow integration disabled")
    projects = flow_service.list_projects(db)
    return [FlowProjectPayload.from_model(p) for p in projects]


@router.get("/projects/{project_id}", response_model=FlowProjectPayload)
async def get_flow_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return single Flow project."""
    project = flow_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return FlowProjectPayload.from_model(project)


@router.post(
    "/projects/{project_id}/scenes/{scene_id}/launch",
    status_code=status.HTTP_202_ACCEPTED,
)
async def launch_flow_scene_render(
    project_id: str,
    scene_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Trigger Veo render for a Flow scene."""
    project = flow_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    scene = next((s for s in project.scenes if s.id == scene_id), None)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    result = await flow_service.trigger_scene_render(db, scene, str(current_user.id))
    return result


@router.post(
    "/projects/{project_id}/scenes/{scene_id}/describe",
    status_code=status.HTTP_201_CREATED,
)
async def describe_flow_scene(
    project_id: str,
    scene_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Generate an accessibility caption for a scene."""
    project = flow_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    scene = next((s for s in project.scenes if s.id == scene_id), None)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    if not settings.SCENE_DESCRIBER_ENABLED:
        raise HTTPException(status_code=503, detail="Scene describer disabled")
    caption = await scene_describer_service.describe_scene(db, scene)
    return {
        "scene_id": scene.id,
        "caption": caption.caption,
        "safety_labels": caption.safety_labels,
        "caption_id": caption.id,
    }


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def flow_webhook(
    request: Request,
    x_flow_signature: Optional[str] = Header(default=None),
):
    """Ingest Flow updates (public endpoint)."""
    if not settings.FLOW_ENABLED:
        raise HTTPException(status_code=503, detail="Flow integration disabled")
    body = await request.body()
    try:
        summary = flow_service.process_webhook(body, x_flow_signature)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return summary


class FlowSyncRequest(BaseModel):
    project_id: str


@router.post("/sync")
async def sync_flow_project(
    payload: FlowSyncRequest = Body(...),
    current_user=Depends(get_current_user),
):
    """Optional manual sync, requires Flow API access."""
    if not settings.FLOW_ENABLED:
        raise HTTPException(status_code=503, detail="Flow integration disabled")
    result = await flow_service.sync_project_with_flow(payload.project_id)
    return result

