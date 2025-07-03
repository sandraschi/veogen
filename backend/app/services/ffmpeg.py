import asyncio
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import json

logger = logging.getLogger(__name__)

class FFmpegService:
    """Service for video processing and movie assembly using FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.temp_dir = Path(tempfile.gettempdir()) / "veogen_ffmpeg"
        self.temp_dir.mkdir(exist_ok=True)
    
    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return "ffmpeg"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        possible_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return "ffmpeg"
    
    async def extract_final_frame(self, video_path: str, output_path: Optional[str] = None) -> str:
        """Extract the final frame from a video file"""
        if output_path is None:
            output_path = str(self.temp_dir / f"frame_{os.path.basename(video_path)}.jpg")
        
        try:
            duration_cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-f", "null",
                "-"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *duration_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            stderr_text = stderr.decode()
            
            duration = self._parse_duration(stderr_text)
            if duration is None:
                raise Exception("Could not determine video duration")
            
            seek_time = max(0, duration - 0.1)
            
            cmd = [
                self.ffmpeg_path,
                "-ss", str(seek_time),
                "-i", video_path,
                "-vframes", "1",
                "-y",
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Extracted final frame to {output_path}")
                return output_path
            else:
                error_msg = stderr.decode()
                logger.error(f"Frame extraction failed: {error_msg}")
                raise Exception(f"Frame extraction failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error extracting frame from {video_path}: {e}")
            raise
    
    def _parse_duration(self, ffmpeg_output: str) -> Optional[float]:
        """Parse duration from FFmpeg output"""
        import re
        
        pattern = r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})"
        match = re.search(pattern, ffmpeg_output)
        
        if match:
            hours, minutes, seconds, centiseconds = match.groups()
            total_seconds = (
                int(hours) * 3600 +
                int(minutes) * 60 +
                int(seconds) +
                int(centiseconds) / 100
            )
            return total_seconds
        
        return None
    
    async def apply_style_transfer(
        self, 
        frame_path: str, 
        style: str, 
        output_path: Optional[str] = None
    ) -> str:
        """Apply style transfer to maintain consistency"""
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(frame_path))[0]
            output_path = str(self.temp_dir / f"{base_name}_styled.jpg")
        
        try:
            image = cv2.imread(frame_path)
            if image is None:
                raise Exception(f"Could not load image: {frame_path}")
            
            if style == "anime":
                image = self._enhance_anime_style(image)
            elif style == "wes-anderson":
                image = self._apply_wes_anderson_style(image)
            elif style == "claymation":
                image = self._apply_claymation_style(image)
            
            cv2.imwrite(output_path, image)
            logger.info(f"Applied {style} style to {frame_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error applying style transfer: {e}")
            import shutil
            shutil.copy2(frame_path, output_path)
            return output_path
    
    def _enhance_anime_style(self, image: np.ndarray) -> np.ndarray:
        """Apply anime-style enhancements"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.3)
        image = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
        return image
    
    def _apply_wes_anderson_style(self, image: np.ndarray) -> np.ndarray:
        """Apply Wes Anderson color palette"""
        b, g, r = cv2.split(image)
        b = cv2.multiply(b, 0.9)
        r = cv2.multiply(r, 1.1)
        g = cv2.multiply(g, 1.05)
        return cv2.merge([b, g, r])
    
    def _apply_claymation_style(self, image: np.ndarray) -> np.ndarray:
        """Apply claymation-like effects"""
        image = cv2.GaussianBlur(image, (3, 3), 0)
        image = cv2.convertScaleAbs(image, alpha=0.9, beta=5)
        return image
    
    async def concatenate_videos(
        self, 
        video_paths: List[str], 
        output_path: str,
        with_transitions: bool = True
    ) -> str:
        """Concatenate multiple videos into a single movie"""
        try:
            if len(video_paths) < 1:
                raise Exception("At least one video is required")
            
            file_list_path = str(self.temp_dir / "file_list.txt")
            
            with open(file_list_path, 'w') as f:
                for video_path in video_paths:
                    f.write(f"file '{os.path.abspath(video_path)}'\n")
            
            if with_transitions and len(video_paths) > 1:
                await self._concatenate_with_transitions(video_paths, output_path)
            else:
                cmd = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", file_list_path,
                    "-c", "copy",
                    "-y",
                    output_path
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    error_msg = stderr.decode()
                    logger.error(f"Video concatenation failed: {error_msg}")
                    raise Exception(f"Video concatenation failed: {error_msg}")
            
            try:
                os.remove(file_list_path)
            except:
                pass
            
            logger.info(f"Successfully concatenated {len(video_paths)} videos to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error concatenating videos: {e}")
            raise
    
    async def _concatenate_with_transitions(self, video_paths: List[str], output_path: str):
        """Concatenate videos with smooth transitions"""
        if len(video_paths) == 1:
            import shutil
            shutil.copy2(video_paths[0], output_path)
            return
        
        input_args = []
        for video_path in video_paths:
            input_args.extend(["-i", video_path])
        
        # Simple concatenation with fade transitions
        filter_parts = []
        for i in range(len(video_paths) - 1):
            if i == 0:
                filter_parts.append(f"[0:v][1:v]xfade=transition=fade:duration=0.5:offset=7.5[v01]")
            else:
                filter_parts.append(f"[v0{i}][{i+1}:v]xfade=transition=fade:duration=0.5:offset=7.5[v0{i+1}]")
        
        # Audio concatenation
        audio_inputs = "".join([f"[{i}:a]" for i in range(len(video_paths))])
        filter_parts.append(f"{audio_inputs}concat=n={len(video_paths)}:v=0:a=1[outa]")
        
        filter_complex = ";".join(filter_parts)
        final_video = f"v0{len(video_paths)-1}" if len(video_paths) > 2 else "v01"
        
        cmd = input_args + [
            "-filter_complex", filter_complex,
            "-map", f"[{final_video}]",
            "-map", "[outa]",
            "-y",
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode()
            logger.error(f"Video transition concatenation failed: {error_msg}")
            raise Exception(f"Video transition concatenation failed: {error_msg}")
    
    async def create_thumbnail(self, video_path: str, output_path: Optional[str] = None) -> str:
        """Create a thumbnail from the middle of the video"""
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = str(self.temp_dir / f"{base_name}_thumb.jpg")
        
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-ss", "00:00:04",  # Take frame from 4 seconds in
                "-vframes", "1",
                "-vf", "scale=320:240",
                "-y",
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Created thumbnail: {output_path}")
                return output_path
            else:
                error_msg = stderr.decode()
                logger.error(f"Thumbnail creation failed: {error_msg}")
                raise Exception(f"Thumbnail creation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            raise
    
    async def get_video_info(self, video_path: str) -> Dict:
        """Get video information using ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                info = json.loads(stdout.decode())
                return info
            else:
                error_msg = stderr.decode()
                logger.error(f"Video info extraction failed: {error_msg}")
                raise Exception(f"Video info extraction failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise
    
    def cleanup_temp_files(self, keep_recent: int = 10):
        """Clean up temporary files, keeping only the most recent ones"""
        try:
            temp_files = list(self.temp_dir.glob("*"))
            temp_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep the most recent files
            files_to_delete = temp_files[keep_recent:]
            
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    logger.debug(f"Deleted temp file: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not delete temp file {file_path}: {e}")
                    
        except Exception as e:
            logger.warning(f"Error during temp file cleanup: {e}")

# Global FFmpeg service instance
ffmpeg_service = FFmpegService()
