"""
Nightly SynthID audit helper.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from sqlalchemy.orm import Session

from app.database import GenerationHistory, SessionLocal
from app.models.flow import FlowScene

logger = logging.getLogger(__name__)


class SynthIDAuditService:
    """Scans generation records for missing SynthID metadata."""

    def run(self) -> Dict[str, int]:
        db = SessionLocal()
        try:
            issues = self._scan_generations(db)
            issues += self._scan_flow_scenes(db)
            total = len(issues)
            if total:
                logger.warning("SynthID audit found %s issues", total)
            else:
                logger.info("SynthID audit clean")
            return {"issues": total}
        finally:
            db.close()

    def _scan_generations(self, db: Session) -> List[Dict]:
        rows = db.query(GenerationHistory).filter(GenerationHistory.generation_metadata.isnot(None)).all()
        issues = []
        for row in rows:
            metadata = row.generation_metadata or {}
            if not metadata.get("synthId"):
                issues.append(
                    {
                        "type": "generation",
                        "id": row.id,
                        "user_id": row.user_id,
                        "created_at": row.created_at.isoformat(),
                    }
                )
        return issues

    def _scan_flow_scenes(self, db: Session) -> List[Dict]:
        scenes = db.query(FlowScene).filter(FlowScene.status == "rendering").all()
        issues = []
        for scene in scenes:
            metadata = scene.flow_metadata or {}
            synthid = metadata.get("synthId") or scene.checklist.get("synthId") if scene.checklist else None
            if not synthid:
                issues.append(
                    {
                        "type": "flow_scene",
                        "scene_id": scene.id,
                        "project_id": scene.project_id,
                    }
                )
        return issues


synthid_audit_service = SynthIDAuditService()
