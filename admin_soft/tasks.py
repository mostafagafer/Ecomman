import logging
from email.utils import formataddr

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)


def send_sync_email(subject, recipient_list, template_name, context, from_email=None, text_template=None):
    from_email = from_email or formataddr((getattr(settings, "EMAIL_FROM_NAME", "Ecomman"), settings.DEFAULT_FROM_EMAIL))
    recipients = [email.strip() for email in recipient_list if email and email.strip()]
    if not recipients:
        return False

    try:
        html_content = render_to_string(template_name, context)
        text_content = render_to_string(text_template, context) if text_template else html_content
        message = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=recipients)
        message.attach_alternative(html_content, "text/html")
        message.send()
        return True
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, recipients)
        return False
