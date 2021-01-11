from django.apps import AppConfig


class InvoicingConfig(AppConfig):
    name = "apps.invoicing"

    def ready(self):
        from apps.annotations.registry import annotations
        from apps.search.registry import search
        from apps.audit.registry import audit
        from apps.invoicing.models import (
            Contractor,
            SaleInvoice,
            RefrigerantWeights,
            ServiceTemplate,
            SaleInvoiceItem,
            CorrectiveSaleInvoice,
        )

        annotations.register(Contractor)
        annotations.register(SaleInvoice)
        search.register(Contractor)
        search.register(SaleInvoice)
        audit.register(Contractor)
        audit.register(SaleInvoice)
        audit.register(RefrigerantWeights)
        audit.register(ServiceTemplate)
        audit.register(SaleInvoiceItem)
        audit.register(CorrectiveSaleInvoice)
