"""
Image Generation API Endpoints
Uses MCP-based image service for Imagen generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.image import (
    ImageGeneration,
    ImageGenerationCreate,
    ImageGenerationResponse,
    ImageStyle,
    ImageQuality
)
from app.services.image_service import image_service

router = APIRouter()

class ImageGenerationRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"
    num_images: int = 1
    style: str = "photorealistic"

class ImageGenerationResponse(BaseModel):
    status: str
    image_id: str
    image_urls: Optional[List[str]] = None
    prompt: Optional[str] = None
    aspect_ratio: Optional[str] = None
    error: Optional[str] = None

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

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate an image using Imagen via MCP"""
    try:
        result = await image_service.generate_image(
            prompt=request.prompt,
            user_id=current_user.id,
            aspect_ratio=request.aspect_ratio,
            num_images=request.num_images,
            style=request.style
        )
        
        return ImageGenerationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.get("/status/{image_id}", response_model=ImageStatusResponse)
async def get_image_status(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
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
async def list_user_images(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get all images for the current user"""
    try:
        images = await image_service.get_user_images(current_user.id, limit)
        return [ImageStatusResponse(**image) for image in images]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user images: {str(e)}")

@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
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
