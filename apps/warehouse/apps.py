from django.apps import AppConfig


class WarehousesConfig(AppConfig):
    name = "apps.warehouse"

    def ready(self):
        from apps.annotations.registry import annotations
        from apps.search.registry import search
        from apps.audit.registry import audit
        from apps.warehouse.models import Ware, Supplier, Invoice, InvoiceItem

        annotations.register(Ware)
        annotations.register(Supplier)
        annotations.register(Invoice)
        search.register(Ware)
        search.register(Supplier)
        search.register(Invoice)
        audit.register(Ware)
        audit.register(Supplier)
        audit.register(Invoice)
        audit.register(InvoiceItem)
