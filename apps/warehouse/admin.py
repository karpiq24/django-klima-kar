from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from apps.warehouse.models import Invoice, InvoiceItem, Supplier, Ware

# Register your models here.
admin.site.register(Invoice, CompareVersionAdmin)
admin.site.register(InvoiceItem, CompareVersionAdmin)
admin.site.register(Supplier, CompareVersionAdmin)
admin.site.register(Ware, CompareVersionAdmin)
