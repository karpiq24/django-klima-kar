from django.apps import AppConfig


class WarehousesConfig(AppConfig):
    name = "apps.warehouse"

    def ready(self):
        from apps.annotations.registry import annotations
        from apps.warehouse.models import Ware, Supplier, Invoice

        annotations.register(Ware)
        annotations.register(Supplier)
        annotations.register(Invoice)
