"""
Enhanced logging configuration for VeoGen with structured logging
"""
import logging
import logging.config
import json
import sys
from datetime import datetime
from typing import Dict, Any
import os

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'service': 'veogen-backend'
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
                
        return json.dumps(log_entry)

class VideoGenerationFormatter(logging.Formatter):
    """
    Specialized formatter for video generation logs
    """
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'service': 'video-generation',
            'message': record.getMessage()
        }
        
        # Add video-specific fields
        video_fields = ['job_id', 'style', 'status', 'duration', 'progress', 'error_type']
        for field in video_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
                
        return json.dumps(log_entry)

class MovieMakerFormatter(logging.Formatter):
    """
    Specialized formatter for movie maker logs
    """
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'service': 'movie-maker',
            'message': record.getMessage()
        }
        
        # Add movie-specific fields
        movie_fields = ['project_id', 'scene_id', 'style', 'status', 'progress', 'scene_type']
        for field in movie_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
                
        return json.dumps(log_entry)

class FFmpegFormatter(logging.Formatter):
    """
    Specialized formatter for FFmpeg operation logs
    """
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'service': 'ffmpeg',
            'message': record.getMessage()
        }
        
        # Add FFmpeg-specific fields
        ffmpeg_fields = ['operation_type', 'input_file', 'output_file', 'duration', 'error_code']
        for field in ffmpeg_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
                
        return json.dumps(log_entry)

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': JSONFormatter,
        },
        'video_generation': {
            '()': VideoGenerationFormatter,
        },
        'movie_maker': {
            '()': MovieMakerFormatter,
        },
        'ffmpeg': {
            '()': FFmpegFormatter,
        },
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': sys.stdout
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        },
        'video_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/video_generation.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'video_generation'
        },
        'movie_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/movie_maker.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'movie_maker'
        },
        'ffmpeg_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/ffmpeg.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'ffmpeg'
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/error.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'json'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        },
        'app.services.video': {
            'handlers': ['video_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'app.services.movie_maker': {
            'handlers': ['movie_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'app.services.ffmpeg': {
            'handlers': ['ffmpeg_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'uvicorn': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'fastapi': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

def setup_logging():
    """Setup logging configuration"""
    # Ensure log directory exists
    os.makedirs('/app/logs', exist_ok=True)
    
    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Get root logger
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized", extra={
        'service': 'veogen-backend',
        'component': 'logging'
    })

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

# Utility functions for structured logging
def log_video_generation_start(logger: logging.Logger, job_id: str, style: str, prompt: str):
    """Log video generation start"""
    logger.info("Video generation started", extra={
        'job_id': job_id,
        'style': style,
        'status': 'started',
        'prompt_length': len(prompt)
    })

def log_video_generation_progress(logger: logging.Logger, job_id: str, progress: float):
    """Log video generation progress"""
    logger.info("Video generation progress", extra={
        'job_id': job_id,
        'progress': progress,
        'status': 'in_progress'
    })

def log_video_generation_complete(logger: logging.Logger, job_id: str, style: str, duration: float, output_file: str):
    """Log video generation completion"""
    logger.info("Video generation completed", extra={
        'job_id': job_id,
        'style': style,
        'status': 'completed',
        'duration': duration,
        'output_file': output_file
    })

def log_video_generation_error(logger: logging.Logger, job_id: str, style: str, error: str, error_type: str = 'unknown'):
    """Log video generation error"""
    logger.error("Video generation failed", extra={
        'job_id': job_id,
        'style': style,
        'status': 'failed',
        'error': error,
        'error_type': error_type
    })

def log_movie_project_start(logger: logging.Logger, project_id: str, style: str, scene_count: int):
    """Log movie project start"""
    logger.info("Movie project started", extra={
        'project_id': project_id,
        'style': style,
        'status': 'started',
        'scene_count': scene_count
    })

def log_movie_scene_complete(logger: logging.Logger, project_id: str, scene_id: str, scene_type: str):
    """Log movie scene completion"""
    logger.info("Movie scene completed", extra={
        'project_id': project_id,
        'scene_id': scene_id,
        'scene_type': scene_type,
        'status': 'scene_completed'
    })

def log_ffmpeg_operation(logger: logging.Logger, operation_type: str, input_file: str, output_file: str, duration: float = None, error: str = None):
    """Log FFmpeg operation"""
    extra = {
        'operation_type': operation_type,
        'input_file': input_file,
        'output_file': output_file
    }
    
    if duration is not None:
        extra['duration'] = duration
        
    if error:
        extra['error'] = error
        extra['status'] = 'failed'
        logger.error("FFmpeg operation failed", extra=extra)
    else:
        extra['status'] = 'completed'
        logger.info("FFmpeg operation completed", extra=extra)

def log_image_generation_event(logger, event: str, job_id: str, **kwargs):
    """Log image generation events with structured data"""
    extra = {
        'component': 'image_generation',
        'event': event,
        'job_id': job_id,
        **kwargs
    }
    
    if event == "started":
        logger.info("Image generation started", extra=extra)
    elif event == "completed":
        logger.info("Image generation completed", extra=extra)
    elif event == "failed":
        logger.error("Image generation failed", extra=extra)
    else:
        logger.info("Image generation event", extra=extra)

def log_music_generation_event(logger, event: str, job_id: str, **kwargs):
    """Log music generation events with structured data"""
    extra = {
        'component': 'music_generation',
        'event': event,
        'job_id': job_id,
        **kwargs
    }
    
    if event == "started":
        logger.info("Music generation started", extra=extra)
    elif event == "completed":
        logger.info("Music generation completed", extra=extra)
    elif event == "failed":
        logger.error("Music generation failed", extra=extra)
    else:
        logger.info("Music generation event", extra=extra)
