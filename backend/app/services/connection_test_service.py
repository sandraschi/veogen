"""
Real connection testing service for Google/Gemini APIs
Tests actual API connectivity and functionality
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import google.generativeai as genai
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import aiplatform

from app.config import settings
from app.database import get_user_setting

logger = logging.getLogger(__name__)


class ConnectionTestService:
    """Service for testing real API connections"""

    def __init__(self):
        self.test_results = {}

    async def test_google_auth(self, api_key: Optional[str] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Test Google Cloud authentication"""
        try:
            result = {
                "service": "Google Cloud Auth",
                "status": "testing",
                "details": {},
                "timestamp": asyncio.get_event_loop().time(),
            }

            # Test 1: API Key validation
            if api_key:
                try:
                    # Basic validation for Google API key format
                    if not api_key.startswith("AIza") or len(api_key) < 30:
                        raise ValueError(
                            "Invalid Google API key format. It should start with 'AIza' and be at least 30 characters long."
                        )

                    # Test the API key with a simple request
                    genai.configure(api_key=api_key)

                    try:
                        # Test with a simple model list request
                        models = list(genai.list_models())
                        model_count = len(models)

                        if model_count == 0:
                            raise ValueError(
                                "No models available with this API key. The key may not have the required permissions."
                            )

                        result["details"]["api_key_auth"] = {
                            "status": "success",
                            "models_available": model_count,
                            "message": f"Google API key is valid. {model_count} models available",
                        }

                    except Exception as api_error:
                        error_msg = str(api_error).lower()
                        if "quota" in error_msg:
                            raise ValueError(
                                "API key has exceeded quota or is not enabled for the required APIs. Please check your Google Cloud Console."
                            )
                        elif "permission" in error_msg or "disabled" in error_msg:
                            raise ValueError(
                                "API key is not authorized or the required API is not enabled. Please enable the Generative Language API in Google Cloud Console."
                            )
                        elif "invalid" in error_msg or "malformed" in error_msg:
                            raise ValueError("Invalid Google API key. Please check the key and try again.")
                        else:
                            raise

                except Exception as e:
                    result["details"]["api_key_auth"] = {
                        "status": "failed",
                        "error": str(e),
                        "message": f"Google API key validation failed: {str(e)}",
                        "help": "Please ensure your API key is correct and has the necessary permissions enabled in Google Cloud Console.",
                    }

            # Test 2: Service Account authentication
            try:
                credentials, detected_project = default()
                result["details"]["service_account"] = {
                    "status": "success",
                    "project": detected_project or project_id,
                    "credentials_type": type(credentials).__name__,
                    "message": "Service account authentication successful",
                }

                # Initialize AI Platform with detected credentials
                if project_id or detected_project:
                    aiplatform.init(
                        project=project_id or detected_project,
                        location=settings.GOOGLE_CLOUD_LOCATION,
                        credentials=credentials,
                    )

                    result["details"]["ai_platform"] = {
                        "status": "success",
                        "project": project_id or detected_project,
                        "location": settings.GOOGLE_CLOUD_LOCATION,
                        "message": "AI Platform initialization successful",
                    }

            except DefaultCredentialsError as e:
                result["details"]["service_account"] = {
                    "status": "warning",
                    "error": str(e),
                    "message": "No service account credentials found, using API key only",
                }
            except Exception as e:
                result["details"]["service_account"] = {
                    "status": "failed",
                    "error": str(e),
                    "message": "Service account authentication failed",
                }

            # Determine overall status
            if result["details"].get("api_key_auth", {}).get("status") == "success":
                result["status"] = "success"
                result["message"] = "Google Cloud authentication successful"
            elif result["details"].get("service_account", {}).get("status") == "success":
                result["status"] = "success"
                result["message"] = "Google Cloud authentication successful (service account)"
            else:
                result["status"] = "failed"
                result["message"] = "Google Cloud authentication failed"

            return result

        except Exception as e:
            return {
                "service": "Google Cloud Auth",
                "status": "error",
                "error": str(e),
                "message": "Authentication test failed",
                "timestamp": asyncio.get_event_loop().time(),
            }

    async def test_gemini_api(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Test Gemini API functionality"""
        try:
            result = {
                "service": "Gemini API",
                "status": "testing",
                "details": {},
                "timestamp": asyncio.get_event_loop().time(),
            }

            if not api_key:
                api_key = settings.GEMINI_API_KEY

            if not api_key:
                return {
                    "service": "Gemini API",
                    "status": "failed",
                    "error": "No API key provided",
                    "message": "Gemini API key is required",
                    "timestamp": asyncio.get_event_loop().time(),
                }

            # Configure Gemini
            genai.configure(api_key=api_key)

            # Test 1: List available models with detailed error handling
            try:
                # Basic validation for Gemini API key format
                if not api_key or len(api_key) < 30:
                    raise ValueError("Invalid Gemini API key format. It should be at least 30 characters long.")

                # Configure with the provided API key
                genai.configure(api_key=api_key)

                # Test the API key by listing models
                models = list(genai.list_models())

                if not models:
                    raise ValueError("No models available. The API key may be invalid or have no access to models.")

                gemini_models = [m for m in models if "gemini" in m.name.lower()]

                if not gemini_models:
                    raise ValueError("No Gemini models found. The API key may not have access to Gemini models.")

                result["details"]["models"] = {
                    "status": "success",
                    "total_models": len(models),
                    "gemini_models": len(gemini_models),
                    "model_names": [m.name for m in gemini_models[:5]],  # First 5
                    "message": f"Successfully connected to Gemini API. Found {len(gemini_models)} Gemini models",
                }

            except Exception as e:
                error_msg = str(e).lower()
                detailed_msg = "Failed to list models"
                help_text = "Please check your API key and ensure it has the correct permissions."

                if "api key" in error_msg or "invalid" in error_msg:
                    detailed_msg = "Invalid or unauthorized API key"
                    help_text = "Please verify your Gemini API key is correct and has the necessary permissions."
                elif "quota" in error_msg:
                    detailed_msg = "API quota exceeded"
                    help_text = (
                        "You've exceeded your API quota. Please check your Google Cloud Console for quota limits."
                    )
                elif "permission" in error_msg:
                    detailed_msg = "Insufficient permissions"
                    help_text = "The API key doesn't have permission to access Gemini models. Please check your Google Cloud IAM settings."

                result["details"]["models"] = {
                    "status": "failed",
                    "error": str(e),
                    "message": f"Gemini API connection failed: {detailed_msg}",
                    "help": help_text,
                }

            # Test 2: Simple text generation
            try:
                model = genai.GenerativeModel(settings.GEMINI_FLASH_MODEL)
                response = model.generate_content("Hello, test message")

                result["details"]["text_generation"] = {
                    "status": "success",
                    "response_length": len(response.text),
                    "response_preview": response.text[:100] + "..." if len(response.text) > 100 else response.text,
                    "message": "Text generation successful",
                }

            except Exception as e:
                result["details"]["text_generation"] = {
                    "status": "failed",
                    "error": str(e),
                    "message": "Text generation failed",
                }

            # Test 3: Check for media generation capabilities
            try:
                models = list(genai.list_models())
                video_models = [
                    m
                    for m in models
                    if any(keyword in m.name.lower() for keyword in ["veo", "video", "imagen", "image"])
                ]

                result["details"]["media_capabilities"] = {
                    "status": "success" if video_models else "warning",
                    "video_models": len(video_models),
                    "model_names": [m.name for m in video_models],
                    "message": f"Found {len(video_models)} media generation models"
                    if video_models
                    else "No media models found",
                }

            except Exception as e:
                result["details"]["media_capabilities"] = {
                    "status": "failed",
                    "error": str(e),
                    "message": "Failed to check media capabilities",
                }

            # Determine overall status
            if result["details"].get("text_generation", {}).get("status") == "success":
                result["status"] = "success"
                result["message"] = "Gemini API is working correctly"
            else:
                result["status"] = "failed"
                result["message"] = "Gemini API test failed"

            return result

        except Exception as e:
            return {
                "service": "Gemini API",
                "status": "error",
                "error": str(e),
                "message": "Gemini API test failed",
                "timestamp": asyncio.get_event_loop().time(),
            }

    async def run_full_connection_test(self, db_session=None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Run complete connection test for all services"""
        try:
            logger.info("🔍 Starting comprehensive connection test...")

            # Get API keys from user settings or environment
            google_api_key = None
            gemini_api_key = None
            project_id = None

            if db_session and user_id:
                google_api_key = get_user_setting(db_session, user_id, "google_api_key")
                gemini_api_key = get_user_setting(db_session, user_id, "gemini_api_key")
                project_id = get_user_setting(db_session, user_id, "google_cloud_project")

            # Fallback to environment variables
            google_api_key = google_api_key or settings.GOOGLE_API_KEY
            gemini_api_key = gemini_api_key or settings.GEMINI_API_KEY
            project_id = project_id or settings.GOOGLE_CLOUD_PROJECT

            # Run tests
            auth_result = await self.test_google_auth(google_api_key, project_id)
            gemini_result = await self.test_gemini_api(gemini_api_key)

            # Process results
            results = {
                "timestamp": asyncio.get_event_loop().time(),
                "overall_status": "success",
                "tests_run": 2,
                "tests_passed": 0,
                "tests_failed": 0,
                "details": {"google_auth": auth_result, "gemini_api": gemini_result},
            }

            for result in [auth_result, gemini_result]:
                if result.get("status") == "success":
                    results["tests_passed"] += 1
                else:
                    results["tests_failed"] += 1

            # Determine overall status
            if results["tests_failed"] == 0:
                results["overall_status"] = "success"
                results["message"] = "All connection tests passed ✅"
            elif results["tests_passed"] > 0:
                results["overall_status"] = "partial"
                results["message"] = f"Partial success: {results['tests_passed']}/{results['tests_run']} tests passed ⚠️"
            else:
                results["overall_status"] = "failed"
                results["message"] = "All connection tests failed ❌"

            # Store results for later retrieval
            self.test_results = results

            logger.info(f"✅ Connection test completed: {results['message']}")
            return results

        except Exception as e:
            error_result = {
                "timestamp": asyncio.get_event_loop().time(),
                "overall_status": "error",
                "error": str(e),
                "message": "Connection test framework failed",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "details": {},
            }

            logger.error(f"❌ Connection test failed: {e}")
            return error_result


# Global connection test service instance
connection_test_service = ConnectionTestService()
