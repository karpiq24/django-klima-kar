from django.contrib import admin

from apps.warehouse.models import Invoice, InvoiceItem, Supplier, Ware, WarePriceChange

# Register your models here.
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Supplier)
admin.site.register(Ware)
admin.site.register(WarePriceChange)
