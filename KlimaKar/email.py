from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend

from django.conf import settings
from apps.settings.models import SiteSettings


def get_email_message(subject, body, to):
    config = SiteSettings.load()

    if config.EMAIL_HOST and config.EMAIL_HOST_USER and config.EMAIL_HOST_PASSWORD:
        backend = EmailBackend(host=config.EMAIL_HOST, port=config.EMAIL_PORT, username=config.EMAIL_HOST_USER,
                               password=config.EMAIL_HOST_PASSWORD, use_tls=config.EMAIL_USE_TLS,
                               use_ssl=config.EMAIL_USE_SSL, fail_silently=False)
        from_email = config.DEFAULT_FROM_EMAIL or config.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
        return EmailMessage(subject=subject, body=body, from_email=from_email, to=to, connection=backend)
    else:
        return EmailMessage(subject=subject, body=body, to=to)


def mail_admins(subject, message, fail_silently=False):
    """Send a message to the admins, as defined by the ADMINS setting."""
    if not settings.ADMINS:
        return
    mail = get_email_message(f'{settings.EMAIL_SUBJECT_PREFIX} {subject}', message, [a[1] for a in settings.ADMINS])
    mail.send(fail_silently=fail_silently)


def mail_managers(subject, message, fail_silently=False):
    """Send a message to the managers, as defined by the MANAGERS setting."""
    if not settings.MANAGERS:
        return
    mail = get_email_message(f'{settings.EMAIL_SUBJECT_PREFIX} {subject}', message, [a[1] for a in settings.MANAGERS])
    mail.send(fail_silently=fail_silently)
