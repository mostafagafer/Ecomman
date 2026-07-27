import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import LoginLockout


logger = logging.getLogger(__name__)


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.META.get("REMOTE_ADDR") or "0.0.0.0"


def normalize_login_email(email):
    return (email or "").strip().lower()


def get_login_lockout(email, request):
    return LoginLockout.objects.filter(
        email=normalize_login_email(email),
        ip_address=get_client_ip(request),
        locked_until__gt=timezone.now(),
    ).first()


def record_login_failure(email, request):
    email = normalize_login_email(email)
    now = timezone.now()
    lockout, _ = LoginLockout.objects.get_or_create(
        email=email,
        ip_address=get_client_ip(request),
        defaults={"last_user_agent": (request.META.get("HTTP_USER_AGENT") or "")[:255]},
    )
    lockout.failed_attempts = int(lockout.failed_attempts or 0) + 1
    lockout.last_failed_at = now
    lockout.last_user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:255]
    if lockout.failed_attempts >= settings.LOGIN_LOCKOUT_FAILURE_LIMIT:
        lockout.locked_until = now + timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
    lockout.save(update_fields=["failed_attempts", "last_failed_at", "last_user_agent", "locked_until", "updated_at"])
    logger.warning("Failed login attempt for %s from %s", email, lockout.ip_address)
    return lockout


def clear_login_failures(email, request):
    LoginLockout.objects.filter(email=normalize_login_email(email), ip_address=get_client_ip(request)).delete()
