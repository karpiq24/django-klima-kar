from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from apps.invoicing.models import SaleInvoice, SaleInvoiceItem, Contractor, RefrigerantWeights, ServiceTemplate

admin.site.register(SaleInvoice, CompareVersionAdmin)
admin.site.register(SaleInvoiceItem, CompareVersionAdmin)
admin.site.register(Contractor, CompareVersionAdmin)
admin.site.register(RefrigerantWeights, CompareVersionAdmin)
admin.site.register(ServiceTemplate, CompareVersionAdmin)
