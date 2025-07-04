from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)
router = APIRouter()

class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str
    preserve_formatting: bool = True
    context: Optional[str] = None

class TranslationResponse(BaseModel):
    translated_text: str
    detected_language: Optional[str] = None
    confidence: float
    alternatives: List[str] = []

class LanguageDetectionRequest(BaseModel):
    text: str

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    alternatives: List[dict]

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text from one language to another using AI
    """
    try:
        logger.info(f"Translating text from {request.source_language} to {request.target_language}")
        
        # Create translation prompt
        if request.source_language == "auto":
            prompt = f"""
            Translate the following text to {request.target_language}. 
            If the text appears to be in a different language, detect it and translate accordingly.
            
            Text to translate:
            {request.text}
            
            Context (if relevant): {request.context or "None"}
            
            Please provide:
            1. The translated text
            2. The detected source language (if auto-detection was used)
            3. Alternative translations if applicable
            
            Maintain the original formatting and tone of the text.
            """
        else:
            prompt = f"""
            Translate the following text from {request.source_language} to {request.target_language}.
            
            Text to translate:
            {request.text}
            
            Context (if relevant): {request.context or "None"}
            
            Please provide:
            1. The translated text
            2. Alternative translations if applicable
            
            Maintain the original formatting and tone of the text.
            """
        
        # Get AI translation
        response = await gemini_service.generate_content(prompt)
        translated_content = response.get("content", "")
        
        # Parse the response (simplified - in production you'd want more sophisticated parsing)
        lines = translated_content.split('\n')
        translated_text = ""
        detected_language = None
        alternatives = []
        
        for line in lines:
            if "translated:" in line.lower() or "translation:" in line.lower():
                translated_text = line.split(":", 1)[1].strip()
            elif "detected:" in line.lower() or "language:" in line.lower():
                detected_language = line.split(":", 1)[1].strip()
            elif "alternative" in line.lower():
                alternatives.append(line.strip())
        
        # If parsing failed, use the full response as translated text
        if not translated_text:
            translated_text = translated_content.strip()
        
        return TranslationResponse(
            translated_text=translated_text,
            detected_language=detected_language or request.source_language,
            confidence=0.95,  # Mock confidence score
            alternatives=alternatives[:3]  # Limit to 3 alternatives
        )
        
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to translate text: {str(e)}")

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """
    Detect the language of the provided text
    """
    try:
        logger.info("Detecting language of text")
        
        prompt = f"""
        Detect the language of the following text and provide confidence scores for the top 3 most likely languages:
        
        Text: {request.text}
        
        Please provide:
        1. The most likely language
        2. Confidence score (0-1)
        3. Alternative languages with their confidence scores
        """
        
        response = await gemini_service.generate_content(prompt)
        content = response.get("content", "")
        
        # Parse response (simplified)
        detected_language = "English"  # Default
        confidence = 0.9
        alternatives = [
            {"language": "Spanish", "confidence": 0.8},
            {"language": "French", "confidence": 0.7}
        ]
        
        # Try to extract from AI response
        lines = content.split('\n')
        for line in lines:
            if "language:" in line.lower():
                detected_language = line.split(":", 1)[1].strip()
            elif "confidence:" in line.lower():
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except:
                    pass
        
        return LanguageDetectionResponse(
            detected_language=detected_language,
            confidence=confidence,
            alternatives=alternatives
        )
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to detect language: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for translation
    """
    return {
        "languages": [
            {"code": "auto", "name": "Auto-detect", "flag": "🌐", "native_name": "Auto-detect"},
            {"code": "en", "name": "English", "flag": "🇺🇸", "native_name": "English"},
            {"code": "es", "name": "Spanish", "flag": "🇪🇸", "native_name": "Español"},
            {"code": "fr", "name": "French", "flag": "🇫🇷", "native_name": "Français"},
            {"code": "de", "name": "German", "flag": "🇩🇪", "native_name": "Deutsch"},
            {"code": "it", "name": "Italian", "flag": "🇮🇹", "native_name": "Italiano"},
            {"code": "pt", "name": "Portuguese", "flag": "🇵🇹", "native_name": "Português"},
            {"code": "ru", "name": "Russian", "flag": "🇷🇺", "native_name": "Русский"},
            {"code": "zh", "name": "Chinese", "flag": "🇨🇳", "native_name": "中文"},
            {"code": "ja", "name": "Japanese", "flag": "🇯🇵", "native_name": "日本語"},
            {"code": "ko", "name": "Korean", "flag": "🇰🇷", "native_name": "한국어"},
            {"code": "ar", "name": "Arabic", "flag": "🇸🇦", "native_name": "العربية"},
            {"code": "hi", "name": "Hindi", "flag": "🇮🇳", "native_name": "हिन्दी"},
            {"code": "nl", "name": "Dutch", "flag": "🇳🇱", "native_name": "Nederlands"},
            {"code": "sv", "name": "Swedish", "flag": "🇸🇪", "native_name": "Svenska"},
            {"code": "no", "name": "Norwegian", "flag": "🇳🇴", "native_name": "Norsk"},
            {"code": "da", "name": "Danish", "flag": "🇩🇰", "native_name": "Dansk"},
            {"code": "fi", "name": "Finnish", "flag": "🇫🇮", "native_name": "Suomi"},
            {"code": "pl", "name": "Polish", "flag": "🇵🇱", "native_name": "Polski"},
            {"code": "tr", "name": "Turkish", "flag": "🇹🇷", "native_name": "Türkçe"}
        ]
    }

@router.post("/batch-translate")
async def batch_translate(request: List[TranslationRequest]):
    """
    Translate multiple texts in a single request
    """
    try:
        logger.info(f"Batch translating {len(request)} texts")
        
        results = []
        for i, translation_request in enumerate(request):
            try:
                result = await translate_text(translation_request)
                results.append({
                    "index": i,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "results": results,
            "total": len(request),
            "successful": len([r for r in results if r["success"]])
        }
        
    except Exception as e:
        logger.error(f"Error in batch translation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to batch translate: {str(e)}")

@router.post("/translate-with-context")
async def translate_with_context(request: TranslationRequest):
    """
    Translate text with additional context for better accuracy
    """
    try:
        logger.info(f"Translating with context: {request.source_language} to {request.target_language}")
        
        prompt = f"""
        Translate the following text from {request.source_language} to {request.target_language}.
        
        Text to translate:
        {request.text}
        
        Additional context to consider:
        {request.context or "No additional context provided"}
        
        Please provide a contextually appropriate translation that takes into account:
        1. The domain or subject matter
        2. Cultural nuances
        3. Technical terminology if applicable
        4. The intended audience
        
        Provide the translation and explain any context-specific choices made.
        """
        
        response = await gemini_service.generate_content(prompt)
        
        return {
            "translated_text": response.get("content", ""),
            "context_notes": "Translation adapted for the provided context",
            "confidence": 0.92
        }
        
    except Exception as e:
        logger.error(f"Error translating with context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to translate with context: {str(e)}") 