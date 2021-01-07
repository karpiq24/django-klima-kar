from django.apps import AppConfig


class CommissionConfig(AppConfig):
    name = "apps.commission"

    def ready(self):
        from apps.annotations.registry import annotations
        from apps.commission.models import Commission, Vehicle, Component

        annotations.register(Commission)
        annotations.register(Vehicle)
        annotations.register(Component)
