from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.routers import video, movie
from app.api.api_v1.endpoints import music, image, book, code, translation, predictor, documents, auth
from app.api.api_v1.endpoints import settings as settings_endpoints
# from app.api.api_v1.endpoints import chat
from app.middleware.metrics import PrometheusMetricsMiddleware, metrics_endpoint
import uvicorn

# Configure logging
from app.utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting VeoGen API...")
    logger.info("Initializing services...")
    
    # Initialize services here if needed
    try:
        # Test FFmpeg availability
        from app.services.ffmpeg import ffmpeg_service
        logger.info("FFmpeg service initialized")
        
        # Test Gemini CLI availability
        from app.services.gemini_cli import gemini_service
        logger.info("Gemini CLI service initialized")
        
        # Test Movie Maker service
        from app.services.movie_maker import movie_maker_service
        logger.info("Movie Maker service initialized")
        
    except Exception as e:
        logger.warning(f"Service initialization warning: {e}")
    
    yield
    
    logger.info("Shutting down VeoGen API...")
    # Cleanup here if needed
    try:
        # Cleanup temporary files
        ffmpeg_service.cleanup_temp_files()
        logger.info("Cleaned up temporary files")
    except Exception as e:
        logger.warning(f"Cleanup warning: {e}")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMetricsMiddleware)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly in production
)

# Include routers
app.include_router(
    video.router,
    prefix=f"{settings.API_V1_STR}/video",
    tags=["video"]
)

app.include_router(
    movie.router,
    prefix=f"{settings.API_V1_STR}/movie",
    tags=["movie"]
)

app.include_router(
    music.router,
    prefix=f"{settings.API_V1_STR}/music",
    tags=["music"]
)

app.include_router(
    image.router,
    prefix=f"{settings.API_V1_STR}/image",
    tags=["image"]
)

# New endpoints for enhanced frontend features
app.include_router(
    book.router,
    prefix=f"{settings.API_V1_STR}/book",
    tags=["book"]
)

app.include_router(
    code.router,
    prefix=f"{settings.API_V1_STR}/code",
    tags=["code"]
)

app.include_router(
    translation.router,
    prefix=f"{settings.API_V1_STR}/translation",
    tags=["translation"]
)

app.include_router(
    predictor.router,
    prefix=f"{settings.API_V1_STR}/predictor",
    tags=["predictor"]
)

app.include_router(
    documents.router,
    prefix=f"{settings.API_V1_STR}/documents",
    tags=["documents"]
)

# Authentication endpoints
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

# Settings endpoints
app.include_router(
    settings_endpoints.router,
    prefix=f"{settings.API_V1_STR}/settings",
    tags=["settings"]
)

# Chat endpoints
# app.include_router(
#     chat.router,
#     prefix=f"{settings.API_V1_STR}/chat",
#     tags=["chat"]
# )

# Add metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return await metrics_endpoint()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to VeoGen API",
        "version": settings.VERSION,
        "features": [
            "AI Video Generation",
            "Movie Maker with Continuity",
            "Book Maker Studio",
            "Code Assistant",
            "Universal Translator",
            "Future Predictor",
            "Document Management",
            "User Authentication & Management",
            "Secure API Key Storage",
            "Multiple Visual Styles",
            "Real-time Progress Tracking"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check core services
        health_status = {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "components": {}
        }
        
        # Check FFmpeg
        try:
            from app.services.ffmpeg import ffmpeg_service
            health_status["components"]["ffmpeg"] = "available"
        except Exception as e:
            health_status["components"]["ffmpeg"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check Gemini CLI
        try:
            from app.services.gemini_cli import gemini_service
            health_status["components"]["gemini_cli"] = "available"
        except Exception as e:
            health_status["components"]["gemini_cli"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check Movie Maker
        try:
            from app.services.movie_maker import movie_maker_service
            active_projects = len(movie_maker_service.list_projects())
            health_status["components"]["movie_maker"] = f"available ({active_projects} active projects)"
        except Exception as e:
            health_status["components"]["movie_maker"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check database
        try:
            from app.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            health_status["components"]["database"] = "available"
        except Exception as e:
            health_status["components"]["database"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "error": str(e)
        }

@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "endpoints": {
            "video": f"{settings.API_V1_STR}/video",
            "movie": f"{settings.API_V1_STR}/movie",
            "music": f"{settings.API_V1_STR}/music",
            "image": f"{settings.API_V1_STR}/image",
            "book": f"{settings.API_V1_STR}/book",
            "code": f"{settings.API_V1_STR}/code",
            "translation": f"{settings.API_V1_STR}/translation",
            "predictor": f"{settings.API_V1_STR}/predictor",
            "documents": f"{settings.API_V1_STR}/documents",
            "auth": f"{settings.API_V1_STR}/auth"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )
