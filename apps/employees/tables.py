import django_tables2 as tables

from apps.employees.models import Employee, WorkAbsence
from apps.invoicing.models import Contractor


class EmployeeTable(tables.Table):
    first_name = tables.Column(attrs={"th": {"width": "20%"}})
    last_name = tables.Column(attrs={"th": {"width": "20%"}})
    email = tables.Column(attrs={"th": {"width": "20%"}})
    phone = tables.Column(attrs={"th": {"width": "20%"}})
    user = tables.Column(attrs={"th": {"width": "13%"}})
    actions = tables.TemplateColumn(
        attrs={"th": {"width": "7%"}},
        verbose_name="Akcje",
        template_name="employees/employee_actions.html",
        orderable=False,
        exclude_from_export=True,
    )

    class Meta:
        model = Employee
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = ["first_name", "last_name", "email", "phone", "user"]
        order_by = "last_name"
        empty_text = "Brak pracowników"

    def render_phone(self, value):
        return Contractor.format_phone_number(value)


class WorkAbsenceTable(tables.Table):
    reason = tables.Column(attrs={"th": {"width": "23%"}})
    date_from = tables.Column(attrs={"th": {"width": "23%"}})
    date_to = tables.Column(attrs={"th": {"width": "23%"}})
    comment = tables.Column(attrs={"th": {"width": "24%"}})
    actions = tables.TemplateColumn(
        attrs={"th": {"width": "7%"}},
        verbose_name="Akcje",
        template_name="employees/absence_actions.html",
        orderable=False,
        exclude_from_export=True,
    )

    class Meta:
        model = WorkAbsence
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = ["reason", "date_from", "date_to", "comment"]
        order_by = "-date_from"
        empty_text = "Brak nieobecności"
