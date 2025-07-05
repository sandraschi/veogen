"""
Connection Test Service for VeoGen
Comprehensive testing of all MCP servers, API keys, and services
"""

import asyncio
import json
import logging
import os
import subprocess
import aiohttp
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from ..config import settings
from ..database import get_user_setting

logger = logging.getLogger(__name__)

@dataclass
class ConnectionTestResult:
    """Result of a connection test"""
    service_name: str
    status: str  # "success", "error", "warning", "not_available"
    details: str
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    capabilities: Optional[List[str]] = None
    version: Optional[str] = None
    config_info: Optional[Dict[str, Any]] = None

@dataclass
class ApiKeyTestResult:
    """Result of an API key test"""
    key_name: str
    status: str  # "valid", "invalid", "missing", "error"
    details: str
    error_message: Optional[str] = None
    permissions: Optional[List[str]] = None
    quota_info: Optional[Dict[str, Any]] = None

class ConnectionTestService:
    """Service for comprehensive connection testing"""
    
    def __init__(self):
        self.test_results: Dict[str, ConnectionTestResult] = {}
        self.api_key_results: Dict[str, ApiKeyTestResult] = {}
        
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
    
    async def test_all_connections(self, db_session=None, user_id=None) -> Dict[str, Any]:
        """Run comprehensive connection tests"""
        logger.info("Starting comprehensive connection tests")
        
        # Test API keys
        await self._test_api_keys(db_session, user_id)
        
        # Test MCP servers
        await self._test_mcp_servers(db_session, user_id)
        
        # Test external services
        await self._test_external_services(db_session, user_id)
        
        # Test local services
        await self._test_local_services()
        
        # Generate summary
        summary = self._generate_summary()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary,
            "api_keys": {k: asdict(v) for k, v in self.api_key_results.items()},
            "services": {k: asdict(v) for k, v in self.test_results.items()},
            "recommendations": self._generate_recommendations()
        }
    
    async def _test_api_keys(self, db_session=None, user_id=None):
        """Test all API keys"""
        logger.info("Testing API keys")
        
        # Test Gemini API key
        await self._test_gemini_api_key(db_session, user_id)
        
        # Test Google Cloud API key
        await self._test_google_cloud_api_key(db_session, user_id)
        
        # Test Google Cloud Project
        await self._test_google_cloud_project(db_session, user_id)
        
        # Test Google Application Credentials
        await self._test_google_application_credentials()
    
    async def _test_gemini_api_key(self, db_session=None, user_id=None):
        """Test Gemini API key"""
        key = self._get_api_key_from_user_settings(db_session, user_id, "gemini_api_key")
        
        if not key:
            self.api_key_results["gemini_api_key"] = ApiKeyTestResult(
                key_name="gemini_api_key",
                status="missing",
                details="No Gemini API key found in user settings or environment variables",
                error_message="API key not configured"
            )
            return
        
        try:
            start_time = datetime.now()
            
            # Test with a simple API call
            import google.generativeai as genai
            genai.configure(api_key=key)
            
            model = genai.GenerativeModel('gemini-pro')
            response = await asyncio.to_thread(
                model.generate_content,
                "Hello, this is a test message."
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response and response.text:
                self.api_key_results["gemini_api_key"] = ApiKeyTestResult(
                    key_name="gemini_api_key",
                    status="valid",
                    details=f"Gemini API key is valid. Response time: {response_time:.2f}ms",
                    response_time_ms=response_time,
                    permissions=["text_generation", "content_generation"]
                )
            else:
                self.api_key_results["gemini_api_key"] = ApiKeyTestResult(
                    key_name="gemini_api_key",
                    status="error",
                    details="Gemini API key test failed - no response received",
                    error_message="Empty response from API"
                )
                
        except Exception as e:
            self.api_key_results["gemini_api_key"] = ApiKeyTestResult(
                key_name="gemini_api_key",
                status="invalid",
                details=f"Gemini API key test failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_google_cloud_api_key(self, db_session=None, user_id=None):
        """Test Google Cloud API key"""
        key = self._get_api_key_from_user_settings(db_session, user_id, "google_api_key")
        
        if not key:
            self.api_key_results["google_api_key"] = ApiKeyTestResult(
                key_name="google_api_key",
                status="missing",
                details="No Google Cloud API key found in user settings or environment variables",
                error_message="API key not configured"
            )
            return
        
        try:
            start_time = datetime.now()
            
            # Test with Google Cloud AI Platform
            from google.cloud import aiplatform
            
            aiplatform.init(
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
            
            # Test a simple operation
            response = await asyncio.to_thread(
                aiplatform.Model.list,
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.api_key_results["google_api_key"] = ApiKeyTestResult(
                key_name="google_api_key",
                status="valid",
                details=f"Google Cloud API key is valid. Response time: {response_time:.2f}ms",
                response_time_ms=response_time,
                permissions=["aiplatform_access", "model_listing"]
            )
            
        except Exception as e:
            self.api_key_results["google_api_key"] = ApiKeyTestResult(
                key_name="google_api_key",
                status="invalid",
                details=f"Google Cloud API key test failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_google_cloud_project(self, db_session=None, user_id=None):
        """Test Google Cloud Project configuration"""
        project_id = self._get_api_key_from_user_settings(db_session, user_id, "google_cloud_project") or settings.GOOGLE_CLOUD_PROJECT
        
        if not project_id:
            self.api_key_results["google_cloud_project"] = ApiKeyTestResult(
                key_name="google_cloud_project",
                status="missing",
                details="No Google Cloud Project ID configured",
                error_message="Project ID not configured"
            )
            return
        
        try:
            # Test project access
            from google.cloud import aiplatform
            
            aiplatform.init(project=project_id)
            
            # Try to list models to verify project access
            models = await asyncio.to_thread(
                aiplatform.Model.list,
                project=project_id,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
            
            self.api_key_results["google_cloud_project"] = ApiKeyTestResult(
                key_name="google_cloud_project",
                status="valid",
                details=f"Google Cloud Project '{project_id}' is accessible",
                permissions=["project_access", "model_listing"]
            )
            
        except Exception as e:
            self.api_key_results["google_cloud_project"] = ApiKeyTestResult(
                key_name="google_cloud_project",
                status="invalid",
                details=f"Google Cloud Project '{project_id}' access failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_google_application_credentials(self):
        """Test Google Application Credentials"""
        creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        if not creds_path:
            self.api_key_results["google_application_credentials"] = ApiKeyTestResult(
                key_name="google_application_credentials",
                status="missing",
                details="No Google Application Credentials file configured",
                error_message="Credentials file not configured"
            )
            return
        
        if not os.path.exists(creds_path):
            self.api_key_results["google_application_credentials"] = ApiKeyTestResult(
                key_name="google_application_credentials",
                status="invalid",
                details=f"Google Application Credentials file not found: {creds_path}",
                error_message="Credentials file does not exist"
            )
            return
        
        try:
            # Test credentials file
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            
            required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
            missing_fields = [field for field in required_fields if field not in creds_data]
            
            if missing_fields:
                self.api_key_results["google_application_credentials"] = ApiKeyTestResult(
                    key_name="google_application_credentials",
                    status="invalid",
                    details=f"Google Application Credentials file is missing required fields: {missing_fields}",
                    error_message="Invalid credentials file format"
                )
                return
            
            # Test actual authentication
            from google.cloud import aiplatform
            
            aiplatform.init(
                project=creds_data["project_id"],
                location=settings.GOOGLE_CLOUD_LOCATION,
                credentials=creds_path
            )
            
            # Try to list models
            models = await asyncio.to_thread(
                aiplatform.Model.list,
                project=creds_data["project_id"],
                location=settings.GOOGLE_CLOUD_LOCATION
            )
            
            self.api_key_results["google_application_credentials"] = ApiKeyTestResult(
                key_name="google_application_credentials",
                status="valid",
                details=f"Google Application Credentials are valid for project '{creds_data['project_id']}'",
                permissions=["service_account_access", "aiplatform_access"],
                config_info={"project_id": creds_data["project_id"], "client_email": creds_data["client_email"]}
            )
            
        except Exception as e:
            self.api_key_results["google_application_credentials"] = ApiKeyTestResult(
                key_name="google_application_credentials",
                status="invalid",
                details=f"Google Application Credentials test failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_mcp_servers(self, db_session=None, user_id=None):
        """Test all MCP servers"""
        logger.info("Testing MCP servers")
        
        mcp_servers = {
            "veo": {"port": 8081, "binary": "mcp-veo-go", "tools": ["veo_t2v", "veo_i2v"]},
            "imagen": {"port": 8082, "binary": "mcp-imagen-go", "tools": ["imagen_t2i"]},
            "lyria": {"port": 8083, "binary": "mcp-lyria-go", "tools": ["lyria_generate_music"]},
            "chirp": {"port": 8084, "binary": "mcp-chirp3-go", "tools": ["chirp_tts", "list_chirp_voices"]},
            "avtool": {"port": 8085, "binary": "mcp-avtool-go", "tools": ["av_composite"]}
        }
        
        for server_name, config in mcp_servers.items():
            await self._test_mcp_server(server_name, config, db_session, user_id)
    
    async def _test_mcp_server(self, server_name: str, config: Dict[str, Any], db_session=None, user_id=None):
        """Test a specific MCP server"""
        try:
            start_time = datetime.now()
            
            # Test server health endpoint
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{config['port']}/health", timeout=5.0) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if response.status == 200:
                        health_data = await response.json()
                        
                        self.test_results[f"mcp_{server_name}"] = ConnectionTestResult(
                            service_name=f"MCP {server_name.upper()}",
                            status="success",
                            details=f"MCP {server_name} server is running on port {config['port']}. Response time: {response_time:.2f}ms",
                            response_time_ms=response_time,
                            capabilities=config["tools"],
                            version=health_data.get("version", "unknown"),
                            config_info={"port": config["port"], "binary": config["binary"]}
                        )
                    else:
                        self.test_results[f"mcp_{server_name}"] = ConnectionTestResult(
                            service_name=f"MCP {server_name.upper()}",
                            status="error",
                            details=f"MCP {server_name} server returned status {response.status}",
                            error_message=f"HTTP {response.status}",
                            config_info={"port": config["port"], "binary": config["binary"]}
                        )
                        
        except asyncio.TimeoutError:
            self.test_results[f"mcp_{server_name}"] = ConnectionTestResult(
                service_name=f"MCP {server_name.upper()}",
                status="error",
                details=f"MCP {server_name} server connection timeout",
                error_message="Connection timeout",
                config_info={"port": config["port"], "binary": config["binary"]}
            )
        except Exception as e:
            self.test_results[f"mcp_{server_name}"] = ConnectionTestResult(
                service_name=f"MCP {server_name.upper()}",
                status="not_available",
                details=f"MCP {server_name} server is not available: {str(e)}",
                error_message=str(e),
                config_info={"port": config["port"], "binary": config["binary"]}
            )
    
    async def _test_external_services(self, db_session=None, user_id=None):
        """Test external services"""
        logger.info("Testing external services")
        
        # Test Gemini API
        await self._test_gemini_api()
        
        # Test Google Cloud AI Platform
        await self._test_google_cloud_ai_platform()
        
        # Test Google Cloud Storage (if configured)
        await self._test_google_cloud_storage()
    
    async def _test_gemini_api(self):
        """Test Gemini API connectivity"""
        try:
            start_time = datetime.now()
            
            import google.generativeai as genai
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                
                model = genai.GenerativeModel('gemini-pro')
                response = await asyncio.to_thread(
                    model.generate_content,
                    "Test message"
                )
                
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                self.test_results["gemini_api"] = ConnectionTestResult(
                    service_name="Gemini API",
                    status="success",
                    details=f"Gemini API is accessible. Response time: {response_time:.2f}ms",
                    response_time_ms=response_time,
                    capabilities=["text_generation", "content_generation"]
                )
            else:
                self.test_results["gemini_api"] = ConnectionTestResult(
                    service_name="Gemini API",
                    status="not_available",
                    details="Gemini API key not configured",
                    error_message="API key missing"
                )
                
        except Exception as e:
            self.test_results["gemini_api"] = ConnectionTestResult(
                service_name="Gemini API",
                status="error",
                details=f"Gemini API test failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_google_cloud_ai_platform(self):
        """Test Google Cloud AI Platform"""
        try:
            start_time = datetime.now()
            
            from google.cloud import aiplatform
            
            aiplatform.init(
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
            
            # Test model listing
            models = await asyncio.to_thread(
                aiplatform.Model.list,
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.test_results["google_cloud_ai_platform"] = ConnectionTestResult(
                service_name="Google Cloud AI Platform",
                status="success",
                details=f"Google Cloud AI Platform is accessible. Response time: {response_time:.2f}ms",
                response_time_ms=response_time,
                capabilities=["model_management", "deployment", "prediction"],
                config_info={"project": settings.GOOGLE_CLOUD_PROJECT, "location": settings.GOOGLE_CLOUD_LOCATION}
            )
            
        except Exception as e:
            self.test_results["google_cloud_ai_platform"] = ConnectionTestResult(
                service_name="Google Cloud AI Platform",
                status="error",
                details=f"Google Cloud AI Platform test failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_google_cloud_storage(self):
        """Test Google Cloud Storage"""
        try:
            bucket_name = settings.GENMEDIA_BUCKET
            if not bucket_name:
                self.test_results["google_cloud_storage"] = ConnectionTestResult(
                    service_name="Google Cloud Storage",
                    status="not_available",
                    details="Storage bucket not configured",
                    error_message="Bucket name missing"
                )
                return
            
            start_time = datetime.now()
            
            from google.cloud import storage
            
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            
            # Test bucket access
            bucket.reload()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.test_results["google_cloud_storage"] = ConnectionTestResult(
                service_name="Google Cloud Storage",
                status="success",
                details=f"Google Cloud Storage bucket '{bucket_name}' is accessible. Response time: {response_time:.2f}ms",
                response_time_ms=response_time,
                capabilities=["file_storage", "media_storage"],
                config_info={"bucket": bucket_name}
            )
            
        except Exception as e:
            self.test_results["google_cloud_storage"] = ConnectionTestResult(
                service_name="Google Cloud Storage",
                status="error",
                details=f"Google Cloud Storage test failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_local_services(self):
        """Test local services"""
        logger.info("Testing local services")
        
        # Test FFmpeg
        await self._test_ffmpeg()
        
        # Test Gemini CLI
        await self._test_gemini_cli()
        
        # Test database
        await self._test_database()
    
    async def _test_ffmpeg(self):
        """Test FFmpeg availability"""
        try:
            result = await asyncio.create_subprocess_exec(
                "ffmpeg", "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                version_line = stdout.decode().split('\n')[0]
                
                self.test_results["ffmpeg"] = ConnectionTestResult(
                    service_name="FFmpeg",
                    status="success",
                    details=f"FFmpeg is available: {version_line}",
                    capabilities=["video_processing", "audio_processing", "format_conversion"],
                    version=version_line
                )
            else:
                self.test_results["ffmpeg"] = ConnectionTestResult(
                    service_name="FFmpeg",
                    status="not_available",
                    details="FFmpeg is not available",
                    error_message="FFmpeg not installed or not in PATH"
                )
                
        except Exception as e:
            self.test_results["ffmpeg"] = ConnectionTestResult(
                service_name="FFmpeg",
                status="error",
                details=f"FFmpeg test failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_gemini_cli(self):
        """Test Gemini CLI availability"""
        try:
            cli_found = False
            cli_name = None
            
            for name in ["gemini", "gemini-cli", "google-gemini"]:
                result = await asyncio.create_subprocess_exec(
                    name, "--help",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    cli_found = True
                    cli_name = name
                    break
            
            if cli_found:
                self.test_results["gemini_cli"] = ConnectionTestResult(
                    service_name="Gemini CLI",
                    status="success",
                    details=f"Gemini CLI is available: {cli_name}",
                    capabilities=["text_generation", "mcp_integration", "tool_execution"],
                    version=cli_name
                )
            else:
                self.test_results["gemini_cli"] = ConnectionTestResult(
                    service_name="Gemini CLI",
                    status="not_available",
                    details="Gemini CLI is not available",
                    error_message="CLI not installed or not in PATH"
                )
                
        except Exception as e:
            self.test_results["gemini_cli"] = ConnectionTestResult(
                service_name="Gemini CLI",
                status="error",
                details=f"Gemini CLI test failed: {str(e)}",
                error_message=str(e)
            )
    
    async def _test_database(self):
        """Test database connectivity"""
        try:
            start_time = datetime.now()
            
            from ..database import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.test_results["database"] = ConnectionTestResult(
                service_name="Database",
                status="success",
                details=f"Database is accessible. Response time: {response_time:.2f}ms",
                response_time_ms=response_time,
                capabilities=["data_storage", "user_management", "settings_storage"]
            )
            
        except Exception as e:
            self.test_results["database"] = ConnectionTestResult(
                service_name="Database",
                status="error",
                details=f"Database test failed: {str(e)}",
                error_message=str(e)
            )
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all test results"""
        total_tests = len(self.test_results) + len(self.api_key_results)
        successful_tests = 0
        error_tests = 0
        warning_tests = 0
        not_available_tests = 0
        
        # Count service results
        for result in self.test_results.values():
            if result.status == "success":
                successful_tests += 1
            elif result.status == "error":
                error_tests += 1
            elif result.status == "warning":
                warning_tests += 1
            elif result.status == "not_available":
                not_available_tests += 1
        
        # Count API key results
        for result in self.api_key_results.values():
            if result.status == "valid":
                successful_tests += 1
            elif result.status in ["invalid", "error"]:
                error_tests += 1
            elif result.status == "missing":
                not_available_tests += 1
        
        # Determine overall status
        if error_tests == 0 and not_available_tests == 0:
            overall_status = "healthy"
        elif error_tests == 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return {
            "overall_status": overall_status,
            "total_tests": total_tests,
            "successful": successful_tests,
            "errors": error_tests,
            "warnings": warning_tests,
            "not_available": not_available_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check API keys
        if "gemini_api_key" in self.api_key_results:
            result = self.api_key_results["gemini_api_key"]
            if result.status == "missing":
                recommendations.append("Configure GEMINI_API_KEY environment variable or set in user settings")
            elif result.status == "invalid":
                recommendations.append("Check GEMINI_API_KEY validity and permissions")
        
        if "google_api_key" in self.api_key_results:
            result = self.api_key_results["google_api_key"]
            if result.status == "missing":
                recommendations.append("Configure GOOGLE_API_KEY environment variable or set in user settings")
            elif result.status == "invalid":
                recommendations.append("Check GOOGLE_API_KEY validity and permissions")
        
        if "google_cloud_project" in self.api_key_results:
            result = self.api_key_results["google_cloud_project"]
            if result.status == "missing":
                recommendations.append("Configure GOOGLE_CLOUD_PROJECT environment variable")
            elif result.status == "invalid":
                recommendations.append("Check Google Cloud Project access and billing")
        
        # Check MCP servers
        mcp_servers_down = []
        for service_name, result in self.test_results.items():
            if service_name.startswith("mcp_") and result.status in ["error", "not_available"]:
                mcp_servers_down.append(service_name.replace("mcp_", ""))
        
        if mcp_servers_down:
            recommendations.append(f"Start MCP servers: {', '.join(mcp_servers_down)}")
        
        # Check local services
        if "ffmpeg" in self.test_results and self.test_results["ffmpeg"].status == "not_available":
            recommendations.append("Install FFmpeg for video processing capabilities")
        
        if "gemini_cli" in self.test_results and self.test_results["gemini_cli"].status == "not_available":
            recommendations.append("Install Gemini CLI for enhanced functionality")
        
        # Check database
        if "database" in self.test_results and self.test_results["database"].status == "error":
            recommendations.append("Check database configuration and connectivity")
        
        if not recommendations:
            recommendations.append("All systems are properly configured and operational")
        
        return recommendations

# Global instance
connection_test_service = ConnectionTestService() 