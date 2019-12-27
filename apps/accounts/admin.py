from django.contrib import admin

from apps.accounts.models import UserSession

# Register your models here.
admin.site.register(UserSession)
