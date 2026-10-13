"""
Workspace automation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.services.workspace_automation_service import workspace_automation_service

router = APIRouter()


class BriefImportRequest(BaseModel):
    title: str
    outline: dict = Field(default_factory=dict)


@router.post("/flow/import")
async def import_workspace_brief(
    payload: BriefImportRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not settings.WORKSPACE_AUTOMATION_ENABLED:
        raise HTTPException(status_code=503, detail="Workspace automations disabled")
    project = workspace_automation_service.import_brief(db, payload.title, payload.outline)
    return {"project_id": project.id}
