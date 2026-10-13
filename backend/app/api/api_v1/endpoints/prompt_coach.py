"""
Prompt coach HTTP endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.config import settings
from app.services.prompt_coach_service import prompt_coach_service

router = APIRouter()


class PromptCoachStartResponse(BaseModel):
    session_id: str


class PromptCoachRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    prompt: str = Field(..., min_length=10, max_length=2000)


@router.post("/session", response_model=PromptCoachStartResponse, status_code=status.HTTP_201_CREATED)
async def start_prompt_coach_session(current_user=Depends(get_current_user)):
    if not settings.PROMPT_COACH_ENABLED:
        raise HTTPException(status_code=503, detail="Prompt coach disabled")
    session = prompt_coach_service.start_session(str(current_user.id))
    return PromptCoachStartResponse(**session)


@router.post("/critique")
async def critique_prompt(
    payload: PromptCoachRequest,
    current_user=Depends(get_current_user),
):
    if not settings.PROMPT_COACH_ENABLED:
        raise HTTPException(status_code=503, detail="Prompt coach disabled")
    try:
        result = await prompt_coach_service.critique_prompt(payload.session_id, payload.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result
