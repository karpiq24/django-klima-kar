from django.contrib import admin
from apps.audit.models import AuditLog


admin.site.register(AuditLog)
