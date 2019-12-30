from django.apps import AppConfig
from django.db.models.signals import pre_save, pre_delete, post_save


class AuditConfig(AppConfig):
    name = 'apps.audit'

    def ready(self):
        from apps.audit.functions import pre_delete_handler, pre_save_handler, post_save_handler  # noqa
        from apps.warehouse import models as warehouse  # noqa
        from apps.commission import models as commission  # noqa
        from apps.invoicing import models as invoicing  # noqa

        models = [
            warehouse.Ware,
            warehouse.Supplier,
            warehouse.Invoice,
            warehouse.InvoiceItem,
            commission.Vehicle,
            commission.Component,
            commission.Commission,
            commission.CommissionItem,
            commission.CommissionFile,
            invoicing.Contractor,
            invoicing.SaleInvoice,
            invoicing.RefrigerantWeights,
            invoicing.ServiceTemplate,
            invoicing.SaleInvoiceItem,
            invoicing.CorrectiveSaleInvoice
        ]

        for model in models:
            pre_save.connect(pre_save_handler, sender=model)
            post_save.connect(post_save_handler, sender=model)
            pre_delete.connect(pre_delete_handler, sender=model)
