from django.contrib import admin
from apps.commission.models import (
    Component,
    Vehicle,
    Commission,
    CommissionFile,
    CommissionItem,
)


admin.site.register(Component)
admin.site.register(Vehicle)
admin.site.register(Commission)
admin.site.register(CommissionItem)
admin.site.register(CommissionFile)
