from django.conf import settings

from .tasks import send_sync_email


def _send(user, subject, html_template, text_template, context=None):
    merged_context = {
        "user": user,
        "email_brand_name": getattr(settings, "EMAIL_BRAND_NAME", "Ecomman"),
        "email_website_url": getattr(settings, "EMAIL_WEBSITE_URL", ""),
        "email_logo_url": getattr(settings, "EMAIL_LOGO_URL", ""),
        "email_social_linkedin_url": getattr(settings, "EMAIL_SOCIAL_LINKEDIN_URL", ""),
        "email_social_facebook_url": getattr(settings, "EMAIL_SOCIAL_FACEBOOK_URL", ""),
        "support_email": getattr(settings, "SUPPORT_EMAIL", ""),
        "frontend_base_url": getattr(settings, "FRONTEND_BASE_URL", ""),
    }
    merged_context.update(context or {})
    return send_sync_email(
        subject=subject,
        recipient_list=[user.email],
        template_name=html_template,
        text_template=text_template,
        context=merged_context,
    )


def send_verification_otp_email(*, user, otp_code):
    return _send(
        user,
        "Verify your Ecomman account",
        "emails/verification_otp_email.html",
        "emails/verification_otp_email.txt",
        {"otp_code": otp_code},
    )


def send_welcome_email(*, user):
    return _send(user, "Welcome to Ecomman", "emails/welcome_email.html", "emails/welcome_email.txt")


def send_password_reset_email(*, user, reset_url):
    return _send(
        user,
        "Reset your Ecomman password",
        "emails/password_reset_email.html",
        "emails/password_reset_email.txt",
        {"reset_url": reset_url},
    )


def send_password_changed_email(*, user):
    return _send(user, "Your Ecomman password was changed", "emails/password_changed_email.html", "emails/password_changed_email.txt")


def send_password_reset_complete_email(*, user):
    return _send(
        user,
        "Your Ecomman password was reset",
        "emails/password_reset_complete_email.html",
        "emails/password_reset_complete_email.txt",
    )
