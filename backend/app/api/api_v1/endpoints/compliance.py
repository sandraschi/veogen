"""
Compliance Center endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.config import settings
from app.services.synthid_audit import synthid_audit_service

router = APIRouter()


@router.post("/synthid/audit")
async def run_synthid_audit(current_user=Depends(get_current_user)):
    if not settings.SYNTHID_DASHBOARD_ENABLED:
        raise HTTPException(status_code=503, detail="SynthID analytics disabled")
    result = synthid_audit_service.run()
    return result
