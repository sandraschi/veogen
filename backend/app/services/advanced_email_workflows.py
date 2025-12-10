"""
VeoGen Advanced Email Workflow System
=====================================

Enhanced email workflows for professional user experience:
- Multi-step registration with welcome series
- Challenge-response authentication 
- Advanced password reset with security features
- User engagement and notification emails
"""

import os
import uuid
import smtplib
import asyncio
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from enum import Enum
import secrets
import logging

# Email workflow types
class EmailWorkflowType(Enum):
    WELCOME_SERIES = "welcome_series"
    CHALLENGE_RESPONSE = "challenge_response" 
    PASSWORD_RESET_ADVANCED = "password_reset_advanced"
    ENGAGEMENT = "engagement"
    NOTIFICATION = "notification"
    SECURITY_ALERT = "security_alert"

class EmailWorkflowStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"
    CLICKED = "clicked"
    COMPLETED = "completed"
    FAILED = "failed"

# Enhanced Email Service
class AdvancedEmailService:
    def __init__(self):
        self.email_from = os.getenv("EMAIL_FROM", "noreply@veogen.com")
        self.email_smtp = os.getenv("EMAIL_SMTP", "smtp-mail.outlook.com")
        self.email_port = int(os.getenv("EMAIL_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "sandraschipal@hotmail.com")
        self.email_pass = os.getenv("EMAIL_PASS", "vlkaragatumrxsgt")
        self.dev_outbox = os.getenv("EMAIL_DEV_OUTBOX", "dev_emails/")
        self.base_url = os.getenv("BASE_URL", "http://localhost:4710")
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Ensure dev directory exists
        os.makedirs(self.dev_outbox, exist_ok=True)
        os.makedirs(f"{self.dev_outbox}/workflows", exist_ok=True)

    async def send_email_with_tracking(self, to: str, subject: str, body: str, 
                                     html: str = None, workflow_id: str = None,
                                     workflow_type: EmailWorkflowType = None) -> bool:
        """Send email with enhanced tracking and logging"""
        
        # Generate tracking ID
        tracking_id = str(uuid.uuid4())
        # Add tracking pixel to HTML if provided
        if html and workflow_id:
            tracking_pixel = f'<img src="{self.base_url}/api/email/track/open/{tracking_id}" width="1" height="1" style="display:none;">'
            html = html.replace('</body>', f'{tracking_pixel}</body>')

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to
        msg["Message-ID"] = f"<{tracking_id}@veogen.com>"
        msg["X-VeoGen-Workflow-ID"] = workflow_id or "none"
        msg["X-VeoGen-Tracking-ID"] = tracking_id
        
        # Attach text and HTML parts
        msg.attach(MIMEText(body, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        # Save to file system (for backup and dev)
        await self._save_email_to_file(msg, tracking_id, workflow_type)
        
        # Log email workflow
        await self._log_email_workflow(tracking_id, to, subject, workflow_id, workflow_type)

        # Send via SMTP
        try:
            if self.email_smtp != "dev" and self.email_user and self.email_pass:
                with smtplib.SMTP(self.email_smtp, self.email_port) as server:
                    server.starttls()
                    server.login(self.email_user, self.email_pass)
                    server.sendmail(self.email_from, to, msg.as_string())
                
                self.logger.info(f"Email sent successfully: {tracking_id}")
                return True
            else:
                self.logger.info(f"Dev mode - email saved to file: {tracking_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"SMTP error for {tracking_id}: {e}")
            return False

    async def _save_email_to_file(self, msg: MIMEMultipart, tracking_id: str, 
                                workflow_type: EmailWorkflowType = None):
        """Save email to file system for backup and development"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_to = msg["To"].replace('@', '_at_').replace('.', '_')
        
        # Save raw email
        filename = f"{self.dev_outbox}/email_{timestamp}_{tracking_id}_{safe_to}.eml"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(msg.as_string())

        # Save HTML preview
        html_content = None
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode()
                break

        if html_content:
            html_filename = f"{self.dev_outbox}/email_{timestamp}_{tracking_id}_{safe_to}.html"
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html_content)

        # Save workflow metadata
        if workflow_type:
            workflow_file = f"{self.dev_outbox}/workflows/workflow_{timestamp}_{tracking_id}.json"
            import json
            metadata = {
                "tracking_id": tracking_id,
                "workflow_type": workflow_type.value,
                "to": msg["To"],
                "subject": msg["Subject"],
                "timestamp": timestamp,
                "status": "sent"
            }
            with open(workflow_file, "w") as f:
                json.dump(metadata, f, indent=2)

    async def _log_email_workflow(self, tracking_id: str, to: str, subject: str,
                                workflow_id: str, workflow_type: EmailWorkflowType):
        """Log email workflow for analytics and debugging"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tracking_id": tracking_id,
            "workflow_id": workflow_id,
            "workflow_type": workflow_type.value if workflow_type else None,
            "to": to,
            "subject": subject,
            "action": "sent"
        }
        
        # In production, this would go to database/analytics service
        self.logger.info(f"Email workflow logged: {log_entry}")

# MAIN EMAIL WORKFLOW ORCHESTRATOR
class VeoGenEmailOrchestrator:
    """
    Main orchestrator for all VeoGen email workflows
    Coordinates between different email systems and manages workflow state
    """
    
    def __init__(self):
        self.email_service = AdvancedEmailService()
        # Workflow state tracking (in production, use Redis/Database)
        self.active_workflows = {}
        
    async def send_enhanced_verification_email(self, user_id: str, email: str, name: str) -> str:
        """Send enhanced verification email with onboarding preview"""
        workflow_id = f"welcome_{user_id}_{int(datetime.utcnow().timestamp())}"
        verify_token = secrets.token_urlsafe(32)
        verify_url = f"{self.email_service.base_url}/verify-email?token={verify_token}&user={user_id}"
        
        subject = "🎬 Welcome to VeoGen! Verify your email to start creating"
        
        html_template = self._get_verification_email_html(name, verify_url)
        text_body = self._get_verification_email_text(name, verify_url)
        
        await self.email_service.send_email_with_tracking(
            to=email,
            subject=subject,
            body=text_body,
            html=html_template,
            workflow_id=workflow_id,
            workflow_type=EmailWorkflowType.WELCOME_SERIES
        )
        
        self.active_workflows[workflow_id] = {
            "type": "registration",
            "user_id": user_id,
            "verify_token": verify_token,
            "status": "active",
            "started": datetime.utcnow()
        }
        
        return workflow_id
    
    async def send_security_challenge(self, user_id: str, email: str, action: str, 
                                   ip_address: str = None, user_agent: str = None) -> tuple:
        """Send security challenge for sensitive actions"""
        challenge_id = f"challenge_{user_id}_{int(datetime.utcnow().timestamp())}"
        challenge_code = self._generate_challenge_code()
        
        subject = f"🔐 VeoGen Security Challenge: {action}"
        
        html_template = self._get_challenge_email_html(action, challenge_code, ip_address, user_agent)
        text_body = self._get_challenge_email_text(action, challenge_code, ip_address, user_agent)
        
        await self.email_service.send_email_with_tracking(
            to=email,
            subject=subject,
            body=text_body,
            html=html_template,
            workflow_id=challenge_id,
            workflow_type=EmailWorkflowType.CHALLENGE_RESPONSE
        )
        
        self.active_workflows[challenge_id] = {
            "type": "challenge",
            "user_id": user_id,
            "challenge_code": challenge_code,
            "status": "pending",
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }
        
        return challenge_id, challenge_code
    
    async def send_advanced_password_reset(self, user_id: str, email: str, name: str,
                                         ip_address: str = None, user_agent: str = None) -> tuple:
        """Send advanced password reset with security features"""
        reset_id = f"reset_{user_id}_{int(datetime.utcnow().timestamp())}"
        reset_token = secrets.token_urlsafe(32)
        reset_url = f"{self.email_service.base_url}/reset-password?token={reset_token}&user={user_id}"
        
        subject = "🔒 VeoGen Password Reset Request - Secure Link Inside"
        
        html_template = self._get_password_reset_html(name, reset_url, ip_address, user_agent)
        text_body = self._get_password_reset_text(name, reset_url, ip_address, user_agent)
        
        await self.email_service.send_email_with_tracking(
            to=email,
            subject=subject,
            body=text_body,
            html=html_template,
            workflow_id=reset_id,
            workflow_type=EmailWorkflowType.PASSWORD_RESET_ADVANCED
        )
        
        self.active_workflows[reset_id] = {
            "type": "password_reset",
            "user_id": user_id,
            "reset_token": reset_token,
            "status": "pending",
            "expires": datetime.utcnow() + timedelta(hours=2)
        }
        
        return reset_id, reset_token
    
    async def send_project_completion_notification(self, user_id: str, email: str, name: str,
                                                 project_name: str, video_url: str) -> str:
        """Send notification when video generation is complete"""
        notification_id = f"completion_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        subject = f"🎉 Your VeoGen video '{project_name}' is ready!"
        
        html_template = self._get_project_completion_html(name, project_name, video_url)
        text_body = self._get_project_completion_text(name, project_name, video_url)
        
        await self.email_service.send_email_with_tracking(
            to=email,
            subject=subject,
            body=text_body,
            html=html_template,
            workflow_id=notification_id,
            workflow_type=EmailWorkflowType.NOTIFICATION
        )
        
        return notification_id
    
    async def send_weekly_digest(self, user_id: str, email: str, name: str, stats: Dict[str, Any]) -> str:
        """Send weekly engagement digest"""
        digest_id = f"digest_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        subject = f"📊 Your VeoGen Weekly Summary - {stats.get('videos_created', 0)} videos created!"
        
        html_template = self._get_weekly_digest_html(name, stats)
        text_body = self._get_weekly_digest_text(name, stats)
        
        await self.email_service.send_email_with_tracking(
            to=email,
            subject=subject,
            body=text_body,
            html=html_template,
            workflow_id=digest_id,
            workflow_type=EmailWorkflowType.ENGAGEMENT
        )
        
        return digest_id
    
    async def send_security_alert(self, user_id: str, email: str, name: str,
                                activity: str, ip_address: str, user_agent: str,
                                location: str = None) -> str:
        """Send security alert for suspicious activity"""
        alert_id = f"security_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        subject = "🚨 VeoGen Security Alert: Unusual Account Activity Detected"
        
        html_template = self._get_security_alert_html(name, activity, ip_address, user_agent, location, alert_id)
        text_body = self._get_security_alert_text(name, activity, ip_address, user_agent, location, alert_id)
        
        await self.email_service.send_email_with_tracking(
            to=email,
            subject=subject,
            body=text_body,
            html=html_template,
            workflow_id=alert_id,
            workflow_type=EmailWorkflowType.SECURITY_ALERT
        )
        
        return alert_id
    
    def verify_challenge_code(self, challenge_id: str, provided_code: str) -> bool:
        """Verify challenge response code"""
        workflow = self.active_workflows.get(challenge_id)
        if not workflow or workflow["type"] != "challenge":
            return False
        
        if datetime.utcnow() > workflow["expires"]:
            self.active_workflows[challenge_id]["status"] = "expired"
            return False
        
        if workflow["challenge_code"] == provided_code:
            self.active_workflows[challenge_id]["status"] = "verified"
            return True
        
        return False
    
    def verify_reset_token(self, reset_id: str, provided_token: str) -> bool:
        """Verify password reset token"""
        workflow = self.active_workflows.get(reset_id)
        if not workflow or workflow["type"] != "password_reset":
            return False
        
        if datetime.utcnow() > workflow["expires"]:
            self.active_workflows[reset_id]["status"] = "expired"
            return False
        
        if workflow["reset_token"] == provided_token:
            self.active_workflows[reset_id]["status"] = "verified"
            return True
        
        return False
    
    def _generate_challenge_code(self) -> str:
        """Generate a secure 6-digit challenge code"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def _get_verification_email_html(self, name: str, verify_url: str) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to VeoGen!</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 32px; }}
        .header .tagline {{ color: #e0e6ff; margin: 10px 0; font-size: 16px; }}
        .content {{ padding: 40px 30px; }}
        .welcome-message {{ background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .verify-btn {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 16px 32px; border-radius: 30px; font-weight: bold; margin: 20px 0; font-size: 16px; }}
        .feature-preview {{ background: #f1f5f9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .feature {{ display: flex; align-items: center; margin: 10px 0; }}
        .feature-icon {{ font-size: 24px; margin-right: 15px; }}
        .security-note {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #64748b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 VeoGen</h1>
            <div class="tagline">AI-Powered Video Generation Platform</div>
        </div>
        
        <div class="content">
            <h2>Welcome aboard, {name}! 🚀</h2>
            
            <div class="welcome-message">
                <p><strong>You've just joined the future of video creation!</strong></p>
                <p>VeoGen empowers creators like you to generate professional videos using cutting-edge AI technology. In just a few clicks, you'll be creating content that would traditionally take hours or days.</p>
            </div>
            
            <p>To unlock your account and start creating amazing videos, please verify your email address:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}" class="verify-btn">✨ Verify Email & Start Creating</a>
            </div>
            
            <div class="feature-preview">
                <h3>🎯 What you'll get access to:</h3>
                <div class="feature">
                    <span class="feature-icon">🎥</span>
                    <div><strong>AI Video Generation:</strong> Create videos from text descriptions</div>
                </div>
                <div class="feature">
                    <span class="feature-icon">📝</span>
                    <div><strong>Movie Maker:</strong> Generate complete movie scripts with AI</div>
                </div>
                <div class="feature">
                    <span class="feature-icon">🎨</span>
                    <div><strong>Style Templates:</strong> Professional video styles and themes</div>
                </div>
                <div class="feature">
                    <span class="feature-icon">📊</span>
                    <div><strong>Project Dashboard:</strong> Manage and track your creations</div>
                </div>
                <div class="feature">
                    <span class="feature-icon">⚡</span>
                    <div><strong>Fast Processing:</strong> Generate videos in minutes, not hours</div>
                </div>
            </div>
            
            <div class="security-note">
                <strong>🔒 Security:</strong> This verification link expires in 24 hours. If you didn't create this account, you can safely ignore this email.
            </div>
            
            <p>Questions? Reply to this email or visit our help center.</p>
            
            <p>Excited to see what you create!<br>
            <strong>The VeoGen Team</strong></p>
        </div>
        
        <div class="footer">
            <p><strong>VeoGen</strong> • AI-Powered Video Generation<br>
            <a href="{self.email_service.base_url}" style="color: #667eea;">Visit VeoGen Dashboard</a></p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_verification_email_text(self, name: str, verify_url: str) -> str:
        return f"""
Welcome to VeoGen, {name}!

You've just joined the future of video creation! VeoGen empowers creators to generate professional videos using cutting-edge AI technology.

Please verify your email to start creating: {verify_url}

What you'll get access to:
• AI Video Generation: Create videos from text descriptions
• Movie Maker: Generate complete movie scripts with AI  
• Style Templates: Professional video styles and themes
• Project Dashboard: Manage and track your creations
• Fast Processing: Generate videos in minutes, not hours

This verification link expires in 24 hours.

Questions? Reply to this email or visit our help center.

The VeoGen Team
        """

# Add other template methods...
    def _get_challenge_email_html(self, action: str, challenge_code: str, ip_address: str, user_agent: str) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Security Challenge - VeoGen</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; }}
        .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 30px 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 28px; }}
        .content {{ padding: 30px; }}
        .challenge-code {{ background: #1f2937; color: #10b981; font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 8px; margin: 20px 0; letter-spacing: 4px; }}
        .security-info {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .action-details {{ background: #f1f5f9; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #64748b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Security Challenge</h1>
        </div>
        
        <div class="content">
            <h2>Security Verification Required</h2>
            
            <div class="action-details">
                <strong>Action Requested:</strong> {action}<br>
                <strong>Time:</strong> {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC<br>
                <strong>IP Address:</strong> {ip_address or "Unknown"}<br>
                <strong>Device:</strong> {user_agent[:50] + "..." if user_agent and len(user_agent) > 50 else user_agent or "Unknown"}
            </div>
            
            <p>To proceed with this action, please enter the following challenge code in VeoGen:</p>
            
            <div class="challenge-code">{challenge_code}</div>
            
            <div class="security-info">
                <strong>🛡️ Security Note:</strong><br>
                • This code expires in 10 minutes<br>
                • Only enter this code if you initiated this action<br>
                • If you didn't request this, please secure your account immediately
            </div>
            
            <p>If you didn't initiate this action, please contact our security team immediately.</p>
            
            <p><strong>VeoGen Security Team</strong></p>
        </div>
        
        <div class="footer">
            <p><strong>VeoGen Security</strong> • Keep Your Account Safe</p>
        </div>
    </div>
</body>
</html>
        """

# Demo function
async def demo_email_workflows():
    """Demo the advanced email workflow system"""
    orchestrator = VeoGenEmailOrchestrator()
    
    demo_user = {
        "id": "demo_user_123",
        "email": "sandraschipal@hotmail.com",
        "name": "Sandra"
    }
    
    print("🚀 VeoGen Advanced Email Workflow Demo")
    print("=" * 50)
    
    # 1. Enhanced verification email
    print("\n📧 1. Sending Enhanced Verification Email...")
    workflow_id = await orchestrator.send_enhanced_verification_email(
        user_id=demo_user["id"],
        email=demo_user["email"],
        name=demo_user["name"]
    )
    print(f"   ✅ Verification email sent: {workflow_id}")
    
    # 2. Security challenge
    print("\n🔐 2. Sending Security Challenge...")
    challenge_id, challenge_code = await orchestrator.send_security_challenge(
        user_id=demo_user["id"],
        email=demo_user["email"],
        action="Delete Account",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    print(f"   ✅ Security challenge sent: {challenge_id}")
    print(f"   🔑 Challenge code: {challenge_code}")
    
    # 3. Advanced password reset
    print("\n🔒 3. Sending Advanced Password Reset...")
    reset_id, reset_token = await orchestrator.send_advanced_password_reset(
        user_id=demo_user["id"],
        email=demo_user["email"],
        name=demo_user["name"],
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    print(f"   ✅ Password reset sent: {reset_id}")
    
    # 4. Project completion notification
    print("\n🎬 4. Sending Project Completion Notification...")
    notification_id = await orchestrator.send_project_completion_notification(
        user_id=demo_user["id"],
        email=demo_user["email"],
        name=demo_user["name"],
        project_name="Epic Prague Sunset Video",
        video_url="https://veogen.com/videos/epic-prague-sunset.mp4"
    )
    print(f"   ✅ Project notification sent: {notification_id}")
    
    print("\n" + "=" * 50)
    print("🎉 Advanced email workflows demonstrated!")
    print("📁 Check email files in: dev_emails/")
    
    return {
        "workflow_id": workflow_id,
        "challenge_id": challenge_id,
        "reset_id": reset_id,
        "notification_id": notification_id
    }

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_email_workflows())
