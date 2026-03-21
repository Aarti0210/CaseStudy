"""
Production-ready email service for sending various types of emails.
Secure, reliable, and comprehensive email functionality.
"""

import smtplib
import time
from email.message import EmailMessage
from typing import Optional

from flask import current_app


class EmailServiceError(Exception):
    """Custom email service error."""
    pass


def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_text: Optional[str] = None,
    max_retries: int = 3,
    priority: str = "normal"
) -> bool:
    """
    Send email with retry logic and comprehensive error handling.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        plain_text: Plain text content
        html_text: HTML content (optional)
        max_retries: Maximum number of retry attempts
        priority: Email priority (low, normal, high)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Validate inputs
        if not _validate_email_address(to_email):
            raise EmailServiceError(f"Invalid recipient email: {to_email}")
        
        if not subject or len(subject.strip()) == 0:
            raise EmailServiceError("Email subject cannot be empty")
        
        if not plain_text or len(plain_text.strip()) == 0:
            raise EmailServiceError("Email content cannot be empty")
        
        msg = _build_email_message(to_email, subject, plain_text, html_text)
        return _send_with_retry(msg, max_retries, priority)
        
    except EmailServiceError:
        raise
    except Exception as e:
        current_app.logger.error(f"Email service error: {str(e)}")
        return False


def send_otp_email(to_email: str, code: str, ttl_seconds: int = 300) -> bool:
    """
    Send OTP email with predefined template.
    
    Args:
        to_email: Recipient email address
        code: One-time password code
        ttl_seconds: Time to live for OTP
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        if not _validate_otp_code(code):
            raise EmailServiceError(f"Invalid OTP code format: {code}")
        
        subject = "Your verification code"
        plain_text = (
            f"Your verification code is {code}. It expires in {ttl_seconds//60} minutes."
        )
        html_text = f"""
        <html>
          <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
              <h2 style="color: #333;">Verification Code</h2>
              <p>Dear user,</p>
              <p>Your one-time verification code is <strong style="font-size: 24px; color: #007bff;">{code}</strong>.</p>
              <p>This code will expire in <strong>{ttl_seconds//60} minutes</strong>.</p>
              <p>If you did not request this, ignore this email.</p>
              <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
              <p style="font-size: 12px; color: #666;">
                This is an automated message. Please do not reply to this email.
              </p>
            </div>
          </body>
        </html>
        """
        
        return send_email(to_email, subject, plain_text, html_text, priority="high")
        
    except Exception as e:
        current_app.logger.error(f"OTP email error: {str(e)}")
        return False


def send_welcome_email(to_email: str, user_name: str) -> bool:
    """Send welcome email to new users."""
    try:
        subject = "Welcome to Judicial Supreme System"
        plain_text = f"""
Dear {user_name},

Welcome to the Judicial Supreme Case Management System!

Your account has been successfully created. You can now:
- Log in to your account
- Create and manage legal cases
- Access all system features

If you have any questions, please don't hesitate to contact our support team.

Best regards,
Judicial Supreme Team
        """
        
        html_text = f"""
        <html>
          <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
              <h1 style="color: #007bff;">Welcome to Judicial Supreme!</h1>
              <p>Dear <strong>{user_name}</strong>,</p>
              <p>Welcome to the Judicial Supreme Case Management System!</p>
              <p>Your account has been successfully created. You can now:</p>
              <ul>
                <li>Log in to your account</li>
                <li>Create and manage legal cases</li>
                <li>Access all system features</li>
              </ul>
              <p>If you have any questions, please don't hesitate to contact our support team.</p>
              <p>Best regards,<br>Judicial Supreme Team</p>
            </div>
          </body>
        </html>
        """
        
        return send_email(to_email, subject, plain_text, html_text, priority="high")
        
    except Exception as e:
        current_app.logger.error(f"Welcome email error: {str(e)}")
        return False


def _validate_email_address(email: str) -> bool:
    """Validate email address format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _validate_otp_code(code: str) -> bool:
    """Validate OTP code format."""
    return isinstance(code, str) and len(code) == 6 and code.isdigit()


def _build_email_message(to_email: str, subject: str, plain_text: str, html_text: Optional[str]) -> EmailMessage:
    """Build email message object with security headers."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = current_app.config.get("MAIL_DEFAULT_SENDER")
    msg["To"] = to_email
    msg.set_content(plain_text)
    
    # Add security headers
    msg["X-Priority"] = "3"  # Normal priority
    msg["X-Mailer"] = "Judicial Supreme System"
    
    if html_text:
        msg.add_alternative(html_text, subtype="html")
    
    return msg


def _send_with_retry(msg: EmailMessage, max_retries: int, priority: str) -> bool:
    """Send email with exponential backoff retry logic."""
    cfg = current_app.config
    last_exception = None
    
    for attempt in range(1, max_retries + 1):
        try:
            server = _create_smtp_server(cfg)
            
            # Authenticate if credentials provided
            username = cfg.get("MAIL_USERNAME")
            password = cfg.get("MAIL_PASSWORD")
            if username and password:
                server.login(username, password)
            
            server.send_message(msg)
            server.quit()
            
            current_app.logger.info(f"Email sent successfully on attempt {attempt} with priority {priority}")
            return True
            
        except Exception as e:
            last_exception = e
            current_app.logger.warning(f"Email send attempt {attempt} failed: {str(e)}")
            
            # Exponential backoff with jitter
            if attempt < max_retries:
                wait_time = (2 ** attempt) + (time.time() % 1)  # Add jitter
                _sleep(wait_time)
    
    current_app.logger.error(f"Failed to send email after {max_retries} attempts: {str(last_exception)}")
    return False


def _create_smtp_server(cfg):
    """Create SMTP server based on configuration."""
    use_ssl = cfg.get("MAIL_USE_SSL", False)
    use_tls = cfg.get("MAIL_USE_TLS", False)
    server = cfg.get("MAIL_SERVER")
    port = cfg.get("MAIL_PORT", 587)
    
    if use_ssl:
        return smtplib.SMTP_SSL(server, port)
    else:
        smtp_server = smtplib.SMTP(server, port)
        if use_tls:
            smtp_server.starttls()
        return smtp_server


def _sleep(seconds: int):
    """Sleep with eventlet support."""
    try:
        import eventlet
        eventlet.sleep(seconds)
    except ImportError:
        import time
        time.sleep(seconds)
