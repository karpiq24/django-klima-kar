from django.apps import AppConfig


class InvoicingConfig(AppConfig):
    name = "apps.invoicing"

    def ready(self):
        from apps.annotations.registry import annotations
        from apps.invoicing.models import Contractor

        annotations.register(Contractor)
