from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import logging
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)
router = APIRouter()

class BookRequest(BaseModel):
    title: str
    genre: str
    length: str = "novel"
    main_character: str
    love_interest: Optional[str] = None
    antagonist: Optional[str] = None
    content_ideas: Optional[str] = None
    selected_tropes: List[str] = []
    setting: Optional[str] = None
    time_period: Optional[str] = None

class BookResponse(BaseModel):
    outline: str
    first_chapter: str
    characters: dict
    plot_summary: str
    chapter_breakdown: List[dict]

@router.post("/generate", response_model=BookResponse)
async def generate_book(request: BookRequest, background_tasks: BackgroundTasks):
    """
    Generate a complete book outline and first chapter based on user specifications
    """
    try:
        logger.info(f"Generating book: {request.title} ({request.genre})")
        
        # Create detailed prompt for book generation
        prompt = f"""
        Create a complete book outline and first chapter for a {request.genre} novel titled "{request.title}".
        
        Book Details:
        - Title: {request.title}
        - Genre: {request.genre}
        - Length: {request.length}
        - Main Character: {request.main_character}
        - Love Interest: {request.love_interest or "None"}
        - Antagonist: {request.antagonist or "None"}
        - Setting: {request.setting or "Modern day"}
        - Time Period: {request.time_period or "Contemporary"}
        - Content Ideas: {request.content_ideas or "None"}
        - Selected Tropes: {', '.join(request.selected_tropes) if request.selected_tropes else "None"}
        
        Please provide:
        1. A detailed book outline with chapter breakdown
        2. Character descriptions and development arcs
        3. A compelling first chapter (approximately 2000-3000 words)
        4. Plot summary and major story beats
        5. Writing style appropriate for the genre
        
        Format the response as structured sections with clear headings.
        """
        
        # Generate content using Gemini
        response = await gemini_service.generate_content(prompt)
        
        # Parse the response into structured sections
        # This is a simplified parser - in production you'd want more sophisticated parsing
        content = response.get("content", "")
        
        # Split content into sections (this is a basic implementation)
        sections = content.split("\n\n")
        
        outline = ""
        first_chapter = ""
        characters = {}
        plot_summary = ""
        chapter_breakdown = []
        
        current_section = ""
        for section in sections:
            if "outline" in section.lower() or "chapter" in section.lower():
                outline += section + "\n\n"
            elif "character" in section.lower():
                characters["main_character"] = request.main_character
                if request.love_interest:
                    characters["love_interest"] = request.love_interest
                if request.antagonist:
                    characters["antagonist"] = request.antagonist
            elif "first chapter" in section.lower() or "chapter 1" in section.lower():
                first_chapter = section
            elif "plot" in section.lower() or "summary" in section.lower():
                plot_summary = section
            else:
                outline += section + "\n\n"
        
        # Create chapter breakdown
        chapter_breakdown = [
            {
                "chapter": 1,
                "title": f"Chapter 1: {request.title}",
                "summary": "Opening chapter introducing the main character and setting",
                "word_count": len(first_chapter.split()) if first_chapter else 0
            }
        ]
        
        return BookResponse(
            outline=outline.strip(),
            first_chapter=first_chapter.strip(),
            characters=characters,
            plot_summary=plot_summary.strip(),
            chapter_breakdown=chapter_breakdown
        )
        
    except Exception as e:
        logger.error(f"Error generating book: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate book: {str(e)}")

@router.get("/genres")
async def get_genres():
    """
    Get list of available book genres
    """
    return {
        "genres": [
            "Fantasy", "Science Fiction", "Romance", "Mystery", "Thriller", "Horror",
            "Historical Fiction", "Contemporary Fiction", "Young Adult", "Literary Fiction",
            "Adventure", "Dystopian", "Paranormal", "Contemporary Romance", "Historical Romance"
        ]
    }

@router.get("/tropes")
async def get_tropes():
    """
    Get list of popular story tropes
    """
    return {
        "tropes": [
            "Enemies to Lovers", "Chosen One", "Found Family", "Redemption Arc",
            "Love Triangle", "Fish Out of Water", "Coming of Age", "Forbidden Love",
            "Second Chance", "Fake Relationship", "Marriage of Convenience", "Slow Burn",
            "Friends to Lovers", "Opposites Attract", "Forced Proximity", "Grumpy Sunshine",
            "Only One Bed", "Miscommunication", "Secret Identity", "Hidden Powers"
        ]
    }

@router.get("/lengths")
async def get_lengths():
    """
    Get list of available book lengths
    """
    return {
        "lengths": [
            {"id": "short_story", "name": "Short Story", "word_count": "1,000-7,500"},
            {"id": "novelette", "name": "Novelette", "word_count": "7,500-17,500"},
            {"id": "novella", "name": "Novella", "word_count": "17,500-40,000"},
            {"id": "novel", "name": "Novel", "word_count": "40,000-100,000"},
            {"id": "epic", "name": "Epic Novel", "word_count": "100,000+"}
        ]
    } 