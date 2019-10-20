from django.contrib import admin
from apps.commission.models import Component, Vehicle, Commission


admin.site.register(Component)
admin.site.register(Vehicle)
admin.site.register(Commission)
