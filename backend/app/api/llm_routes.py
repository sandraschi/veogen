"""Local + cloud LLM provider routes (fleet contract, WEBAPP_SOTA_STANDARDS.md VI.10).

Mounted at /api (not /api/v1) so the paths match the fleet-wide contract:
GET /api/llm/providers, GET /api/llm/models, POST /api/llm/chat(+/stream),
GET /api/llm/onboarding, GET/POST /api/settings/llm, DELETE /api/settings/llm/key.
Keys are write-only: no response ever contains key material.
"""

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.services import llm_providers

router = APIRouter(prefix="/api", tags=["llm"])


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1, le=32768)


class LlmSettingsRequest(BaseModel):
    provider: str
    model: Optional[str] = None
    api_key: Optional[str] = None  # write-only


def _target(req: ChatRequest) -> tuple[str, str]:
    selection = llm_providers.get_selection()
    provider = req.provider or selection["provider"]
    model = req.model or (selection["model"] if provider == selection["provider"] else "")
    if not model:
        raise HTTPException(status_code=400, detail=f"No model given or selected for provider '{provider}'")
    return provider, model


@router.get("/llm/providers")
async def providers() -> List[Dict[str, Any]]:
    rows = llm_providers.public_provider_info()
    locals_ = [r["id"] for r in rows if r["kind"] == "local"]
    probes = await asyncio.gather(*(llm_providers.probe_local(p) for p in locals_))
    detected = {p: ok for p, (ok, _models) in zip(locals_, probes)}
    for row in rows:
        if row["kind"] == "local":
            row["detected"] = detected[row["id"]]
    return rows


@router.get("/llm/models")
async def models(provider: str = Query(...)) -> Dict[str, Any]:
    try:
        return await llm_providers.list_models(provider)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/llm/chat")
async def chat(req: ChatRequest, _user: User = Depends(get_current_user)) -> Dict[str, Any]:
    provider, model = _target(req)
    try:
        content = await llm_providers.chat_complete(
            provider, model, [m.model_dump() for m in req.messages], req.temperature, req.max_tokens
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"provider": provider, "model": model, "content": content}


@router.post("/llm/chat/stream")
async def chat_stream(req: ChatRequest, _user: User = Depends(get_current_user)) -> StreamingResponse:
    provider, model = _target(req)
    try:
        llm_providers._resolve(provider, model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    stream = llm_providers.chat_stream(
        provider, model, [m.model_dump() for m in req.messages], req.temperature, req.max_tokens
    )
    return StreamingResponse(stream, media_type="text/event-stream")


@router.get("/llm/onboarding")
async def onboarding() -> Dict[str, Any]:
    locals_ = [r["id"] for r in llm_providers.PROVIDERS if r["kind"] == "local"]
    probes = await asyncio.gather(*(llm_providers.probe_local(p) for p in locals_))
    return llm_providers.onboarding_state({p: ok for p, (ok, _m) in zip(locals_, probes)})


@router.get("/settings/llm")
async def get_llm_settings() -> Dict[str, Any]:
    selection = llm_providers.get_selection()
    return {
        **selection,
        "api_key_configured": llm_providers.is_configured(selection["provider"]),
        "keys_configured": llm_providers.keys_configured(),
    }


@router.post("/settings/llm")
async def save_llm_settings(req: LlmSettingsRequest, _user: User = Depends(get_current_user)) -> Dict[str, Any]:
    try:
        if req.api_key:
            llm_providers.save_key(req.provider, req.api_key)
        if req.model:
            llm_providers.save_selection(req.provider, req.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return await get_llm_settings()


@router.delete("/settings/llm/key")
async def delete_llm_key(provider: str = Query(...), _user: User = Depends(get_current_user)) -> Dict[str, Any]:
    try:
        removed = llm_providers.delete_key(provider)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"provider": provider, "removed": removed, "configured": llm_providers.is_configured(provider)}
