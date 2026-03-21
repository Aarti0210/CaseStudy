"""
Email service for sending various types of emails.
Centralizes email functionality with proper error handling.
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
    max_retries: int = 3
) -> bool:
    """
    Send email with retry logic.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        plain_text: Plain text content
        html_text: HTML content (optional)
        max_retries: Maximum number of retry attempts
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        msg = _build_email_message(to_email, subject, plain_text, html_text)
        return _send_with_retry(msg, max_retries)
        
    except Exception as e:
        current_app.logger.error(f"Email service error: {str(e)}")
        return False


def _build_email_message(to_email: str, subject: str, plain_text: str, html_text: Optional[str]) -> EmailMessage:
    """Build email message object."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = current_app.config.get("MAIL_DEFAULT_SENDER")
    msg["To"] = to_email
    msg.set_content(plain_text)
    
    if html_text:
        msg.add_alternative(html_text, subtype="html")
    
    return msg


def _send_with_retry(msg: EmailMessage, max_retries: int) -> bool:
    """Send email with retry logic."""
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
            
            current_app.logger.info(f"Email sent successfully on attempt {attempt}")
            return True
            
        except Exception as e:
            last_exception = e
            current_app.logger.warning(f"Email send attempt {attempt} failed: {str(e)}")
            
            # Exponential backoff
            if attempt < max_retries:
                wait_time = 2 ** attempt
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
