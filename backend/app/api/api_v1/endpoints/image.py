# Image Generation API Endpoints

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.image import (
    ImageGeneration,
    ImageGenerationCreate,
    ImageGenerationResponse,
    ImageStyle,
    ImageQuality
)
from app.services.image_service_layer import image_service

router = APIRouter()

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(
    image_data: ImageGenerationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate image using Google Imagen AI
    
    - **prompt**: Description of the image to generate (5-500 chars)
    - **style**: Image style (photorealistic, artistic, illustration, etc.)
    - **aspect_ratio**: Image dimensions (1:1, 16:9, 9:16, 4:3)
    - **quality**: Image quality (standard, high, ultra)
    """
    try:
        image_gen = await image_service.create_image_generation(
            db, image_data, current_user
        )
        
        return ImageGenerationResponse(
            job_id=image_gen.id,
            status=image_gen.status,
            message="Image generation started successfully",
            estimated_completion_time=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start image generation: {str(e)}"
        )

@router.get("/{image_id}", response_model=ImageGeneration)
async def get_image_generation(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get image generation status and details"""
    image_gen = await image_service.get_image_generation(
        db, image_id, current_user
    )
    
    if not image_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image generation not found"
        )
    
    return image_gen

@router.get("/", response_model=List[ImageGeneration])
async def list_image_generations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    style: Optional[ImageStyle] = None,
    quality: Optional[ImageQuality] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's image generations with optional filtering"""
    image_gens = await image_service.list_user_images(
        db, current_user, skip=skip, limit=limit,
        style=style, quality=quality, status=status
    )
    return image_gens

@router.delete("/{image_id}")
async def delete_image_generation(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an image generation"""
    image_gen = await image_service.get_image_generation(
        db, image_id, current_user
    )
    
    if not image_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image generation not found"
        )
    
    await image_service.delete_image_generation(db, image_id)
    return {"message": "Image generation deleted successfully"}

@router.post("/{image_id}/regenerate", response_model=ImageGenerationResponse)
async def regenerate_image(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Regenerate a failed image generation"""
    image_gen = await image_service.get_image_generation(
        db, image_id, current_user
    )
    
    if not image_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image generation not found"
        )
    
    if image_gen.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only regenerate failed image generations"
        )
    
    await image_service.regenerate_image(db, image_id)
    
    return ImageGenerationResponse(
        job_id=image_gen.id,
        status="pending",
        message="Image regeneration started"
    )

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
    format: str = Query("png", regex="^(png|jpg|jpeg|webp)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download generated image in specified format"""
    image_gen = await image_service.get_image_generation(
        db, image_id, current_user
    )
    
    if not image_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image generation not found"
        )
    
    if image_gen.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image generation not completed"
        )
    
    download_url = await image_service.get_download_url(image_gen, format)
    
    return {"download_url": download_url}

@router.post("/{image_id}/variations", response_model=ImageGenerationResponse)
async def create_image_variations(
    image_id: UUID,
    variation_count: int = Query(4, ge=1, le=8),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create variations of an existing image"""
    original_image = await image_service.get_image_generation(
        db, image_id, current_user
    )
    
    if not original_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original image not found"
        )
    
    if original_image.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original image must be completed before creating variations"
        )
    
    variations = await image_service.create_variations(
        db, original_image, variation_count, current_user
    )
    
    return ImageGenerationResponse(
        job_id=variations[0].id,
        status=variations[0].status,
        message=f"Creating {variation_count} image variations"
    )
