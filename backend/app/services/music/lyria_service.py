"""
VeoGen Music Generation with Google Lyria

Music Generation Service - Integration with Google's Lyria AI for advanced music generation capabilities.

Music Service Architecture
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from app.config import settings
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
    
    async def initialize(self):
        """Initialize Lyria service"""
        try:
            # Configure Gemini API for music generation
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Test connection
            models = genai.list_models()
            music_models = [m for m in models if 'music' in m.name.lower() or 'lyria' in m.name.lower()]
            
            if not music_models:
                logger.warning("No Lyria/Music models found, using general Gemini for music metadata")
            
            self.initialized = True
            logger.info("Lyria service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Lyria service: {e}")
            raise
    
    async def generate_music(self, request: MusicGenerationRequest) -> MusicGenerationResult:
        """
        Generate music using Google Lyria
        
        Args:
            request: Music generation request parameters
            
        Returns:
            MusicGenerationResult with audio URLs and metadata
        """
        if not self.initialized:
            await self.initialize()
        
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
            composition = await self._generate_composition(enhanced_prompt, request)
            
            # Generate actual audio (simulated for now - would use actual Lyria API)
            audio_result = await self._generate_audio(composition, request)
            
            # Generate additional musical elements
            lyrics = await self._generate_lyrics(request) if request.vocal_style else None
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
                },
                lyrics=lyrics,
                chord_progression=chord_progression,
                sheet_music_url=audio_result.get("sheet_music_url")
            )
            
            logger.info(f"Music generation completed in {duration:.2f}s")
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
    
    def _create_musical_prompt(self, request: MusicGenerationRequest) -> str:
        """Create enhanced prompt for music generation"""
        prompt_parts = [
            f"Create a {request.style} music piece",
            f"with a {request.mood} mood",
            f"lasting {request.duration} seconds"
        ]
        
        if request.tempo:
            prompt_parts.append(f"at {request.tempo} BPM")
        
        if request.key:
            prompt_parts.append(f"in the key of {request.key}")
        
        if request.instruments:
            instruments_str = ", ".join(request.instruments)
            prompt_parts.append(f"featuring {instruments_str}")
        
        if request.vocal_style:
            prompt_parts.append(f"with {request.vocal_style} vocals")
        
        if request.prompt:
            prompt_parts.append(f"Theme: {request.prompt}")
        
        return " ".join(prompt_parts) + "."
    
    async def _generate_composition(self, prompt: str, request: MusicGenerationRequest) -> Dict[str, Any]:
        """Generate musical composition metadata"""
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            composition_prompt = f"""
            Create a detailed musical composition based on this prompt: {prompt}
            
            Please provide a JSON response with:
            - tempo (BPM)
            - key (musical key)
            - time_signature
            - instruments (array of instruments)
            - structure (verse, chorus, bridge, etc.)
            - chord_progressions
            - musical_techniques
            - arrangement_notes
            
            Style: {request.style}
            Mood: {request.mood}
            Duration: {request.duration} seconds
            """
            
            response = await asyncio.to_thread(
                model.generate_content,
                composition_prompt
            )
            
            # Parse composition response (would be actual JSON in real implementation)
            composition = {
                "tempo": request.tempo or self._get_default_tempo(request.style),
                "key": request.key or self._get_default_key(request.mood),
                "time_signature": "4/4",
                "instruments": request.instruments or self._get_default_instruments(request.style),
                "structure": ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
                "composition_notes": response.text if response.text else "AI-generated composition"
            }
            
            return composition
            
        except Exception as e:
            logger.error(f"Composition generation failed: {e}")
            return self._get_default_composition(request)
    
    async def _generate_audio(self, composition: Dict[str, Any], request: MusicGenerationRequest) -> Dict[str, Any]:
        """Generate actual audio file"""
        # In real implementation, this would call Google Lyria API
        # For now, simulate audio generation
        
        await asyncio.sleep(2)  # Simulate processing time
        
        # Generate simulated waveform data
        import math
        import random
        
        sample_rate = 44100
        duration_samples = int(request.duration * sample_rate)
        waveform = []
        
        for i in range(min(duration_samples, 1000)):  # Limit for demo
            # Simple sine wave with some randomness
            t = i / sample_rate
            frequency = 440  # A4 note
            amplitude = 0.5 * math.sin(2 * math.pi * frequency * t)
            amplitude += 0.1 * random.uniform(-1, 1)  # Add some noise
            waveform.append(amplitude)
        
        # Simulate file URLs
        audio_filename = f"{request.style}_{request.mood}_{int(asyncio.get_event_loop().time())}.mp3"
        preview_filename = f"preview_{audio_filename}"
        
        return {
            "audio_url": f"https://storage.googleapis.com/veogen-music/{audio_filename}",
            "preview_url": f"https://storage.googleapis.com/veogen-music/{preview_filename}",
            "waveform_data": waveform,
            "sheet_music_url": f"https://storage.googleapis.com/veogen-music/sheet_{audio_filename}.pdf"
        }
    
    async def _generate_lyrics(self, request: MusicGenerationRequest) -> Optional[str]:
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
