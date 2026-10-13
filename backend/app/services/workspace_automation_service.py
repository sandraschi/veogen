"""
Workspace automation helpers (Docs/Slides to Flow import).
"""

from __future__ import annotations

import logging
import uuid
from typing import Dict

from sqlalchemy.orm import Session

from app.config import settings
from app.models.flow import FlowProject, FlowScene

logger = logging.getLogger(__name__)


class WorkspaceAutomationService:
    """Transforms Workspace briefs into Flow projects."""

    def __init__(self):
        self.enabled = settings.WORKSPACE_AUTOMATION_ENABLED

    def import_brief(self, db: Session, title: str, outline: Dict) -> FlowProject:
        if not self.enabled:
            raise RuntimeError("Workspace automation disabled")
        project_id = outline.get("projectId") or str(uuid.uuid4())
        project = FlowProject(
            id=project_id,
            title=title,
            status="draft",
            synopsis=outline.get("synopsis"),
            flow_metadata=outline,
        )
        db.add(project)
        for idx, beat in enumerate(outline.get("beats", [])):
            scene = FlowScene(
                id=beat.get("id") or f"{project_id}-scene-{idx}",
                project_id=project_id,
                title=beat.get("title", f"Scene {idx + 1}"),
                order_index=idx,
                prompt=beat.get("prompt"),
                duration_seconds=beat.get("duration", 10),
                style=beat.get("style", "cinematic"),
            )
            db.add(scene)
        db.commit()
        db.refresh(project)
        return project


workspace_automation_service = WorkspaceAutomationService()
