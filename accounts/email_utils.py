"""
Email sending helpers for BraveCare Outreach.
All functions are fire-and-forget — they log errors rather than raising,
so a broken SMTP config never breaks the main request flow.
"""
import logging
import random
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .models import EmailOTP

logger = logging.getLogger(__name__)


# ── OTP helpers ───────────────────────────────────────────────────────────────

def generate_otp_code() -> str:
    """Return a 6-digit OTP string (cryptographically random)."""
    return f"{secrets.randbelow(1000000):06d}"


def create_otp(user, purpose: str) -> EmailOTP:
    """
    Invalidate any previous unused OTPs for the same user+purpose,
    then create and return a fresh one.
    """
    EmailOTP.objects.filter(
        user=user, purpose=purpose, is_used=False
    ).update(is_used=True)

    expiry = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    return EmailOTP.objects.create(
        user=user,
        code=generate_otp_code(),
        purpose=purpose,
        expires_at=expiry,
    )


def can_resend_otp(user, purpose: str) -> bool:
    """Return True if cooldown has passed since the last OTP was sent."""
    cooldown = settings.OTP_RESEND_COOLDOWN
    cutoff = timezone.now() - timedelta(seconds=cooldown)
    return not EmailOTP.objects.filter(
        user=user, purpose=purpose, created_at__gte=cutoff
    ).exists()


# ── Email send helpers ─────────────────────────────────────────────────────────

def _send(subject: str, to_email: str, html_template: str, context: dict) -> bool:
    """Render and send an HTML email. Returns True on success."""
    if not to_email:
        logger.warning("_send called with empty to_email for template %s", html_template)
        return False
    try:
        html_body = render_to_string(html_template, context)
        # Plain-text fallback: strip tags naively
        import re
        text_body = re.sub(r'<[^>]+>', '', html_body)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        return True
    except Exception as exc:
        logger.exception("Failed to send email '%s' to %s: %s", subject, to_email, exc)
        return False


def send_welcome_email(user, temp_password: str, login_url: str) -> bool:
    """Send new-account welcome email with temporary credentials."""
    return _send(
        subject='Welcome to BraveCare Outreach — Your Account Details',
        to_email=user.email,
        html_template='emails/welcome.html',
        context={
            'user': user,
            'temp_password': temp_password,
            'login_url': login_url,
            'expiry_minutes': settings.OTP_EXPIRY_MINUTES,
        },
    )


def send_login_otp(user, otp: EmailOTP) -> bool:
    """Send 2-step login OTP email."""
    return _send(
        subject='BraveCare Outreach — Login Verification Code',
        to_email=user.email,
        html_template='emails/login_otp.html',
        context={
            'user': user,
            'code': otp.code,
            'expiry_minutes': settings.OTP_EXPIRY_MINUTES,
        },
    )


def send_forgot_password_otp(user, otp: EmailOTP) -> bool:
    """Send password-reset OTP email."""
    return _send(
        subject='BraveCare Outreach — Password Reset Code',
        to_email=user.email,
        html_template='emails/forgot_otp.html',
        context={
            'user': user,
            'code': otp.code,
            'expiry_minutes': settings.OTP_EXPIRY_MINUTES,
        },
    )


def send_password_changed_email(user) -> bool:
    """Notify user that their password was successfully changed."""
    return _send(
        subject='BraveCare Outreach — Password Changed',
        to_email=user.email,
        html_template='emails/password_changed.html',
        context={'user': user},
    )
