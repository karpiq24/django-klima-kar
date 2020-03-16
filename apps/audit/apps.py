from django.apps import AppConfig
from django.db.models.signals import pre_save, pre_delete, post_save, m2m_changed
from django.db.models.fields.related import ManyToManyField


class AuditConfig(AppConfig):
    name = 'apps.audit'

    def ready(self):
        from apps.audit.functions import pre_delete_handler, pre_save_handler, post_save_handler, m2m_changed_handler
        from apps.warehouse import models as warehouse
        from apps.commission import models as commission
        from apps.invoicing import models as invoicing
        from apps.stats import models as stats

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
            invoicing.CorrectiveSaleInvoice,
            stats.ReceiptPTU
        ]

        for model in models:
            pre_save.connect(pre_save_handler, sender=model)
            post_save.connect(post_save_handler, sender=model)
            pre_delete.connect(pre_delete_handler, sender=model)
            for field in model._meta.get_fields():
                if type(field) is ManyToManyField:
                    m2m_changed.connect(m2m_changed_handler, sender=getattr(
                        model, field.attname).through)
