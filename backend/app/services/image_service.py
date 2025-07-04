# Image Generation Service using Google Imagen

import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from app.config import settings
from app.middleware.metrics import track_image_generation
from app.utils.logging_config import log_image_generation_event

logger = logging.getLogger(__name__)

class ImageStyle(str, Enum):
    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic"
    ILLUSTRATION = "illustration"
    PAINTING = "painting"
    SKETCH = "sketch"
    ANIME = "anime"
    CARTOON = "cartoon"
    ABSTRACT = "abstract"

class ImageQuality(str, Enum):
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"

class AspectRatio(str, Enum):
    SQUARE = "1:1"
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    CLASSIC = "4:3"

@dataclass
class ImageGenerationRequest:
    prompt: str
    style: ImageStyle
    aspect_ratio: AspectRatio
    quality: ImageQuality

@dataclass
class ImageGenerationResult:
    image_url: str
    thumbnail_url: str
    metadata: Dict[str, Any]

class ImagenService:
    """Google Imagen AI Image Generation Service"""
    
    def __init__(self):
        self.client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Imagen service"""
        try:
            # Configure Gemini API for image generation
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Test connection
            models = genai.list_models()
            image_models = [m for m in models if 'image' in m.name.lower() or 'imagen' in m.name.lower()]
            
            if not image_models:
                logger.warning("No Imagen models found, using general Gemini for image generation")
            
            self.initialized = True
            logger.info("Imagen service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Imagen service: {e}")
            raise
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate image using Google Imagen
        
        Args:
            request: Image generation request parameters
            
        Returns:
            ImageGenerationResult with image URLs and metadata
        """
        if not self.initialized:
            await self.initialize()
        
        start_time = asyncio.get_event_loop().time()
        job_id = f"image_{int(start_time)}"
        
        try:
            # Log generation start
            log_image_generation_event(
                logger, "started", job_id,
                style=request.style,
                quality=request.quality,
                aspect_ratio=request.aspect_ratio
            )
            
            # Enhance prompt with style and quality parameters
            enhanced_prompt = self._create_image_prompt(request)
            
            # Generate image (simulated for now - would use actual Imagen API)
            image_result = await self._generate_imagen(enhanced_prompt, request)
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # Track metrics
            track_image_generation(
                request.style, 
                "completed", 
                duration
            )
            
            # Log completion
            log_image_generation_event(
                logger, "completed", job_id,
                duration=duration,
                style=request.style
            )
            
            result = ImageGenerationResult(
                image_url=image_result["image_url"],
                thumbnail_url=image_result["thumbnail_url"],
                metadata={
                    "style": request.style,
                    "quality": request.quality,
                    "aspect_ratio": request.aspect_ratio,
                    "generation_time": duration,
                    "prompt": request.prompt,
                    "enhanced_prompt": enhanced_prompt,
                }
            )
            
            logger.info(f"Image generation completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # Track failed generation
            track_image_generation(
                request.style,
                "failed",
                duration
            )
            
            # Log error
            log_image_generation_event(
                logger, "failed", job_id,
                error=str(e),
                duration=duration
            )
            
            logger.error(f"Image generation failed: {e}")
            raise
    
    def _create_image_prompt(self, request: ImageGenerationRequest) -> str:
        """Create enhanced prompt for image generation"""
        prompt_parts = [request.prompt]
        
        # Add style-specific keywords
        style_keywords = {
            ImageStyle.PHOTOREALISTIC: "photorealistic, highly detailed, realistic lighting, professional photography",
            ImageStyle.ARTISTIC: "artistic, creative interpretation, expressive, unique perspective",
            ImageStyle.ILLUSTRATION: "digital illustration, clean lines, stylized, graphic design",
            ImageStyle.PAINTING: "painted, traditional art, brushstrokes, fine art",
            ImageStyle.SKETCH: "pencil sketch, hand-drawn, line art, artistic drawing",
            ImageStyle.ANIME: "anime style, manga art, Japanese animation, vibrant colors",
            ImageStyle.CARTOON: "cartoon style, simplified forms, bright colors, playful",
            ImageStyle.ABSTRACT: "abstract art, non-representational, artistic expression"
        }
        
        if request.style in style_keywords:
            prompt_parts.append(style_keywords[request.style])
        
        # Add quality keywords
        quality_keywords = {
            ImageQuality.STANDARD: "good quality",
            ImageQuality.HIGH: "high quality, detailed",
            ImageQuality.ULTRA: "ultra high quality, extremely detailed, masterpiece"
        }
        
        if request.quality in quality_keywords:
            prompt_parts.append(quality_keywords[request.quality])
        
        # Add aspect ratio guidance
        ratio_keywords = {
            AspectRatio.SQUARE: "square composition",
            AspectRatio.LANDSCAPE: "wide landscape composition",
            AspectRatio.PORTRAIT: "vertical portrait composition",
            AspectRatio.CLASSIC: "classic photo composition"
        }
        
        if request.aspect_ratio in ratio_keywords:
            prompt_parts.append(ratio_keywords[request.aspect_ratio])
        
        return ", ".join(prompt_parts)
    
    async def _generate_imagen(self, prompt: str, request: ImageGenerationRequest) -> Dict[str, Any]:
        """Generate actual image using Imagen API"""
        # In real implementation, this would call Google Imagen API
        # For now, simulate image generation
        
        await asyncio.sleep(2)  # Simulate processing time
        
        # Get dimensions based on aspect ratio and quality
        dimensions = self._get_image_dimensions(request.aspect_ratio, request.quality)
        
        # Simulate file URLs
        timestamp = int(asyncio.get_event_loop().time())
        image_filename = f"{request.style}_{request.quality}_{timestamp}.png"
        thumbnail_filename = f"thumb_{image_filename}"
        
        return {
            "image_url": f"https://storage.googleapis.com/veogen-images/{image_filename}",
            "thumbnail_url": f"https://storage.googleapis.com/veogen-images/{thumbnail_filename}",
            "dimensions": dimensions,
            "file_size": self._estimate_file_size(dimensions, request.quality)
        }
    
    def _get_image_dimensions(self, aspect_ratio: AspectRatio, quality: ImageQuality) -> tuple:
        """Get image dimensions based on aspect ratio and quality"""
        base_sizes = {
            ImageQuality.STANDARD: 1024,
            ImageQuality.HIGH: 1536,
            ImageQuality.ULTRA: 2048
        }
        
        base_size = base_sizes[quality]
        
        dimensions_map = {
            AspectRatio.SQUARE: (base_size, base_size),
            AspectRatio.LANDSCAPE: (int(base_size * 16/9), base_size),
            AspectRatio.PORTRAIT: (base_size, int(base_size * 16/9)),
            AspectRatio.CLASSIC: (int(base_size * 4/3), base_size)
        }
        
        return dimensions_map.get(aspect_ratio, (base_size, base_size))
    
    def _estimate_file_size(self, dimensions: tuple, quality: ImageQuality) -> int:
        """Estimate file size in bytes"""
        width, height = dimensions
        pixels = width * height
        
        # Rough estimation based on quality
        bytes_per_pixel = {
            ImageQuality.STANDARD: 3,
            ImageQuality.HIGH: 4,
            ImageQuality.ULTRA: 6
        }
        
        return pixels * bytes_per_pixel.get(quality, 3)
    
    async def create_variations(self, original_image_data: Dict[str, Any], count: int = 4) -> List[Dict[str, Any]]:
        """Create variations of an existing image"""
        variations = []
        
        for i in range(count):
            # Create variation request based on original
            variation_request = ImageGenerationRequest(
                prompt=f"Variation of: {original_image_data['prompt']}",
                style=ImageStyle(original_image_data['style']),
                aspect_ratio=AspectRatio(original_image_data['aspect_ratio']),
                quality=ImageQuality(original_image_data['quality'])
            )
            
            # Generate variation
            variation_result = await self.generate_image(variation_request)
            variations.append({
                "image_url": variation_result.image_url,
                "thumbnail_url": variation_result.thumbnail_url,
                "metadata": variation_result.metadata
            })
        
        return variations

# Global service instance
imagen_service = ImagenService()
