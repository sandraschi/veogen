"""
Image Generation Service for VeoGen
Uses Google's MCP servers for Imagen image generation
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from .mcp_media_service import mcp_media_service
from ..models.image import ImageGeneration
from ..database import get_db

logger = logging.getLogger(__name__)

class ImageService:
    """Service for image generation using Google's Imagen via MCP"""
    
    def __init__(self):
        self.db = get_db()
        
    async def generate_image(self, prompt: str, user_id: int, aspect_ratio: str = "1:1", 
                           num_images: int = 1, style: str = "photorealistic") -> Dict[str, Any]:
        """Generate image using Imagen via MCP servers"""
        
        # Create image generation record
        image_id = str(uuid.uuid4())
        image_generation = ImageGeneration(
            id=image_id,
            user_id=user_id,
            prompt=prompt,
            status="processing",
            aspect_ratio=aspect_ratio,
            num_images=num_images,
            style=style,
            created_at=datetime.utcnow()
        )
        
        try:
            # Add to database
            self.db.add(image_generation)
            self.db.commit()
            
            logger.info(f"Starting image generation {image_id} for user {user_id}")
            
            # Generate image using MCP service
            result = await mcp_media_service.generate_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                num_images=num_images,
                user_id=user_id
            )
            
            if result["status"] == "success":
                # Update database with success
                image_generation.status = "completed"
                image_generation.image_urls = result["image_urls"]
                image_generation.completed_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Image generation {image_id} completed successfully")
                
                return {
                    "status": "success",
                    "image_id": image_id,
                    "image_urls": result["image_urls"],
                    "prompt": result["prompt"],
                    "aspect_ratio": result["aspect_ratio"]
                }
            else:
                # Update database with error
                image_generation.status = "failed"
                image_generation.error_message = result.get("error", "Unknown error")
                image_generation.completed_at = datetime.utcnow()
                self.db.commit()
                
                logger.error(f"Image generation {image_id} failed: {result.get('error')}")
                
                return {
                    "status": "error",
                    "image_id": image_id,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            # Update database with error
            image_generation.status = "failed"
            image_generation.error_message = str(e)
            image_generation.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.error(f"Image generation {image_id} failed with exception: {e}")
            
            return {
                "status": "error",
                "image_id": image_id,
                "error": str(e)
            }
            
    async def get_image_status(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an image generation"""
        try:
            image = self.db.query(ImageGeneration).filter(ImageGeneration.id == image_id).first()
            
            if not image:
                return None
                
            return {
                "image_id": image.id,
                "status": image.status,
                "prompt": image.prompt,
                "aspect_ratio": image.aspect_ratio,
                "num_images": image.num_images,
                "style": image.style,
                "image_urls": image.image_urls,
                "error_message": image.error_message,
                "created_at": image.created_at.isoformat() if image.created_at else None,
                "completed_at": image.completed_at.isoformat() if image.completed_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting image status {image_id}: {e}")
            return None
            
    async def get_user_images(self, user_id: int, limit: int = 50) -> list:
        """Get all images for a user"""
        try:
            images = self.db.query(ImageGeneration)\
                .filter(ImageGeneration.user_id == user_id)\
                .order_by(ImageGeneration.created_at.desc())\
                .limit(limit)\
                .all()
                
            return [
                {
                    "image_id": image.id,
                    "status": image.status,
                    "prompt": image.prompt,
                    "aspect_ratio": image.aspect_ratio,
                    "num_images": image.num_images,
                    "style": image.style,
                    "image_urls": image.image_urls,
                    "error_message": image.error_message,
                    "created_at": image.created_at.isoformat() if image.created_at else None,
                    "completed_at": image.completed_at.isoformat() if image.completed_at else None
                }
                for image in images
            ]
            
        except Exception as e:
            logger.error(f"Error getting images for user {user_id}: {e}")
            return []
            
    async def delete_image(self, image_id: str, user_id: int) -> bool:
        """Delete an image generation record"""
        try:
            image = self.db.query(ImageGeneration)\
                .filter(ImageGeneration.id == image_id, ImageGeneration.user_id == user_id)\
                .first()
                
            if not image:
                return False
                
            self.db.delete(image)
            self.db.commit()
            
            logger.info(f"Deleted image {image_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {e}")
            return False

# Global instance
image_service = ImageService()
