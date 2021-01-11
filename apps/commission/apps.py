from django.apps import AppConfig


class CommissionConfig(AppConfig):
    name = "apps.commission"

    def ready(self):
        from apps.annotations.registry import annotations
        from apps.search.registry import search
        from apps.audit.registry import audit
        from apps.commission.models import (
            Commission,
            Vehicle,
            Component,
            CommissionItem,
            CommissionFile,
        )

        annotations.register(Commission)
        annotations.register(Vehicle)
        annotations.register(Component)
        search.register(Commission)
        search.register(Vehicle)
        search.register(Component)
        audit.register(Vehicle)
        audit.register(Component)
        audit.register(Commission)
        audit.register(CommissionItem)
        audit.register(CommissionFile)
