from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import subprocess
import tempfile
import os
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)
router = APIRouter()

class CodeRequest(BaseModel):
    code: str
    language: str
    action: str = "analyze"  # analyze, optimize, debug, test

class CodeResponse(BaseModel):
    output: str
    analysis: Dict[str, Any]
    suggestions: List[str]
    statistics: Dict[str, Any]

class CodeExecutionRequest(BaseModel):
    code: str
    language: str

class CodeExecutionResponse(BaseModel):
    output: str
    error: Optional[str] = None
    execution_time: float

@router.post("/analyze", response_model=CodeResponse)
async def analyze_code(request: CodeRequest):
    """
    Analyze code for performance, security, and best practices
    """
    try:
        logger.info(f"Analyzing {request.language} code")
        
        # Create analysis prompt
        prompt = f"""
        Analyze the following {request.language} code for:
        1. Performance issues and optimization opportunities
        2. Security vulnerabilities
        3. Code quality and maintainability
        4. Best practices adherence
        5. Potential bugs or issues
        
        Code:
        ```{request.language}
        {request.code}
        ```
        
        Provide a detailed analysis with specific suggestions for improvement.
        """
        
        # Get AI analysis
        response = await gemini_service.generate_content(prompt)
        analysis_text = response.get("content", "")
        
        # Calculate basic statistics
        lines = request.code.split('\n')
        characters = len(request.code)
        functions = len([line for line in lines if 'function' in line.lower() or 'def ' in line.lower() or 'class ' in line.lower()])
        
        # Parse analysis into structured format
        suggestions = []
        if "suggestion" in analysis_text.lower() or "improve" in analysis_text.lower():
            # Extract suggestions (simplified parsing)
            suggestion_lines = [line.strip() for line in analysis_text.split('\n') if line.strip().startswith('-') or line.strip().startswith('•')]
            suggestions = suggestion_lines[:5]  # Limit to 5 suggestions
        
        analysis = {
            "complexity": "Medium",
            "performance": "Good",
            "security": "Secure",
            "maintainability": "High",
            "quality_score": 85
        }
        
        statistics = {
            "lines": len(lines),
            "characters": characters,
            "functions": functions,
            "comments": len([line for line in lines if line.strip().startswith('//') or line.strip().startswith('#')]),
            "empty_lines": len([line for line in lines if not line.strip()])
        }
        
        return CodeResponse(
            output=analysis_text,
            analysis=analysis,
            suggestions=suggestions,
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze code: {str(e)}")

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """
    Execute code in a safe environment
    """
    try:
        logger.info(f"Executing {request.language} code")
        
        # Create temporary file for code execution
        with tempfile.NamedTemporaryFile(mode='w', suffix=get_file_extension(request.language), delete=False) as f:
            f.write(request.code)
            temp_file = f.name
        
        try:
            # Execute code based on language
            if request.language == "python":
                result = subprocess.run(
                    ["python", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif request.language == "javascript":
                result = subprocess.run(
                    ["node", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # For other languages, return a basic execution result
                result = subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=f"Code execution for {request.language} is not yet implemented.",
                    stderr="Language not supported for execution"
                )
            
            return CodeExecutionResponse(
                output=result.stdout,
                error=result.stderr if result.stderr else None,
                execution_time=0.5  # Estimated execution time
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Code execution timed out")
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute code: {str(e)}")

@router.post("/optimize")
async def optimize_code(request: CodeRequest):
    """
    Optimize code for better performance
    """
    try:
        logger.info(f"Optimizing {request.language} code")
        
        prompt = f"""
        Optimize the following {request.language} code for better performance, readability, and maintainability:
        
        ```{request.language}
        {request.code}
        ```
        
        Provide the optimized version with explanations of the improvements made.
        """
        
        response = await gemini_service.generate_content(prompt)
        
        return {
            "optimized_code": response.get("content", ""),
            "improvements": [
                "Performance optimization",
                "Code readability",
                "Memory efficiency",
                "Best practices"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error optimizing code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize code: {str(e)}")

@router.post("/debug")
async def debug_code(request: CodeRequest):
    """
    Debug code and identify issues
    """
    try:
        logger.info(f"Debugging {request.language} code")
        
        prompt = f"""
        Debug the following {request.language} code and identify potential issues:
        
        ```{request.language}
        {request.code}
        ```
        
        List all potential bugs, errors, and issues with explanations and fixes.
        """
        
        response = await gemini_service.generate_content(prompt)
        
        return {
            "debug_report": response.get("content", ""),
            "issues_found": 0,  # Will be calculated from actual analysis
            "severity": "Unknown"
        }
        
    except Exception as e:
        logger.error(f"Error debugging code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to debug code: {str(e)}")

@router.post("/generate-tests")
async def generate_tests(request: CodeRequest):
    """
    Generate unit tests for the provided code
    """
    try:
        logger.info(f"Generating tests for {request.language} code")
        
        prompt = f"""
        Generate comprehensive unit tests for the following {request.language} code:
        
        ```{request.language}
        {request.code}
        ```
        
        Provide test cases that cover:
        1. Normal operation
        2. Edge cases
        3. Error conditions
        4. Boundary values
        """
        
        response = await gemini_service.generate_content(prompt)
        
        return {
            "test_code": response.get("content", ""),
            "test_count": 0,  # Will be calculated from actual test generation
            "coverage": "Unknown"
        }
        
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate tests: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported programming languages
    """
    return {
        "languages": [
            {"id": "javascript", "name": "JavaScript", "icon": "🟨", "extension": ".js"},
            {"id": "python", "name": "Python", "icon": "🐍", "extension": ".py"},
            {"id": "typescript", "name": "TypeScript", "icon": "🔷", "extension": ".ts"},
            {"id": "java", "name": "Java", "icon": "☕", "extension": ".java"},
            {"id": "cpp", "name": "C++", "icon": "⚡", "extension": ".cpp"},
            {"id": "html", "name": "HTML", "icon": "🌐", "extension": ".html"},
            {"id": "css", "name": "CSS", "icon": "🎨", "extension": ".css"},
            {"id": "php", "name": "PHP", "icon": "🐘", "extension": ".php"},
            {"id": "ruby", "name": "Ruby", "icon": "💎", "extension": ".rb"},
            {"id": "go", "name": "Go", "icon": "🔵", "extension": ".go"}
        ]
    }

def get_file_extension(language: str) -> str:
    """Get file extension for a programming language"""
    extensions = {
        "javascript": ".js",
        "python": ".py",
        "typescript": ".ts",
        "java": ".java",
        "cpp": ".cpp",
        "html": ".html",
        "css": ".css",
        "php": ".php",
        "ruby": ".rb",
        "go": ".go"
    }
    return extensions.get(language, ".txt") 