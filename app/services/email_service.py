"""
Email service for sending emails via SMTP.

Supports:
- Password reset emails
- Email verification emails
- Custom HTML templates
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(getattr(settings, 'SMTP_PORT', 587))
        self.smtp_user = getattr(settings, 'SMTP_USER', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.smtp_from = getattr(settings, 'SMTP_FROM', self.smtp_user)
        self.use_tls = getattr(settings, 'SMTP_USE_TLS', 'true').lower() == 'true'
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text fallback (optional)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.smtp_user or not self.smtp_password:
            print("⚠️ SMTP credentials not configured - email not sent")
            print(f"Would send email to: {to_email}")
            print(f"Subject: {subject}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            
            # Add plain text version if provided
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: str = "User"
    ) -> bool:
        """
        Send password reset email with link.
        
        Args:
            to_email: User's email address
            reset_token: Password reset token
            user_name: User's name for personalization
            
        Returns:
            True if email was sent successfully
        """
        reset_link = f"{self.frontend_url}/auth/reset-password?token={reset_token}"
        
        subject = "Reset Your Password - AI Claims"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 12px; }}
        .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Password Reset Request</h1>
        </div>
        <div class="content">
            <p>Hello {user_name},</p>
            
            <p>We received a request to reset your password for your AI Claims account.</p>
            
            <p>Click the button below to reset your password:</p>
            
            <center>
                <a href="{reset_link}" class="button">Reset Password</a>
            </center>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #6b7280; font-size: 14px;">{reset_link}</p>
            
            <div class="warning">
                <strong>⚠️ Important:</strong>
                <ul>
                    <li>This link will expire in <strong>1 hour</strong></li>
                    <li>If you didn't request this, please ignore this email</li>
                    <li>Your password won't change until you click the link above</li>
                </ul>
            </div>
            
            <p>If you have any questions, contact us at <a href="mailto:support@company.sk">support@company.sk</a></p>
            
            <p>Best regards,<br>AI Claims Team</p>
        </div>
        <div class="footer">
            <p>© 2024 AI Claims. All rights reserved.</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
        """
        
        text_content = f"""
Password Reset Request

Hello {user_name},

We received a request to reset your password for your AI Claims account.

Click this link to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
AI Claims Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        user_name: str = "User"
    ) -> bool:
        """
        Send email verification link.
        
        Args:
            to_email: User's email address
            verification_token: Email verification token
            user_name: User's name for personalization
            
        Returns:
            True if email was sent successfully
        """
        verification_link = f"{self.frontend_url}/auth/verify-email?token={verification_token}"
        
        subject = "Verify Your Email - AI Claims"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 12px; }}
        .info {{ background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✉️ Welcome to AI Claims!</h1>
        </div>
        <div class="content">
            <p>Hello {user_name},</p>
            
            <p>Thank you for registering with AI Claims! We're excited to have you on board.</p>
            
            <p>To complete your registration, please verify your email address by clicking the button below:</p>
            
            <center>
                <a href="{verification_link}" class="button">Verify Email</a>
            </center>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #6b7280; font-size: 14px;">{verification_link}</p>
            
            <div class="info">
                <strong>ℹ️ What happens next?</strong>
                <ul>
                    <li>Click the verification link above</li>
                    <li>Your account will be activated</li>
                    <li>You can start using AI Claims immediately</li>
                </ul>
            </div>
            
            <p>This link will expire in <strong>24 hours</strong>.</p>
            
            <p>If you didn't create an account, you can safely ignore this email.</p>
            
            <p>Welcome aboard!<br>AI Claims Team</p>
        </div>
        <div class="footer">
            <p>© 2024 AI Claims. All rights reserved.</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
        """
        
        text_content = f"""
Welcome to AI Claims!

Hello {user_name},

Thank you for registering! Please verify your email address by clicking this link:
{verification_link}

This link will expire in 24 hours.

If you didn't create an account, you can safely ignore this email.

Best regards,
AI Claims Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

