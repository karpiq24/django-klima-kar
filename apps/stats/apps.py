from django.apps import AppConfig


class StatsConfig(AppConfig):
    name = "apps.stats"

    def ready(self):
        from apps.audit.registry import audit
        from apps.stats.models import ReceiptPTU

        audit.register(ReceiptPTU)
