from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    name = "apps.employees"

    def ready(self):
        from apps.annotations.registry import annotations
        from apps.employees.models import Employee

        annotations.register(Employee)
