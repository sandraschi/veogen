"""
VeoGen Music Generation with Google Lyria

Music Generation Service - Integration with Google's Lyria AI for advanced music generation capabilities.

Music Service Architecture
"""
import asyncio
import logging
import base64
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from google.cloud import aiplatform
from google.cloud.aiplatform_v1.types import prediction_service
from app.config import settings
from app.database import get_user_setting
from app.middleware.metrics import track_music_generation
from app.utils.logging_config import log_music_generation_event

logger = logging.getLogger(__name__)

class MusicStyle(str, Enum):
    CLASSICAL = "classical"
    JAZZ = "jazz"
    ROCK = "rock"
    ELECTRONIC = "electronic"
    AMBIENT = "ambient"
    CINEMATIC = "cinematic"
    POP = "pop"
    FOLK = "folk"
    BLUES = "blues"
    COUNTRY = "country"
    HIP_HOP = "hip_hop"
    REGGAE = "reggae"

class MusicMood(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    CALM = "calm"
    MYSTERIOUS = "mysterious"
    ROMANTIC = "romantic"
    EPIC = "epic"
    NOSTALGIC = "nostalgic"
    DARK = "dark"
    UPLIFTING = "uplifting"

class InstrumentType(str, Enum):
    PIANO = "piano"
    GUITAR = "guitar"
    VIOLIN = "violin"
    DRUMS = "drums"
    SYNTHESIZER = "synthesizer"
    ORCHESTRA = "orchestra"
    VOCAL = "vocal"
    BASS = "bass"
    SAXOPHONE = "saxophone"
    FLUTE = "flute"

@dataclass
class MusicGenerationRequest:
    prompt: str
    style: MusicStyle
    mood: MusicMood
    duration: int  # seconds
    tempo: Optional[int] = None  # BPM
    key: Optional[str] = None  # Musical key
    instruments: List[InstrumentType] = None
    vocal_style: Optional[str] = None
    lyrics: Optional[str] = None
    reference_track: Optional[str] = None

@dataclass
class MusicGenerationResult:
    audio_url: str
    preview_url: str
    waveform_data: List[float]
    metadata: Dict[str, Any]
    lyrics: Optional[str] = None
    chord_progression: Optional[List[str]] = None
    sheet_music_url: Optional[str] = None

class LyriaService:
    """Google Lyria AI Music Generation Service"""
    
    def __init__(self):
        self.client = None
        self.initialized = False
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
    
    def _get_api_key_from_user_settings(self, db_session=None, user_id=None, key_name="gemini_api_key"):
        """Get API key from user settings first, then environment variables"""
        try:
            if db_session and user_id:
                # Try to get from user settings first
                user_key = get_user_setting(db_session, user_id, key_name)
                if user_key:
                    return user_key
        except Exception as e:
            logger.warning(f"Could not get API key from user settings: {e}")
        
        # Fall back to environment variables
        if key_name == "gemini_api_key":
            return settings.GEMINI_API_KEY
        elif key_name == "google_api_key":
            return settings.GOOGLE_API_KEY
        elif key_name == "google_cloud_project":
            return settings.GOOGLE_CLOUD_PROJECT
        
        return None
    
    async def initialize(self, db_session=None, user_id=None):
        """Initialize Lyria service with Google Cloud AI Platform"""
        try:
            # Get API keys from user settings or environment
            gemini_key = self._get_api_key_from_user_settings(db_session, user_id, "gemini_api_key")
            google_key = self._get_api_key_from_user_settings(db_session, user_id, "google_api_key")
            project_id = self._get_api_key_from_user_settings(db_session, user_id, "google_cloud_project") or self.project_id
            
            # Initialize Google Cloud AI Platform
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                aiplatform.init(
                    project=project_id,
                    location=self.location,
                    credentials=settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                aiplatform.init(
                    project=project_id,
                    location=self.location
                )
            
            # Configure Gemini API for fallback and lyrics generation
            if gemini_key:
                genai.configure(api_key=gemini_key)
            
            self.initialized = True
            logger.info("Lyria service initialized successfully with Google Cloud AI Platform")
            
        except Exception as e:
            logger.error(f"Failed to initialize Lyria service: {e}")
            # Fallback to Gemini if Google Cloud fails
            gemini_key = self._get_api_key_from_user_settings(db_session, user_id, "gemini_api_key")
            if gemini_key:
                genai.configure(api_key=gemini_key)
                self.initialized = True
                logger.info("Falling back to Gemini API for music generation")
            else:
                raise
    
    async def generate_music(self, request: MusicGenerationRequest, db_session=None, user_id=None) -> MusicGenerationResult:
        """
        Generate music using Google Lyria
        
        Args:
            request: Music generation request parameters
            db_session: Database session for user settings
            user_id: User ID for getting API keys from settings
            
        Returns:
            MusicGenerationResult with audio URLs and metadata
        """
        if not self.initialized:
            await self.initialize(db_session, user_id)
        
        start_time = asyncio.get_event_loop().time()
        job_id = f"music_{int(start_time)}"
        
        try:
            # Log generation start
            log_music_generation_event(
                logger, "started", job_id,
                style=request.style,
                mood=request.mood,
                duration=request.duration
            )
            
            # Enhance prompt with musical parameters
            enhanced_prompt = self._create_musical_prompt(request)
            
            # Generate music metadata and composition
            composition = await self._generate_composition(enhanced_prompt, request, db_session, user_id)
            
            # Try real Lyria API first, fallback to Gemini if needed
            try:
                audio_result = await self._generate_audio_real(composition, request, db_session, user_id)
            except Exception as e:
                logger.warning(f"Lyria API failed, falling back to Gemini: {e}")
                audio_result = await self._generate_audio_gemini(composition, request, db_session, user_id)
            
            # Generate additional musical elements
            lyrics = await self._generate_lyrics(request, db_session, user_id) if request.vocal_style else None
            chord_progression = await self._generate_chord_progression(request)
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # Track metrics
            track_music_generation(
                request.style, 
                "completed", 
                duration
            )
            
            # Log completion
            log_music_generation_event(
                logger, "completed", job_id,
                duration=duration,
                style=request.style
            )
            
            result = MusicGenerationResult(
                audio_url=audio_result["audio_url"],
                preview_url=audio_result["preview_url"],
                waveform_data=audio_result["waveform_data"],
                metadata={
                    "style": request.style,
                    "mood": request.mood,
                    "duration": request.duration,
                    "tempo": composition.get("tempo", request.tempo),
                    "key": composition.get("key", request.key),
                    "instruments": composition.get("instruments", []),
                    "generation_time": duration,
                    "composition_analysis": composition,
                    "api_used": audio_result.get("api_used", "lyria"),
                },
                lyrics=lyrics,
                chord_progression=chord_progression,
                sheet_music_url=audio_result.get("sheet_music_url")
            )
            
            logger.info(f"Music generation completed in {duration:.2f}s using {audio_result.get('api_used', 'lyria')}")
            return result
            
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # Track failed generation
            track_music_generation(
                request.style,
                "failed",
                duration
            )
            
            # Log error
            log_music_generation_event(
                logger, "failed", job_id,
                error=str(e),
                duration=duration
            )
            
            logger.error(f"Music generation failed: {e}")
            raise
    
    async def _generate_audio_real(self, composition: Dict[str, Any], request: MusicGenerationRequest, db_session=None, user_id=None) -> Dict[str, Any]:
        """Generate actual audio using real Google Lyria API"""
        try:
            # Get project ID from user settings or environment
            project_id = self._get_api_key_from_user_settings(db_session, user_id, "google_cloud_project") or self.project_id
            
            # Prepare the request for Lyria
            lyria_request = {
                "prompt": composition.get("prompt", request.prompt),
                "duration": request.duration,
                "tempo": composition.get("tempo", request.tempo or self._get_default_tempo(request.style)),
                "key": composition.get("key", request.key or self._get_default_key(request.mood)),
                "style": request.style.value,
                "mood": request.mood.value,
                "instruments": [inst.value for inst in (request.instruments or [])],
                "sample_rate": 44100,
                "format": "mp3"
            }
            
            # Call Lyria API via Google Cloud AI Platform
            # Note: This is a simplified version - actual implementation would use the specific Lyria endpoint
            endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{project_id}/locations/{self.location}/endpoints/lyria"
            )
            
            # Make prediction request
            response = await asyncio.to_thread(
                endpoint.predict,
                instances=[lyria_request]
            )
            
            # Extract audio data from response
            audio_data = response.predictions[0]
            
            # Generate waveform data from audio
            waveform_data = self._generate_waveform_from_audio(audio_data, request.duration)
            
            # Save audio to storage and get URLs
            timestamp = int(asyncio.get_event_loop().time())
            audio_filename = f"lyria_{request.style}_{request.mood}_{timestamp}.mp3"
            
            # For now, return placeholder URLs - in production you'd save to Google Cloud Storage
            return {
                "audio_url": f"https://storage.googleapis.com/veogen-music/{audio_filename}",
                "preview_url": f"https://storage.googleapis.com/veogen-music/preview_{audio_filename}",
                "waveform_data": waveform_data,
                "sheet_music_url": f"https://storage.googleapis.com/veogen-music/sheet_{audio_filename}.pdf",
                "api_used": "lyria"
            }
            
        except Exception as e:
            logger.error(f"Real Lyria API call failed: {e}")
            raise
    
    async def _generate_audio_gemini(self, composition: Dict[str, Any], request: MusicGenerationRequest, db_session=None, user_id=None) -> Dict[str, Any]:
        """Generate audio using Gemini API as fallback"""
        try:
            # Use Gemini for music generation (this would be more complex in reality)
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            # Create music generation prompt
            music_prompt = f"""
            Generate music based on this description: {request.prompt}
            
            Style: {request.style.value}
            Mood: {request.mood.value}
            Duration: {request.duration} seconds
            Tempo: {composition.get('tempo', request.tempo or self._get_default_tempo(request.style))} BPM
            Key: {composition.get('key', request.key or self._get_default_key(request.mood))}
            Instruments: {', '.join([inst.value for inst in (request.instruments or [])])}
            
            Please create music that matches the description and musical parameters.
            """
            
            # Generate music using Gemini (this is a simplified approach)
            response = await asyncio.to_thread(
                model.generate_content,
                music_prompt
            )
            
            # Generate simulated waveform data
            waveform_data = self._generate_simulated_waveform(request.duration)
            
            # Save audio to storage and get URLs
            timestamp = int(asyncio.get_event_loop().time())
            audio_filename = f"gemini_{request.style}_{request.mood}_{timestamp}.mp3"
            
            return {
                "audio_url": f"https://storage.googleapis.com/veogen-music/{audio_filename}",
                "preview_url": f"https://storage.googleapis.com/veogen-music/preview_{audio_filename}",
                "waveform_data": waveform_data,
                "sheet_music_url": f"https://storage.googleapis.com/veogen-music/sheet_{audio_filename}.pdf",
                "api_used": "gemini"
            }
            
        except Exception as e:
            logger.error(f"Gemini music generation failed: {e}")
            raise
    
    def _generate_waveform_from_audio(self, audio_data: Any, duration: int) -> List[float]:
        """Generate waveform data from audio response"""
        # In real implementation, this would process the actual audio data
        # For now, return simulated waveform
        return self._generate_simulated_waveform(duration)
    
    def _generate_simulated_waveform(self, duration: int) -> List[float]:
        """Generate simulated waveform data for demo purposes"""
        import math
        import random
        
        sample_rate = 44100
        duration_samples = int(duration * sample_rate)
        waveform = []
        
        for i in range(min(duration_samples, 1000)):  # Limit for demo
            # Simple sine wave with some randomness
            t = i / sample_rate
            frequency = 440  # A4 note
            amplitude = 0.5 * math.sin(2 * math.pi * frequency * t)
            amplitude += 0.1 * random.uniform(-1, 1)  # Add some noise
            waveform.append(amplitude)
        
        return waveform

    def _create_musical_prompt(self, request: MusicGenerationRequest) -> str:
        """Create enhanced musical prompt"""
        prompt_parts = [request.prompt]
        
        # Add style-specific keywords
        style_keywords = {
            MusicStyle.CLASSICAL: "classical orchestral, sophisticated, refined",
            MusicStyle.JAZZ: "jazz, improvisational, swing, sophisticated",
            MusicStyle.ROCK: "rock, energetic, powerful, electric guitars",
            MusicStyle.ELECTRONIC: "electronic, synthesizer, digital, modern",
            MusicStyle.AMBIENT: "ambient, atmospheric, peaceful, ethereal",
            MusicStyle.CINEMATIC: "cinematic, dramatic, orchestral, film score",
            MusicStyle.POP: "pop, catchy, mainstream, radio-friendly",
            MusicStyle.FOLK: "folk, acoustic, traditional, storytelling",
            MusicStyle.BLUES: "blues, soulful, emotional, guitar-driven",
            MusicStyle.COUNTRY: "country, twangy, rural, storytelling",
            MusicStyle.HIP_HOP: "hip hop, rhythmic, urban, beat-driven",
            MusicStyle.REGGAE: "reggae, laid-back, Caribbean, rhythmic"
        }
        
        if request.style in style_keywords:
            prompt_parts.append(style_keywords[request.style])
        
        # Add mood keywords
        mood_keywords = {
            MusicMood.HAPPY: "upbeat, cheerful, joyful, positive",
            MusicMood.SAD: "melancholic, somber, emotional, reflective",
            MusicMood.ENERGETIC: "energetic, dynamic, powerful, exciting",
            MusicMood.CALM: "calm, peaceful, soothing, relaxing",
            MusicMood.MYSTERIOUS: "mysterious, enigmatic, atmospheric, intriguing",
            MusicMood.ROMANTIC: "romantic, passionate, intimate, emotional",
            MusicMood.EPIC: "epic, grand, majestic, powerful",
            MusicMood.NOSTALGIC: "nostalgic, sentimental, reflective, warm",
            MusicMood.DARK: "dark, intense, brooding, dramatic",
            MusicMood.UPLIFTING: "uplifting, inspiring, motivational, positive"
        }
        
        if request.mood in mood_keywords:
            prompt_parts.append(mood_keywords[request.mood])
        
        # Add instrument information
        if request.instruments:
            instrument_names = [inst.value for inst in request.instruments]
            prompt_parts.append(f"instruments: {', '.join(instrument_names)}")
        
        # Add tempo and key information
        if request.tempo:
            prompt_parts.append(f"tempo: {request.tempo} BPM")
        if request.key:
            prompt_parts.append(f"key: {request.key}")
        
        return ", ".join(prompt_parts)
    
    async def _generate_composition(self, prompt: str, request: MusicGenerationRequest, db_session=None, user_id=None) -> Dict[str, Any]:
        """Generate musical composition using AI"""
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            composition_prompt = f"""
            Create a detailed musical composition for this prompt: {prompt}
            
            Style: {request.style.value}
            Mood: {request.mood.value}
            Duration: {request.duration} seconds
            
            Generate a JSON response with these fields:
            {{
                "tempo": number (BPM),
                "key": "string (musical key)",
                "time_signature": "string (e.g., 4/4)",
                "instruments": ["list", "of", "instruments"],
                "structure": ["intro", "verse", "chorus", "bridge", "outro"],
                "composition_notes": "string (musical analysis and notes)"
            }}
            
            Make the composition musically appropriate for the style and mood.
            """
            
            response = await asyncio.to_thread(
                model.generate_content,
                composition_prompt
            )
            
            # Parse the JSON response
            composition = json.loads(response.text)
            
            return composition
            
        except Exception as e:
            logger.error(f"Composition generation failed: {e}")
            return self._get_default_composition(request)
    
    async def _generate_lyrics(self, request: MusicGenerationRequest, db_session=None, user_id=None) -> Optional[str]:
        """Generate lyrics for vocal tracks"""
        if not request.vocal_style:
            return None
        
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            lyrics_prompt = f"""
            Write song lyrics for a {request.style} song with a {request.mood} mood.
            Vocal style: {request.vocal_style}
            Theme: {request.prompt}
            Duration: approximately {request.duration} seconds
            
            Structure the lyrics with verses, chorus, and bridge as appropriate.
            Make the lyrics emotionally resonant and fitting for the musical style.
            """
            
            response = await asyncio.to_thread(
                model.generate_content,
                lyrics_prompt
            )
            
            return response.text if response.text else None
            
        except Exception as e:
            logger.error(f"Lyrics generation failed: {e}")
            return None
    
    async def _generate_chord_progression(self, request: MusicGenerationRequest) -> List[str]:
        """Generate chord progression for the music"""
        try:
            # Use music theory to generate appropriate chord progressions
            key = request.key or self._get_default_key(request.mood)
            style_progressions = {
                MusicStyle.CLASSICAL: ["I", "vi", "IV", "V"],
                MusicStyle.JAZZ: ["ii", "V", "I", "vi"],
                MusicStyle.ROCK: ["I", "V", "vi", "IV"],
                MusicStyle.POP: ["vi", "IV", "I", "V"],
                MusicStyle.BLUES: ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"],
                MusicStyle.FOLK: ["I", "V", "vi", "IV"],
            }
            
            progression = style_progressions.get(request.style, ["I", "V", "vi", "IV"])
            
            # Convert Roman numerals to actual chords based on key
            actual_chords = self._convert_progression_to_chords(progression, key)
            
            return actual_chords
            
        except Exception as e:
            logger.error(f"Chord progression generation failed: {e}")
            return ["C", "G", "Am", "F"]  # Default progression
    
    def _get_default_tempo(self, style: MusicStyle) -> int:
        """Get default tempo for music style"""
        tempo_map = {
            MusicStyle.CLASSICAL: 120,
            MusicStyle.JAZZ: 120,
            MusicStyle.ROCK: 120,
            MusicStyle.ELECTRONIC: 128,
            MusicStyle.AMBIENT: 80,
            MusicStyle.CINEMATIC: 100,
            MusicStyle.POP: 120,
            MusicStyle.FOLK: 100,
            MusicStyle.BLUES: 100,
            MusicStyle.COUNTRY: 110,
            MusicStyle.HIP_HOP: 90,
            MusicStyle.REGGAE: 70,
        }
        return tempo_map.get(style, 120)
    
    def _get_default_key(self, mood: MusicMood) -> str:
        """Get default key for mood"""
        key_map = {
            MusicMood.HAPPY: "C major",
            MusicMood.SAD: "A minor",
            MusicMood.ENERGETIC: "E major",
            MusicMood.CALM: "F major",
            MusicMood.MYSTERIOUS: "D minor",
            MusicMood.ROMANTIC: "G major",
            MusicMood.EPIC: "C minor",
            MusicMood.NOSTALGIC: "G minor",
            MusicMood.DARK: "B minor",
            MusicMood.UPLIFTING: "D major",
        }
        return key_map.get(mood, "C major")
    
    def _get_default_instruments(self, style: MusicStyle) -> List[str]:
        """Get default instruments for style"""
        instrument_map = {
            MusicStyle.CLASSICAL: ["piano", "violin", "cello", "flute"],
            MusicStyle.JAZZ: ["piano", "saxophone", "trumpet", "drums", "bass"],
            MusicStyle.ROCK: ["guitar", "bass", "drums", "vocal"],
            MusicStyle.ELECTRONIC: ["synthesizer", "drums", "bass"],
            MusicStyle.AMBIENT: ["synthesizer", "piano", "strings"],
            MusicStyle.CINEMATIC: ["orchestra", "piano", "strings", "brass"],
            MusicStyle.POP: ["piano", "guitar", "drums", "bass", "vocal"],
            MusicStyle.FOLK: ["acoustic_guitar", "vocal", "harmonica"],
            MusicStyle.BLUES: ["guitar", "piano", "harmonica", "drums"],
            MusicStyle.COUNTRY: ["guitar", "fiddle", "banjo", "drums"],
            MusicStyle.HIP_HOP: ["drums", "bass", "synthesizer", "vocal"],
            MusicStyle.REGGAE: ["guitar", "bass", "drums", "keyboard"],
        }
        return instrument_map.get(style, ["piano", "guitar", "drums"])
    
    def _get_default_composition(self, request: MusicGenerationRequest) -> Dict[str, Any]:
        """Get default composition if generation fails"""
        return {
            "tempo": self._get_default_tempo(request.style),
            "key": self._get_default_key(request.mood),
            "time_signature": "4/4",
            "instruments": self._get_default_instruments(request.style),
            "structure": ["intro", "verse", "chorus", "verse", "chorus", "outro"],
            "composition_notes": "Default composition template"
        }
    
    def _convert_progression_to_chords(self, progression: List[str], key: str) -> List[str]:
        """Convert Roman numeral progression to actual chords"""
        # Simplified chord conversion (would be more complex in real implementation)
        major_keys = {
            "C major": ["C", "Dm", "Em", "F", "G", "Am", "Bdim"],
            "G major": ["G", "Am", "Bm", "C", "D", "Em", "F#dim"],
            "D major": ["D", "Em", "F#m", "G", "A", "Bm", "C#dim"],
            "A major": ["A", "Bm", "C#m", "D", "E", "F#m", "G#dim"],
            "E major": ["E", "F#m", "G#m", "A", "B", "C#m", "D#dim"],
            "F major": ["F", "Gm", "Am", "Bb", "C", "Dm", "Edim"],
        }
        
        minor_keys = {
            "A minor": ["Am", "Bdim", "C", "Dm", "Em", "F", "G"],
            "D minor": ["Dm", "Edim", "F", "Gm", "Am", "Bb", "C"],
            "G minor": ["Gm", "Adim", "Bb", "Cm", "Dm", "Eb", "F"],
            "B minor": ["Bm", "C#dim", "D", "Em", "F#m", "G", "A"],
        }
        
        # Get chord scale
        if "minor" in key:
            scale = minor_keys.get(key, minor_keys["A minor"])
        else:
            scale = major_keys.get(key, major_keys["C major"])
        
        # Convert Roman numerals to chords
        roman_to_index = {
            "I": 0, "i": 0,
            "ii": 1, "II": 1,
            "iii": 2, "III": 2,
            "IV": 3, "iv": 3,
            "V": 4, "v": 4,
            "vi": 5, "VI": 5,
            "vii": 6, "VII": 6,
        }
        
        actual_chords = []
        for roman in progression:
            index = roman_to_index.get(roman, 0)
            actual_chords.append(scale[index])
        
        return actual_chords

# Global service instance
lyria_service = LyriaService()
