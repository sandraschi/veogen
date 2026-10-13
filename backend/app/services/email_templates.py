"""
Enhanced email templates for VeoGen
"""


def get_verification_email_template(user_name: str, verify_url: str) -> tuple:
    """Generate verification email template"""

    subject = "Welcome to VeoGen! Please verify your email"

    # Plain text version
    text_body = f"""
Hello {user_name},

Welcome to VeoGen - the AI-powered video generation platform!

To complete your account setup, please verify your email address by clicking the link below:

{verify_url}

This verification link will expire in 24 hours.

If you didn't create a VeoGen account, you can safely ignore this email.

Best regards,
The VeoGen Team

---
VeoGen - Create Amazing Videos with AI
https://veogen.com
"""

    # HTML version
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to VeoGen!</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 28px; }}
        .header p {{ color: #e0e0e0; margin: 10px 0 0 0; }}
        .content {{ padding: 40px 30px; }}
        .content h2 {{ color: #333; margin-bottom: 20px; }}
        .content p {{ color: #666; line-height: 1.6; margin-bottom: 20px; }}
        .verify-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
        .verify-button:hover {{ background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%); }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 VeoGen</h1>
            <p>AI-Powered Video Generation Platform</p>
        </div>
        
        <div class="content">
            <h2>Welcome, {user_name}!</h2>
            
            <p>Thank you for joining VeoGen! You're now part of a revolutionary platform that makes professional video creation accessible to everyone through the power of AI.</p>
            
            <p>To get started and unlock all VeoGen features, please verify your email address:</p>
            
            <div style="text-align: center;">
                <a href="{verify_url}" class="verify-button">Verify My Email Address</a>
            </div>
            
            <div class="warning">
                <strong>⏰ Important:</strong> This verification link will expire in 24 hours.
            </div>
            
            <p>Once verified, you'll be able to:</p>
            <ul>
                <li>🎥 Generate professional videos with AI</li>
                <li>📝 Create movie scripts with AI assistance</li>
                <li>🎨 Access premium templates and styles</li>
                <li>📊 Monitor your video generation projects</li>
            </ul>
            
            <p>If you didn't create a VeoGen account, you can safely ignore this email.</p>
        </div>
        
        <div class="footer">
            <p><strong>VeoGen Team</strong><br>
            Create Amazing Videos with AI<br>
            <a href="https://veogen.com" style="color: #667eea;">https://veogen.com</a></p>
        </div>
    </div>
</body>
</html>
"""

    return subject, text_body, html_body


def get_password_reset_template(user_name: str, reset_url: str) -> tuple:
    """Generate password reset email template"""

    subject = "VeoGen Password Reset Request"

    # Plain text version
    text_body = f"""
Hello {user_name},

We received a request to reset your VeoGen account password.

To reset your password, click the link below:

{reset_url}

This reset link will expire in 2 hours for security reasons.

If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.

Best regards,
The VeoGen Team

---
VeoGen - Create Amazing Videos with AI
https://veogen.com
"""

    # HTML version
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - VeoGen</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 28px; }}
        .header p {{ color: #e0e0e0; margin: 10px 0 0 0; }}
        .content {{ padding: 40px 30px; }}
        .content h2 {{ color: #333; margin-bottom: 20px; }}
        .content p {{ color: #666; line-height: 1.6; margin-bottom: 20px; }}
        .reset-button {{ display: inline-block; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
        .reset-button:hover {{ background: linear-gradient(135deg, #ff5252 0%, #e53935 100%); }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; color: #856404; }}
        .security-notice {{ background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; color: #0c5460; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 VeoGen</h1>
            <p>Password Reset Request</p>
        </div>
        
        <div class="content">
            <h2>Password Reset for {user_name}</h2>
            
            <p>We received a request to reset the password for your VeoGen account.</p>
            
            <p>If you requested this password reset, click the button below to create a new password:</p>
            
            <div style="text-align: center;">
                <a href="{reset_url}" class="reset-button">Reset My Password</a>
            </div>
            
            <div class="warning">
                <strong>⏰ Important:</strong> This reset link will expire in 2 hours for security reasons.
            </div>
            
            <div class="security-notice">
                <strong>🛡️ Security Notice:</strong> If you didn't request this password reset, you can safely ignore this email. Your current password will remain unchanged and secure.
            </div>
            
            <p>For your security, always:</p>
            <ul>
                <li>🔒 Use a strong, unique password</li>
                <li>📱 Enable two-factor authentication when available</li>
                <li>🚫 Never share your login credentials</li>
            </ul>
        </div>
        
        <div class="footer">
            <p><strong>VeoGen Security Team</strong><br>
            Create Amazing Videos with AI<br>
            <a href="https://veogen.com" style="color: #667eea;">https://veogen.com</a></p>
        </div>
    </div>
</body>
</html>
"""

    return subject, text_body, html_body
