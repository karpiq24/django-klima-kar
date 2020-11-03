from django.contrib import admin

from apps.employees.models import Employee, WorkAbsence

admin.site.register(Employee)
admin.site.register(WorkAbsence)
