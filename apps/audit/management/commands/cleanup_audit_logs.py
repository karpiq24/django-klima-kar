from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from apps.audit.models import AuditLog


class Command(BaseCommand):
    help = "Cleans up audit log table"

    def handle(self, **options):
        now = timezone.now()
        cleanup_delta = timedelta(hours=settings.AUDIT_LOG_EXPIRATION)
        min_attempt_time = now - cleanup_delta

        audit_logs = AuditLog.objects.filter(
            action_time__lt=min_attempt_time,
        )
        count = audit_logs.count()
        audit_logs.delete()

        print(f'Finished removed {count} AuditLog entries')
