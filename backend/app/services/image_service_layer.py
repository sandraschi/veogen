# Image Service Layer for Imagen Integration

import asyncio
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.services.image_service import imagen_service, ImageGenerationRequest
from app.schemas.image import ImageGenerationCreate, ImageGeneration
from app.models.user import User

logger = logging.getLogger(__name__)

class ImageService:
    """Image generation service layer"""
    
    def __init__(self):
        self.imagen = imagen_service
        self.active_generations = {}  # In-memory storage for demo
    
    async def create_image_generation(
        self, 
        db: AsyncSession, 
        image_data: ImageGenerationCreate, 
        user: User
    ) -> ImageGeneration:
        """Create and start an image generation job"""
        
        # Create image generation record
        image_gen = ImageGeneration(
            id=uuid4(),
            user_id=user.id,
            prompt=image_data.prompt,
            style=image_data.style,
            aspect_ratio=image_data.aspect_ratio,
            quality=image_data.quality,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        # Store in memory for demo (would be database in production)
        self.active_generations[image_gen.id] = image_gen
        
        # Start background generation
        asyncio.create_task(self._generate_image_async(image_gen, db, user))
        
        return image_gen
    
    async def _generate_image_async(self, image_gen: ImageGeneration, db: AsyncSession, user: User):
        """Background task to generate image"""
        try:
            # Update status to generating
            image_gen.status = "generating"
            image_gen.updated_at = datetime.utcnow()
            
            # Create Imagen request
            imagen_request = ImageGenerationRequest(
                prompt=image_gen.prompt,
                style=image_gen.style,
                aspect_ratio=image_gen.aspect_ratio,
                quality=image_gen.quality
            )
            
            # Generate image using Imagen with user settings
            result = await self.imagen.generate_image(
                imagen_request, 
                db_session=db, 
                user_id=user.id
            )
            
            # Update generation with results
            image_gen.status = "completed"
            image_gen.completed_at = datetime.utcnow()
            image_gen.image_url = result.image_url
            image_gen.thumbnail_url = result.thumbnail_url
            image_gen.generation_time = result.metadata.get("generation_time")
            
        except Exception as e:
            logger.error(f"Image generation failed for {image_gen.id}: {e}")
            image_gen.status = "failed"
            image_gen.error_message = str(e)
            image_gen.updated_at = datetime.utcnow()
    
    async def get_image_generation(
        self, 
        db: AsyncSession, 
        image_id: UUID, 
        user: User
    ) -> Optional[ImageGeneration]:
        """Get image generation by ID"""
        return self.active_generations.get(image_id)
    
    async def list_user_images(
        self,
        db: AsyncSession,
        user: User,
        skip: int = 0,
        limit: int = 20,
        style: Optional[str] = None,
        quality: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ImageGeneration]:
        """List user's image generations with filtering"""
        user_images = [
            image for image in self.active_generations.values()
            if image.user_id == user.id
        ]
        
        # Apply filters
        if style:
            user_images = [i for i in user_images if i.style == style]
        if quality:
            user_images = [i for i in user_images if i.quality == quality]
        if status:
            user_images = [i for i in user_images if i.status == status]
        
        # Sort by creation date (newest first)
        user_images.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return user_images[skip:skip + limit]
    
    async def delete_image_generation(self, db: AsyncSession, image_id: UUID):
        """Delete image generation"""
        if image_id in self.active_generations:
            del self.active_generations[image_id]
    
    async def regenerate_image(self, db: AsyncSession, image_id: UUID):
        """Regenerate failed image"""
        image_gen = self.active_generations.get(image_id)
        if image_gen:
            image_gen.status = "pending"
            image_gen.error_message = None
            image_gen.updated_at = datetime.utcnow()
            
            # Get user for regeneration
            user = User(id=image_gen.user_id)  # Simplified - in production you'd fetch from DB
            
            # Start regeneration
            asyncio.create_task(self._generate_image_async(image_gen, db, user))
    
    async def get_download_url(self, image_gen: ImageGeneration, format: str) -> str:
        """Get download URL for image file"""
        if format == "png":
            return image_gen.image_url
        else:
            # Convert format (would be implemented in production)
            base_url = image_gen.image_url.replace('.png', f'.{format}')
            return base_url
    
    async def create_variations(
        self,
        db: AsyncSession,
        original_image: ImageGeneration,
        variation_count: int,
        user: User
    ) -> List[ImageGeneration]:
        """Create variations of existing image"""
        
        variations = []
        
        for i in range(variation_count):
            # Create variation generation
            variation_prompt = f"Variation {i+1} of: {original_image.prompt}"
            
            variation_data = ImageGenerationCreate(
                prompt=variation_prompt,
                style=original_image.style,
                aspect_ratio=original_image.aspect_ratio,
                quality=original_image.quality
            )
            
            variation = await self.create_image_generation(db, variation_data, user)
            variations.append(variation)
        
        return variations

# Global service instance
image_service = ImageService()
