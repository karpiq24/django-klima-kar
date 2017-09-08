from django.contrib import admin
from apps.invoices.models import Invoice, InvoiceItem, Supplier, Ware

# Register your models here.
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Supplier)
admin.site.register(Ware)
