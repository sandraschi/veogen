from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.config import settings

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events for v3.1 Industrial Stack"""
    logger.info(f"Starting {settings.PROJECT_NAME} (v{settings.VERSION})...")
    logger.info(f"Ports: Backend={settings.PORT}, Frontend={settings.FRONTEND_PORT}")
    
    # Initialize Core Services
    try:
        from app.database import init_db
        # init_db() # Keeping it commented for now as I might need to adjust models
        logger.info("Database initialized (schema verification pending)")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    yield
    
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "sota": "April 2026 (v3.1)",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": "2026-04-18T01:11:00Z"
    }

# Placeholder for the "Big Four" routers
# These will be implemented in Step 3
@app.get("/api/v1/info")
async def api_info():
    return {
        "message": "VeoGen Industrial API v3.1",
        "endpoints": {
            "chat": "/api/v1/chat",
            "video": "/api/v1/video",
            "music": "/api/v1/music",
            "image": "/api/v1/image"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
