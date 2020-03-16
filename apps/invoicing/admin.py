from django.contrib import admin

from apps.invoicing.models import (
    SaleInvoice,
    SaleInvoiceItem,
    Contractor,
    RefrigerantWeights,
    ServiceTemplate,
    CorrectiveSaleInvoice,
)

admin.site.register(SaleInvoice)
admin.site.register(SaleInvoiceItem)
admin.site.register(Contractor)
admin.site.register(RefrigerantWeights)
admin.site.register(ServiceTemplate)
admin.site.register(CorrectiveSaleInvoice)
