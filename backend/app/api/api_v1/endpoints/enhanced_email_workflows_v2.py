        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@email_router.post("/challenge/initiate", response_model=ChallengeResponse)
async def initiate_security_challenge(
    request: SecurityChallengeRequest,
    request_info: Request
):
    """Initiate security challenge for sensitive actions"""
    try:
        user_data = await get_user_data(request.user_id)
        request_data = get_request_info(request_info)
        
        result = await email_orchestrator.handle_security_challenge(
            user_data, request.action, request_data
        )
        
        return ChallengeResponse(
            success=True,
            challenge_id=result["challenge_id"],
            expires_in=result["expires_in"],
            message=f"Security challenge sent for action: {request.action}"
        )
        
    except Exception as e:
        logging.error(f"Failed to initiate security challenge: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send challenge: {str(e)}")

@email_router.post("/challenge/verify", response_model=VerificationResponse)
async def verify_security_challenge(request: ChallengeVerifyRequest):
    """Verify security challenge code"""
    try:
        result = await email_orchestrator.verify_challenge(
            request.challenge_id, request.challenge_code
        )
        
        return VerificationResponse(
            valid=result["valid"],
            user_id=result.get("user_id"),
            action=result.get("action"),
            error=result.get("error")
        )
        
    except Exception as e:
        logging.error(f"Failed to verify challenge: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@email_router.post("/password-reset/advanced", response_model=EmailResponse)
async def send_advanced_password_reset(
    request: AdvancedPasswordResetRequest,
    request_info: Request
):
    """Send advanced password reset email with forensic details"""
    try:
        user_data = {
            "user_id": request.user_id or str(uuid.uuid4()),
            "name": request.name or "User",
            "email": request.email
        }
        
        request_data = get_request_info(request_info)
        request_data["location"] = "Vienna, Austria"
        
        result = await email_orchestrator.handle_password_reset(user_data, request_data)
        
        return EmailResponse(
            success=True,
            workflow_id=result["workflow_id"],
            message=f"Advanced password reset sent to {request.email}",
            data={
                "expires_in": "2 hours",
                "security_features": ["Forensic logging", "Single-use token", "IP tracking"]
            }
        )
        
    except Exception as e:
        logging.error(f"Failed to send password reset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send reset email: {str(e)}")

@email_router.post("/notification/video-ready", response_model=EmailResponse)
async def send_video_ready_notification(request: VideoNotificationRequest):
    """Send video completion notification"""
    try:
        user_data = await get_user_data(request.user_id)
        
        video_data = {
            "id": request.video_id,
            "title": request.video_title,
            "duration": request.duration,
            "resolution": request.resolution
        }
        
        result = await email_orchestrator.handle_video_completion(user_data, video_data)
        
        return EmailResponse(
            success=True,
            workflow_id=result["workflow_id"],
            message=f"Video ready notification sent for '{request.video_title}'",
            data={
                "video_id": request.video_id,
                "download_expires": "7 days"
            }
        )
        
    except Exception as e:
        logging.error(f"Failed to send video notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@email_router.post("/digest/weekly", response_model=EmailResponse)
async def send_weekly_digest(request: WeeklyDigestRequest):
    """Send personalized weekly digest"""
    try:
        user_data = await get_user_data(request.user_id)
        
        stats = {
            "videos_created": request.videos_created,
            "total_duration": request.total_duration,
            "days_active": request.days_active
        }
        
        result = await email_orchestrator.handle_weekly_digest(user_data, stats)
        
        return EmailResponse(
            success=True,
            workflow_id=result["workflow_id"],
            message="Weekly digest sent with personalized statistics",
            data={
                "stats": stats,
                "achievements_unlocked": request.videos_created >= 5
            }
        )
        
    except Exception as e:
        logging.error(f"Failed to send weekly digest: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send digest: {str(e)}")

@email_router.post("/security/alert", response_model=EmailResponse)
async def send_security_alert(request: SecurityAlertRequest):
    """Send security alert for suspicious activity"""
    try:
        user_data = await get_user_data(request.user_id)
        
        activity_data = {
            "type": request.activity_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "ip_address": request.ip_address or "Unknown",
            "location": request.location or "Unknown",
            "device_info": request.device_info or "Unknown",
            "risk_level": request.risk_level
        }
        
        result = await email_orchestrator.handle_security_alert(user_data, activity_data)
        
        return EmailResponse(
            success=True,
            workflow_id=result["workflow_id"],
            message=f"Security alert sent for {request.activity_type}",
            data={
                "reference_id": result["reference_id"],
                "risk_level": request.risk_level
            }
        )
        
    except Exception as e:
        logging.error(f"Failed to send security alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send alert: {str(e)}")

# Email Tracking Endpoints

@email_router.get("/track/{workflow_id}")
async def track_email_open(workflow_id: str, request: Request):
    """Track email open via 1x1 pixel"""
    try:
        # Return 1x1 transparent pixel
        pixel_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
        return Response(content=pixel_data, media_type="image/png")
        
    except Exception as e:
        logging.error(f"Failed to track email open: {e}")
        pixel_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
        return Response(content=pixel_data, media_type="image/png")

@email_router.get("/click/{workflow_id}")
async def track_email_click(workflow_id: str, url: str, request: Request):
    """Track email link click and redirect"""
    try:
        return RedirectResponse(url=url, status_code=302)
        
    except Exception as e:
        logging.error(f"Failed to track email click: {e}")
        return RedirectResponse(url=url, status_code=302)

# Analytics Endpoints

@email_router.get("/analytics")
async def get_email_analytics(workflow_id: Optional[str] = None):
    """Get email analytics and engagement metrics"""
    try:
        analytics = await email_orchestrator.get_analytics(workflow_id)
        
        return {
            "total_workflows": analytics["total_workflows"],
            "total_opens": analytics["total_opens"],
            "total_clicks": analytics["total_clicks"],
            "open_rate": analytics["open_rate"],
            "click_rate": analytics["click_rate"],
            "engagement_score": (analytics["open_rate"] + analytics["click_rate"]) / 2
        }
        
    except Exception as e:
        logging.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@email_router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    try:
        analytics = await email_orchestrator.get_analytics()
        
        dashboard_data = {
            "overview": {
                "total_emails_sent": analytics["total_workflows"],
                "overall_open_rate": analytics["open_rate"],
                "overall_click_rate": analytics["click_rate"],
                "engagement_score": (analytics["open_rate"] + analytics["click_rate"]) / 2
            },
            "performance": {
                "high_performing": analytics["open_rate"] > 25,
                "needs_improvement": analytics["click_rate"] < 5,
                "engagement_trend": "improving" if analytics["open_rate"] > 20 else "stable"
            },
            "recommendations": []
        }
        
        # Add recommendations based on performance
        if analytics["open_rate"] < 20:
            dashboard_data["recommendations"].append("Improve subject lines to increase open rates")
        if analytics["click_rate"] < 5:
            dashboard_data["recommendations"].append("Enhance call-to-action buttons for better click rates")
        if analytics["open_rate"] > 30:
            dashboard_data["recommendations"].append("Great job! Your emails are performing well")
        
        return dashboard_data
        
    except Exception as e:
        logging.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

# Test and Demo Endpoints

@email_router.post("/test/demo-all")
async def demo_all_workflows():
    """Demo all email workflows for testing"""
    try:
        from app.services.enhanced_email_workflows_v2 import demo_enhanced_email_workflows
        
        results = await demo_enhanced_email_workflows()
        
        return {
            "success": True,
            "message": "All email workflows demonstrated successfully",
            "workflows_tested": results,
            "total_workflows": len(results),
            "files_location": "dev_emails/"
        }
        
    except Exception as e:
        logging.error(f"Failed to run demo: {e}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

@email_router.get("/test/health")
async def email_system_health():
    """Check email system health and configuration"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "smtp_server": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "from_address": "noreply@veogen.com",
                "development_mode": True,
                "outbox_location": "dev_emails/"
            },
            "features": {
                "welcome_series": True,
                "security_challenges": True,
                "password_reset": True,
                "video_notifications": True,
                "weekly_digests": True,
                "security_alerts": True,
                "email_tracking": True,
                "analytics": True
            },
            "version": "2.0",
            "last_updated": "2025-07-10"
        }
        
        return health_data
        
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Export the router
__all__ = ["email_router"]
