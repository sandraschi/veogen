"""
Image Generation API Endpoints backed by Gemini CLI Imagen calls.
"""

import base64
import logging
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.database import User
from app.schemas.image import (
    ImageGeneration,
    ImageGenerationResponse,
    ImageQuality,
    ImageStyle,
)
from app.services.gemini_cli import gemini_service
from app.services.image_service import image_service

logger = logging.getLogger(__name__)

router = APIRouter()


ASPECT_RATIO_TO_RESOLUTION: Dict[str, str] = {
    "1:1": "1024x1024",
    "16:9": "1344x768",
    "9:16": "768x1344",
    "4:3": "1152x896",
    "3:2": "1216x832",
}


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Image description for Nano Banana Pro")
    aspect_ratio: str = Field("1:1", description="Aspect ratio hint (e.g. 1:1, 16:9)")
    style: Optional[str] = Field(None, description="Optional artistic style label")
    num_images: int = Field(1, ge=1, le=4, description="Number of images to generate")
    creativity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Creativity level mapped to temperature")
    reference_image: Optional[str] = Field(None, description="Base64 encoded image for editing or OCR")
    mode: Optional[str] = Field("generate", description="Mode: 'generate', 'edit', or 'ocr'")


class GeneratedImage(BaseModel):
    url: str
    metadata: Dict[str, Optional[str]]


class ImageGenerateResponse(BaseModel):
    status: str
    images: List[GeneratedImage]
    message: Optional[str] = None
    api_used: Optional[str] = None


class ImageStatusResponse(BaseModel):
    image_id: str
    status: str
    prompt: str
    aspect_ratio: str
    num_images: int
    style: str
    image_urls: Optional[List[str]] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_image(request: ImageGenerationRequest, current_user: User = Depends(get_current_user)):
    """Generate, edit, or OCR an image using Nano Banana Pro (Gemini 3 Pro Image)."""
    resolution = ASPECT_RATIO_TO_RESOLUTION.get(request.aspect_ratio, "1024x1024")

    if request.num_images > 1:
        logger.info(
            "Multiple image request (%s) received; returning single image for now.",
            request.num_images,
        )

    try:
        result = await gemini_service.generate_image(
            prompt=request.prompt,
            style=request.style,
            resolution=resolution,
            reference_image=request.reference_image,
            mode=request.mode or "generate",
            db_session=None,
            user_id=str(current_user.id),
        )
    except Exception as exc:
        logger.error("Gemini Imagen generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Image generation failed due to upstream error.",
        ) from exc

    if result.get("status") != "success":
        message = result.get("message") or "Image generation failed."
        logger.error("Gemini Imagen returned error: %s", message)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)

    image_bytes = result.get("image_data", b"")
    if not image_bytes:
        logger.error("Gemini Imagen returned no image bytes.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image generation did not return image data.",
        )

    data_url = "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii")

    image_metadata = {
        "prompt": request.prompt,
        "style": request.style or "default",
        "aspect_ratio": request.aspect_ratio,
        "resolution": resolution,
        "api_used": result.get("api_used"),
    }

    return ImageGenerateResponse(
        status="success",
        images=[GeneratedImage(url=data_url, metadata=image_metadata)],
        message=result.get("message"),
        api_used=result.get("api_used"),
    )


@router.get("/status/{image_id}", response_model=ImageStatusResponse)
async def get_image_status(image_id: str, current_user: User = Depends(get_current_user)):
    """Get the status of an image generation"""
    try:
        result = await image_service.get_image_status(image_id)

        if not result:
            raise HTTPException(status_code=404, detail="Image not found")

        return ImageStatusResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get image status: {str(e)}")


@router.get("/list", response_model=List[ImageStatusResponse])
async def list_user_images(limit: int = 50, current_user: User = Depends(get_current_user)):
    """Get all images for the current user"""
    try:
        images = await image_service.get_user_images(current_user.id, limit)
        return [ImageStatusResponse(**image) for image in images]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user images: {str(e)}")


@router.delete("/{image_id}")
async def delete_image(image_id: str, current_user: User = Depends(get_current_user)):
    """Delete an image generation"""
    try:
        success = await image_service.delete_image(image_id, current_user.id)

        if not success:
            raise HTTPException(status_code=404, detail="Image not found")

        return {"message": "Image deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")


@router.get("/{image_id}", response_model=ImageGeneration)
async def get_image_generation(
    image_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get image generation status and details"""
    image_gen = await image_service.get_image_generation(db, image_id, current_user)

    if not image_gen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image generation not found")

    return image_gen


@router.get("/", response_model=List[ImageGeneration])
async def list_image_generations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    style: Optional[ImageStyle] = None,
    quality: Optional[ImageQuality] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's image generations with optional filtering"""
    image_gens = await image_service.list_user_images(
        db, current_user, skip=skip, limit=limit, style=style, quality=quality, status=status
    )
    return image_gens


@router.post("/{image_id}/regenerate", response_model=ImageGenerationResponse)
async def regenerate_image(
    image_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Regenerate a failed image generation"""
    image_gen = await image_service.get_image_generation(db, image_id, current_user)

    if not image_gen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image generation not found")

    if image_gen.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can only regenerate failed image generations"
        )

    await image_service.regenerate_image(db, image_id)

    return ImageGenerationResponse(job_id=image_gen.id, status="pending", message="Image regeneration started")


@router.get("/styles/", response_model=List[str])
async def get_image_styles():
    """Get available image styles"""
    return [style.value for style in ImageStyle]


@router.get("/qualities/", response_model=List[str])
async def get_image_qualities():
    """Get available image quality levels"""
    return [quality.value for quality in ImageQuality]


@router.get("/{image_id}/download")
async def download_image(
    image_id: UUID,
    format: str = Query("png", pattern="^(png|jpg|jpeg|webp)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download generated image in specified format"""
    image_gen = await image_service.get_image_generation(db, image_id, current_user)

    if not image_gen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image generation not found")

    if image_gen.status != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image generation not completed")

    download_url = await image_service.get_download_url(image_gen, format)

    return {"download_url": download_url}


@router.post("/{image_id}/variations", response_model=ImageGenerationResponse)
async def create_image_variations(
    image_id: UUID,
    variation_count: int = Query(4, ge=1, le=8),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create variations of an existing image"""
    original_image = await image_service.get_image_generation(db, image_id, current_user)

    if not original_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Original image not found")

    if original_image.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original image must be completed before creating variations",
        )

    variations = await image_service.create_variations(db, original_image, variation_count, current_user)

    return ImageGenerationResponse(
        job_id=variations[0].id, status=variations[0].status, message=f"Creating {variation_count} image variations"
    )
