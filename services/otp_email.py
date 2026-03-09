import smtplib
import time
from email.message import EmailMessage

from flask import current_app


def _build_otp_message(to_email: str, code: str, ttl_seconds: int):
    subject = "Your verification code"
    plain = (
        f"Your verification code is {code}. It expires in {ttl_seconds//60} minutes."
    )
    html = f"""
    <html>
      <body>
        <p>Dear user,</p>
        <p>Your one-time verification code is <strong>{code}</strong>.</p>
        <p>This code will expire in <strong>{ttl_seconds//60} minutes</strong>.</p>
        <p>If you did not request this, ignore this email.</p>
      </body>
    </html>
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = current_app.config.get("MAIL_DEFAULT_SENDER")
    msg["To"] = to_email
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")
    return msg


def send_otp_email(to_email: str, code: str, ttl_seconds: int) -> bool:
    """Send OTP email with retry logic. Returns True on success, False on failure."""
    cfg = current_app.config
    max_retries = int(cfg.get("OTP_SEND_MAX_RETRIES", 3))
    backoff_base = 1
    last_exc = None
    msg = _build_otp_message(to_email, code, ttl_seconds)

    for attempt in range(1, max_retries + 1):
        try:
            server = None
            if cfg.get("MAIL_USE_SSL"):
                server = smtplib.SMTP_SSL(cfg.get("MAIL_SERVER"), cfg.get("MAIL_PORT"))
            else:
                server = smtplib.SMTP(cfg.get("MAIL_SERVER"), cfg.get("MAIL_PORT"))
                if cfg.get("MAIL_USE_TLS"):
                    server.starttls()
            username = cfg.get("MAIL_USERNAME")
            password = cfg.get("MAIL_PASSWORD")
            if username and password:
                server.login(username, password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            last_exc = e
            wait = backoff_base**attempt
            # Use eventlet's cooperative sleep if available (prevents blocking under eventlet)
            try:
                import eventlet

                eventlet.sleep(wait)
            except Exception:
                time.sleep(wait)
            continue
    current_app.logger.exception("Failed to send OTP email after retries: %s", last_exc)
    return False
