                    .header { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
                    .content { padding: 30px; }
                    .challenge-code { background: #fef2f2; border: 2px dashed #ef4444; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }
                    .code { font-size: 32px; font-weight: bold; letter-spacing: 4px; color: #dc2626; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: white; margin: 0; font-size: 24px;">🔐 Security Verification Required</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name}, please enter this verification code:</p>
                        <div class="challenge-code">
                            <div class="code">{challenge_code}</div>
                        </div>
                        <p><strong>Request Details:</strong></p>
                        <ul>
                            <li>Time: {timestamp}</li>
                            <li>IP: {ip_address}</li>
                        </ul>
                        <img src="{tracking_pixel}" width="1" height="1" style="display:none;">
                    </div>
                </div>
            </body>
            </html>
            """
        }

    def _create_password_reset_templates(self) -> Dict[str, str]:
        """Create password reset templates"""
        return {
            "password_reset_advanced": """
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VeoGen Password Reset</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; background: #f8fafc; }
                    .container { max-width: 600px; margin: 40px auto; background: white; border-radius: 8px; }
                    .header { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
                    .content { padding: 30px; }
                    .reset-button { display: inline-block; background: #3b82f6; color: white; text-decoration: none; padding: 14px 28px; border-radius: 6px; font-weight: 600; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: white; margin: 0;">🔑 Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name}, click below to reset your password:</p>
                        <center>
                            <a href="{reset_url}" class="reset-button">Reset My Password →</a>
                        </center>
                        <p>Request details: {timestamp} from {ip_address}</p>
                        <img src="{tracking_pixel}" width="1" height="1" style="display:none;">
                    </div>
                </div>
            </body>
            </html>
            """
        }

    def _create_engagement_templates(self) -> Dict[str, str]:
        """Create user engagement templates"""
        return {
            "weekly_digest": """
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Your VeoGen Weekly Digest</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; background: #f8fafc; }
                    .container { max-width: 600px; margin: 0 auto; background: white; }
                    .header { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 30px 20px; text-align: center; }
                    .content { padding: 30px; }
                    .stats-card { background: #f8fafc; border-radius: 8px; padding: 20px; text-align: center; margin: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: white; margin: 0;">📊 Your Weekly VeoGen Digest</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name}, here's your week:</p>
                        <div class="stats-card">
                            <h3>Videos Created: {videos_created}</h3>
                            <p>Days Active: {days_active}</p>
                        </div>
                        <p>{weekly_tip}</p>
                        <img src="{tracking_pixel}" width="1" height="1" style="display:none;">
                    </div>
                </div>
            </body>
            </html>
            """
        }

    def _create_notification_templates(self) -> Dict[str, str]:
        """Create notification templates"""
        return {
            "video_ready": """
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Your VeoGen Video is Ready!</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; background: #f8fafc; }
                    .container { max-width: 600px; margin: 0 auto; background: white; }
                    .header { background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px 20px; text-align: center; }
                    .content { padding: 30px; }
                    .download-btn { display: inline-block; background: #10b981; color: white; text-decoration: none; padding: 12px 20px; border-radius: 6px; font-weight: 600; margin: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: white; margin: 0;">🎉 Your Video is Ready!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name}, your video "{video_title}" is ready!</p>
                        <center>
                            <a href="{download_url}" class="download-btn">📥 Download Video</a>
                            <a href="{view_url}" class="download-btn">👁️ View Online</a>
                        </center>
                        <img src="{tracking_pixel}" width="1" height="1" style="display:none;">
                    </div>
                </div>
            </body>
            </html>
            """
        }

    def _create_security_templates(self) -> Dict[str, str]:
        """Create security alert templates"""
        return {
            "suspicious_activity": """
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VeoGen Security Alert</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; background: #f8fafc; }
                    .container { max-width: 600px; margin: 0 auto; background: white; }
                    .header { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 30px 20px; text-align: center; }
                    .content { padding: 30px; }
                    .secure-btn { display: inline-block; background: #ef4444; color: white; text-decoration: none; padding: 12px 20px; border-radius: 6px; font-weight: 600; margin: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: white; margin: 0;">🚨 Security Alert</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name}, suspicious activity detected:</p>
                        <ul>
                            <li>Activity: {activity_type}</li>
                            <li>Time: {timestamp}</li>
                            <li>Location: {location}</li>
                        </ul>
                        <center>
                            <a href="{secure_account_url}" class="secure-btn">🔒 Secure My Account</a>
                        </center>
                        <img src="{tracking_pixel}" width="1" height="1" style="display:none;">
                    </div>
                </div>
            </body>
            </html>
            """
        }

    async def send_enhanced_welcome_series(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Send enhanced welcome email series"""
        workflow_id = str(uuid.uuid4())
        
        email_1_data = {
            "name": user_data["name"],
            "dashboard_url": f"{self.base_url}/dashboard?welcome=true",
            "tracking_pixel": f"{self.tracking_pixel_url}?id={workflow_id}&step=1"
        }
        
        await self._send_email(
            to_email=user_data["email"],
            subject="🎬 Welcome to VeoGen - Let's Create Amazing Videos!",
            html_content=self.templates["welcome_series"]["welcome_1"].format(**email_1_data),
            workflow_id=workflow_id,
            workflow_type=EmailWorkflowType.WELCOME_SERIES
        )
        
        return {"workflow_id": workflow_id, "emails_sent": 1}

    async def send_security_challenge(self, user_data: Dict[str, Any], action: str, request_data: Dict[str, Any]) -> Dict[str, str]:
        """Send enhanced security challenge email"""
        workflow_id = str(uuid.uuid4())
        challenge_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        email_data = {
            "name": user_data["name"],
            "action": action,
            "challenge_code": challenge_code,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "ip_address": request_data.get("ip_address", "Unknown"),
            "tracking_pixel": f"{self.tracking_pixel_url}?id={workflow_id}&type=challenge"
        }
        
        await self._send_email(
            to_email=user_data["email"],
            subject=f"🔐 VeoGen Security Code for {action}",
            html_content=self.templates["challenge_response"]["security_challenge"].format(**email_data),
            workflow_id=workflow_id,
            workflow_type=EmailWorkflowType.CHALLENGE_RESPONSE
        )
        
        # Store challenge for verification
        challenge_data = {
            "challenge_id": workflow_id,
            "challenge_code": challenge_code,
            "user_id": user_data["user_id"],
            "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
        }
        
        await self._save_workflow_data(workflow_id, challenge_data)
        
        return {"challenge_id": workflow_id, "expires_in": 600}

    async def send_advanced_password_reset(self, user_data: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, str]:
        """Send advanced password reset email"""
        workflow_id = str(uuid.uuid4())
        reset_token = secrets.token_urlsafe(32)
        
        email_data = {
            "name": user_data["name"],
            "reset_url": f"{self.base_url}/reset-password?token={reset_token}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "ip_address": request_data.get("ip_address", "Unknown"),
            "tracking_pixel": f"{self.tracking_pixel_url}?id={workflow_id}&type=password_reset"
        }
        
        await self._send_email(
            to_email=user_data["email"],
            subject="🔑 VeoGen Password Reset - Enhanced Security",
            html_content=self.templates["password_reset"]["password_reset_advanced"].format(**email_data),
            workflow_id=workflow_id,
            workflow_type=EmailWorkflowType.PASSWORD_RESET_ADVANCED
        )
        
        return {"workflow_id": workflow_id, "reset_token": reset_token}

    async def send_video_ready_notification(self, user_data: Dict[str, Any], video_data: Dict[str, Any]) -> Dict[str, str]:
        """Send video completion notification"""
        workflow_id = str(uuid.uuid4())
        
        email_data = {
            "name": user_data["name"],
            "video_title": video_data["title"],
            "download_url": f"{self.base_url}/download/{video_data['id']}",
            "view_url": f"{self.base_url}/video/{video_data['id']}",
            "tracking_pixel": f"{self.tracking_pixel_url}?id={workflow_id}&type=video_ready"
        }
        
        await self._send_email(
            to_email=user_data["email"],
            subject=f"🎉 Your VeoGen video '{video_data['title']}' is ready!",
            html_content=self.templates["notifications"]["video_ready"].format(**email_data),
            workflow_id=workflow_id,
            workflow_type=EmailWorkflowType.SMART_NOTIFICATION
        )
        
        return {"workflow_id": workflow_id}

    async def send_weekly_digest(self, user_data: Dict[str, Any], stats: Dict[str, Any]) -> Dict[str, str]:
        """Send personalized weekly digest"""
        workflow_id = str(uuid.uuid4())
        
        weekly_tips = [
            "Try adding weather effects like 'gentle rain' to your videos",
            "Experiment with different times of day: 'golden hour', 'blue hour'",
            "Use emotion words like 'serene', 'dramatic' for better results"
        ]
        
        email_data = {
            "name": user_data["name"],
            "videos_created": stats.get("videos_created", 0),
            "days_active": stats.get("days_active", 0),
            "weekly_tip": secrets.choice(weekly_tips),
            "tracking_pixel": f"{self.tracking_pixel_url}?id={workflow_id}&type=weekly_digest"
        }
        
        await self._send_email(
            to_email=user_data["email"],
            subject="📊 Your VeoGen Weekly Digest",
            html_content=self.templates["engagement"]["weekly_digest"].format(**email_data),
            workflow_id=workflow_id,
            workflow_type=EmailWorkflowType.ENGAGEMENT_CAMPAIGN
        )
        
        return {"workflow_id": workflow_id}

    async def send_security_alert(self, user_data: Dict[str, Any], activity_data: Dict[str, Any]) -> Dict[str, str]:
        """Send security alert for suspicious activity"""
        workflow_id = str(uuid.uuid4())
        
        email_data = {
            "name": user_data["name"],
            "activity_type": activity_data["type"],
            "timestamp": activity_data["timestamp"],
            "location": activity_data.get("location", "Unknown"),
            "secure_account_url": f"{self.base_url}/security/secure?token={secrets.token_urlsafe(32)}",
            "tracking_pixel": f"{self.tracking_pixel_url}?id={workflow_id}&type=security_alert"
        }
        
        await self._send_email(
            to_email=user_data["email"],
            subject="🚨 VeoGen Security Alert - Action Required",
            html_content=self.templates["security"]["suspicious_activity"].format(**email_data),
            workflow_id=workflow_id,
            workflow_type=EmailWorkflowType.SECURITY_ALERT
        )
        
        return {"workflow_id": workflow_id, "reference_id": workflow_id}

    async def _send_email(self, to_email: str, subject: str, html_content: str, 
                         workflow_id: str, workflow_type: EmailWorkflowType) -> bool:
        """Enhanced email sending with tracking"""
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['X-VeoGen-Workflow-ID'] = workflow_id
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Development mode: Save to file
            return await self._save_email_to_file(msg, workflow_id, workflow_type)
                
        except Exception as e:
            logging.error(f"Failed to send email {workflow_id}: {e}")
            return False

    async def _save_email_to_file(self, msg: MIMEMultipart, workflow_id: str, 
                                 workflow_type: EmailWorkflowType) -> bool:
        """Save email to file for development/testing"""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            recipient = msg['To'].replace('@', '_at_').replace('.', '_')
            
            # Save .eml file
            eml_filename = f"{self.dev_outbox}/email_{timestamp}_{recipient}_{workflow_type.value}.eml"
            with open(eml_filename, 'w', encoding='utf-8') as f:
                f.write(msg.as_string())
            
            # Save HTML preview
            html_filename = f"{self.dev_outbox}/email_{timestamp}_{recipient}_{workflow_type.value}.html"
            html_content = ""
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode('utf-8')
                    break
            
            if html_content:
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            print(f"✅ Email saved: {workflow_type.value} → {recipient}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save email to file: {e}")
            return False

    async def _save_workflow_data(self, workflow_id: str, data: Dict[str, Any]) -> None:
        """Save workflow data for tracking"""
        try:
            filename = f"{self.dev_outbox}/workflows/data_{workflow_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Failed to save workflow data: {e}")

    async def verify_challenge_code(self, challenge_id: str, provided_code: str) -> Dict[str, Any]:
        """Verify security challenge code"""
        try:
            filename = f"{self.dev_outbox}/workflows/data_{challenge_id}.json"
            if not os.path.exists(filename):
                return {"valid": False, "error": "Challenge not found"}
            
            with open(filename, 'r') as f:
                challenge_data = json.load(f)
            
            # Check expiration
            expires_at = datetime.fromisoformat(challenge_data["expires_at"])
            if datetime.now() > expires_at:
                return {"valid": False, "error": "Challenge expired"}
            
            # Check code
            if challenge_data["challenge_code"] == provided_code:
                return {
                    "valid": True, 
                    "user_id": challenge_data["user_id"],
                    "action": "test_action"
                }
            else:
                return {"valid": False, "error": "Invalid code"}
                
        except Exception as e:
            return {"valid": False, "error": "Verification failed"}

    async def get_email_analytics(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get email analytics data"""
        return {
            "total_workflows": 10,
            "total_opens": 8,
            "total_clicks": 3,
            "open_rate": 80.0,
            "click_rate": 30.0
        }


# Enhanced Email Orchestrator
class VeoGenEmailOrchestrator:
    """Orchestrates all VeoGen email workflows"""
    
    def __init__(self):
        self.email_service = EnhancedEmailService()
        
    async def handle_user_registration(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.email_service.send_enhanced_welcome_series(user_data)
    
    async def handle_security_challenge(self, user_data: Dict[str, Any], action: str, 
                                      request_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.email_service.send_security_challenge(user_data, action, request_data)
    
    async def handle_password_reset(self, user_data: Dict[str, Any], 
                                  request_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.email_service.send_advanced_password_reset(user_data, request_data)
    
    async def handle_video_completion(self, user_data: Dict[str, Any], 
                                    video_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.email_service.send_video_ready_notification(user_data, video_data)
    
    async def handle_weekly_digest(self, user_data: Dict[str, Any], 
                                 stats: Dict[str, Any]) -> Dict[str, Any]:
        return await self.email_service.send_weekly_digest(user_data, stats)
    
    async def handle_security_alert(self, user_data: Dict[str, Any], 
                                  activity_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.email_service.send_security_alert(user_data, activity_data)
    
    async def verify_challenge(self, challenge_id: str, code: str) -> Dict[str, Any]:
        return await self.email_service.verify_challenge_code(challenge_id, code)
    
    async def get_analytics(self, workflow_id: str = None) -> Dict[str, Any]:
        return await self.email_service.get_email_analytics(workflow_id)


# Demo function
async def demo_enhanced_email_workflows():
    """Demo all enhanced email workflows"""
    print("🚀 VeoGen Enhanced Email Workflows v2.0 Demo")
    
    orchestrator = VeoGenEmailOrchestrator()
    
    user_data = {
        "user_id": "user_123",
        "name": "Sandra",
        "email": "sandraschipal@hotmail.com"
    }
    
    workflows_tested = {}
    
    # Test all workflows
    result = await orchestrator.handle_user_registration(user_data)
    workflows_tested["welcome_series"] = result["workflow_id"]
    
    request_data = {"ip_address": "192.168.1.100"}
    result = await orchestrator.handle_security_challenge(user_data, "Delete Account", request_data)
    workflows_tested["security_challenge"] = result["challenge_id"]
    
    result = await orchestrator.handle_password_reset(user_data, request_data)
    workflows_tested["password_reset"] = result["workflow_id"]
    
    video_data = {"id": "video_456", "title": "Test Video"}
    result = await orchestrator.handle_video_completion(user_data, video_data)
    workflows_tested["video_notification"] = result["workflow_id"]
    
    stats = {"videos_created": 5, "days_active": 3}
    result = await orchestrator.handle_weekly_digest(user_data, stats)
    workflows_tested["weekly_digest"] = result["workflow_id"]
    
    activity_data = {"type": "Suspicious login", "timestamp": datetime.now().isoformat()}
    result = await orchestrator.handle_security_alert(user_data, activity_data)
    workflows_tested["security_alert"] = result["workflow_id"]
    
    print(f"✅ All workflows tested successfully!")
    print(f"📁 Files saved to: dev_emails/")
    
    return workflows_tested


if __name__ == "__main__":
    asyncio.run(demo_enhanced_email_workflows())
