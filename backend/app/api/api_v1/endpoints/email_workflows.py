"""
VeoGen Advanced Email Workflow Endpoints
========================================

FastAPI endpoints for the enhanced email workflow system
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from app.services.advanced_email_workflows import VeoGenEmailOrchestrator
from app.services.auth_service import auth_service
from app.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

# Initialize router and orchestrator
email_router = APIRouter(prefix="/api/email", tags=["Advanced Email Workflows"])
email_orchestrator = VeoGenEmailOrchestrator()

# Request/Response models
class EnhancedRegistrationRequest(BaseModel):
    email: EmailStr
    name: str
    user_id: Optional[str] = None

class SecurityChallengeRequest(BaseModel):
    user_id: str
    action: str

class ChallengeVerifyRequest(BaseModel):
    challenge_id: str
    challenge_code: str

class AdvancedPasswordResetRequest(BaseModel):
    email: EmailStr
    user_id: Optional[str] = None
    name: Optional[str] = None

class ProjectNotificationRequest(BaseModel):
    user_id: str
    project_name: str
    video_url: str

class WeeklyDigestRequest(BaseModel):
    user_id: str
    stats: Dict[str, Any]

class SecurityAlertRequest(BaseModel):
    user_id: str
    activity: str
    location: Optional[str] = None

@email_router.post("/verification/enhanced")
async def send_enhanced_verification(
    request: EnhancedRegistrationRequest, 
    http_request: Request,
    background_tasks: BackgroundTasks
):
    """Send enhanced verification email with welcome series"""
    try:
        user_id = request.user_id or str(uuid.uuid4())
        
        workflow_id = await email_orchestrator.send_enhanced_verification_email(
            user_id=user_id,
            email=request.email,
            name=request.name
        )
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "user_id": user_id,
            "message": "Enhanced verification email sent with onboarding preview",
            "workflow_type": "welcome_series"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")

@email_router.post("/challenge/initiate")
async def initiate_security_challenge(
    request: SecurityChallengeRequest, 
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Initiate security challenge for sensitive actions"""
    try:
        # Get user from database
        user = auth_service.get_user_by_id(db, request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = user.email

        client_ip = http_request.client.host
        user_agent = http_request.headers.get("user-agent", "Unknown")
        
        challenge_id, challenge_code = await email_orchestrator.send_security_challenge(
            user_id=request.user_id,
            email=user_email,
            action=request.action,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        return {
            "success": True,
            "challenge_id": challenge_id,
            "message": f"Security challenge sent for action: {request.action}",
            "expires_in_minutes": 10,
            "workflow_type": "challenge_response"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate security challenge: {str(e)}")

@email_router.post("/challenge/verify")
async def verify_security_challenge(request: ChallengeVerifyRequest):
    """Verify security challenge code"""
    try:
        is_valid = email_orchestrator.verify_challenge_code(
            request.challenge_id,
            request.challenge_code
        )
        
        if is_valid:
            return {
                "success": True,
                "verified": True,
                "message": "Security challenge verified successfully"
            }
        else:
            return {
                "success": False,
                "verified": False,
                "message": "Invalid or expired challenge code"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify challenge: {str(e)}")

@email_router.post("/password-reset/advanced")
async def send_advanced_password_reset(
    request: AdvancedPasswordResetRequest, 
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Send advanced password reset with enhanced security features"""
    try:
        # Look up user by email in database
        user = auth_service.get_user_by_email(db, request.email)
        if not user:
            # For security, don't reveal that the email doesn't exist
            return {
                "success": True,
                "message": "If the email exists, a password reset link has been sent"
            }
        
        user_id = user.id
        user_name = user.full_name or user.username or "User"
        
        client_ip = http_request.client.host
        user_agent = http_request.headers.get("user-agent", "Unknown")
        
        reset_id, reset_token = await email_orchestrator.send_advanced_password_reset(
            user_id=user_id,
            email=request.email,
            name=user_name,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        return {
            "success": True,
            "reset_id": reset_id,
            "message": "Advanced password reset email sent with security features",
            "expires_in_hours": 2,
            "workflow_type": "password_reset_advanced"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send password reset: {str(e)}")

@email_router.post("/password-reset/verify")
async def verify_reset_token(reset_id: str, reset_token: str):
    """Verify password reset token"""
    try:
        is_valid = email_orchestrator.verify_reset_token(reset_id, reset_token)
        
        if is_valid:
            return {
                "success": True,
                "verified": True,
                "message": "Reset token verified successfully"
            }
        else:
            return {
                "success": False,
                "verified": False,
                "message": "Invalid or expired reset token"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify reset token: {str(e)}")

@email_router.post("/notification/project-complete")
async def send_project_completion_notification(
    request: ProjectNotificationRequest,
    db: Session = Depends(get_db)
):
    """Send project completion notification with video download link"""
    try:
        # Get user details from database using user_id
        user = auth_service.get_user_by_id(db, request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = user.email
        user_name = user.full_name or user.username or "User"
        
        notification_id = await email_orchestrator.send_project_completion_notification(
            user_id=request.user_id,
            email=user_email,
            name=user_name,
            project_name=request.project_name,
            video_url=request.video_url
        )
        
        return {
            "success": True,
            "notification_id": notification_id,
            "message": f"Project completion notification sent for: {request.project_name}",
            "workflow_type": "notification"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send project notification: {str(e)}")

@email_router.post("/engagement/weekly-digest")
async def send_weekly_digest(
    request: WeeklyDigestRequest,
    db: Session = Depends(get_db)
):
    """Send weekly engagement digest with user statistics"""
    try:
        # Get user details from database using user_id
        user = auth_service.get_user_by_id(db, request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = user.email
        user_name = user.full_name or user.username or "User"
        
        digest_id = await email_orchestrator.send_weekly_digest(
            user_id=request.user_id,
            email=user_email,
            name=user_name,
            stats=request.stats
        )
        
        return {
            "success": True,
            "digest_id": digest_id,
            "message": "Weekly digest sent successfully",
            "workflow_type": "engagement"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send weekly digest: {str(e)}")

@email_router.post("/security/alert")
async def send_security_alert(
    request: SecurityAlertRequest, 
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Send security alert for suspicious account activity"""
    try:
        # Get user details from database using user_id
        user = auth_service.get_user_by_id(db, request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = user.email
        user_name = user.full_name or user.username or "User"
        
        client_ip = http_request.client.host
        user_agent = http_request.headers.get("user-agent", "Unknown")
        
        alert_id = await email_orchestrator.send_security_alert(
            user_id=request.user_id,
            email=user_email,
            name=user_name,
            activity=request.activity,
            ip_address=client_ip,
            user_agent=user_agent,
            location=request.location
        )
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": f"Security alert sent for: {request.activity}",
            "workflow_type": "security_alert"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send security alert: {str(e)}")

@email_router.get("/track/open/{tracking_id}")
async def track_email_open(tracking_id: str):
    """Track email open events (1x1 pixel endpoint)"""
    try:
        # Log email open event
        email_orchestrator.email_service.logger.info(f"Email opened: {tracking_id}")
        
        # Return 1x1 transparent pixel
        pixel_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00\x3b'
        
        return Response(
            content=pixel_data,
            media_type="image/gif",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    except Exception:
        # Return empty pixel even on error
        return Response(content=b'', media_type="image/gif")

@email_router.get("/workflows/status")
async def get_workflow_status():
    """Get status of active email workflows (admin endpoint)"""
    try:
        active_count = len([w for w in email_orchestrator.active_workflows.values() 
                          if w["status"] == "active"])
        pending_count = len([w for w in email_orchestrator.active_workflows.values() 
                           if w["status"] == "pending"])
        
        return {
            "total_workflows": len(email_orchestrator.active_workflows),
            "active_workflows": active_count,
            "pending_workflows": pending_count,
            "workflow_types": {
                "registration": len([w for w in email_orchestrator.active_workflows.values() 
                                   if w["type"] == "registration"]),
                "challenge": len([w for w in email_orchestrator.active_workflows.values() 
                               if w["type"] == "challenge"]),
                "password_reset": len([w for w in email_orchestrator.active_workflows.values() 
                                     if w["type"] == "password_reset"])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@email_router.post("/test/demo")
async def run_email_demo(db: Session = Depends(get_db)):
    """Demo endpoint to test all email workflows"""
    try:
        # Get Sandra's user account for demo
        demo_user_obj = auth_service.get_user_by_email(db, "sandraschipal@hotmail.com")
        if not demo_user_obj:
            # Fallback to a demo user if Sandra's account doesn't exist
            demo_user = {
                "id": "demo_user_123",
                "email": "sandraschipal@hotmail.com",
                "name": "Sandra"
            }
        else:
            demo_user = {
                "id": demo_user_obj.id,
                "email": demo_user_obj.email,
                "name": demo_user_obj.full_name or demo_user_obj.username or "Sandra"
            }
        
        results = {}
        
        # 1. Enhanced verification
        workflow_id = await email_orchestrator.send_enhanced_verification_email(
            user_id=demo_user["id"],
            email=demo_user["email"],
            name=demo_user["name"]
        )
        results["verification"] = workflow_id
        
        # 2. Security challenge
        challenge_id, challenge_code = await email_orchestrator.send_security_challenge(
            user_id=demo_user["id"],
            email=demo_user["email"],
            action="Delete Account Test",
            ip_address="192.168.1.100",
            user_agent="Demo User Agent"
        )
        results["challenge"] = {"id": challenge_id, "code": challenge_code}
        
        # 3. Password reset
        reset_id, reset_token = await email_orchestrator.send_advanced_password_reset(
            user_id=demo_user["id"],
            email=demo_user["email"],
            name=demo_user["name"],
            ip_address="192.168.1.100",
            user_agent="Demo User Agent"
        )
        results["password_reset"] = {"id": reset_id, "token": reset_token[:20] + "..."}
        
        # 4. Project notification
        notification_id = await email_orchestrator.send_project_completion_notification(
            user_id=demo_user["id"],
            email=demo_user["email"],
            name=demo_user["name"],
            project_name="Demo Video Project",
            video_url="https://veogen.com/demo-video.mp4"
        )
        results["notification"] = notification_id
        
        # 5. Weekly digest
        stats = {
            "videos_created": 5,
            "total_duration": 75,
            "styles_used": 3,
            "projects_completed": 4,
            "achievement": "Demo Creator",
            "achievement_description": "Successfully tested email workflows!"
        }
        digest_id = await email_orchestrator.send_weekly_digest(
            user_id=demo_user["id"],
            email=demo_user["email"],
            name=demo_user["name"],
            stats=stats
        )
        results["weekly_digest"] = digest_id
        
        # 6. Security alert
        alert_id = await email_orchestrator.send_security_alert(
            user_id=demo_user["id"],
            email=demo_user["email"],
            name=demo_user["name"],
            activity="Demo security test",
            ip_address="192.168.1.100",
            user_agent="Demo User Agent",
            location="Test Location"
        )
        results["security_alert"] = alert_id
        
        return {
            "success": True,
            "message": "All email workflows demonstrated successfully!",
            "results": results,
            "check_files": "dev_emails/ folder for generated emails",
            "total_emails_sent": 6
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")
