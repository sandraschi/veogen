import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.llm_routes import router as llm_router
from app.api.router import api_router
from app.config import settings
from app.mcp_server import mcp_http_app

logger = logging.getLogger(__name__)
_started_at = time.time()

# MCP streamable HTTP app - created before FastAPI so its lifespan can be
# merged into the parent app (FastMCP requires the parent to run its
# session-manager task group via lifespan_context).
mcp_web_app = mcp_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Combined lifespan: database init + FastMCP session manager."""
    from app.database import init_db

    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error("Database initialization failed: %s", e)

    try:
        async with mcp_web_app.router.lifespan_context(app):
            yield
    finally:
        logger.info("Shutting down %s", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The full v1 API surface (auth, chat, image, music, video, settings, ...)
app.include_router(api_router)
app.include_router(llm_router)

# MCP streamable HTTP surface (Phase 4 fleet integration)
app.mount("/mcp", mcp_web_app)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "uptime_seconds": int(time.time() - _started_at),
    }


@app.get("/api/v1/diagnostics")
async def diagnostics():
    """Fleet-standard diagnostics: status, tools, system info (CUA smoke)."""
    tool_routes = sorted(p for p in app.openapi()["paths"] if p.startswith("/api/v1") and p.count("/") >= 3)
    system = {}
    try:
        import platform

        import psutil

        system = {
            "windows": platform.system() == "Windows",
            "platform": platform.system(),
            "python": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "memory_percent": psutil.virtual_memory().percent,
        }
    except Exception:
        system = {"windows": True}
    return {
        "status": "ok",
        "server": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "uptime_seconds": int(time.time() - _started_at),
        "tool_count": len(tool_routes),
        "tools": [{"path": p} for p in tool_routes],
        "system": system,
        "errors": [],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
