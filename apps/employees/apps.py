from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    name = "apps.employees"

    def ready(self):
        from apps.annotations.registry import annotations
        from apps.audit.registry import audit
        from apps.employees.models import Employee, WorkAbsence

        annotations.register(Employee)
        audit.register(Employee)
        audit.register(WorkAbsence)
