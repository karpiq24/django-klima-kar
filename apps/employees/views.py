from urllib.parse import urlencode

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, UpdateView, CreateView
from django.contrib import messages

from django_tables2.export.views import ExportMixin

from KlimaKar.mixins import AjaxFormMixin, SingleTableAjaxMixin
from KlimaKar.views import FilteredSingleTableView

from KlimaKar.templatetags.slugify import slugify
from apps.employees.filters import EmployeeFilter
from apps.employees.forms import EmployeeModelForm, WorkAbsenceModelForm
from apps.employees.models import Employee, WorkAbsence
from apps.employees.tables import EmployeeTable, WorkAbsenceTable


class EmployeeTableView(ExportMixin, FilteredSingleTableView):
    model = Employee
    table_class = EmployeeTable
    filter_class = EmployeeFilter
    template_name = "employees/employee_table.html"
    export_name = "Pracownicy"


class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeModelForm
    template_name = "employees/employee_form.html"

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Zapisano zmiany.")
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse(
            "employees:employee_detail",
            kwargs={"pk": self.object.pk, "slug": slugify(self.object)},
        )


class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeModelForm
    template_name = "employees/employee_form.html"

    def form_valid(self, form):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            '<a href="{}">Dodaj kolejnego pracownika.</a>'.format(
                reverse("employees:employee_create")
            ),
        )
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse(
            "employees:employee_detail",
            kwargs={"pk": self.object.pk, "slug": slugify(self.object)},
        )


class EmployeeDetailView(SingleTableAjaxMixin, DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    table_class = WorkAbsenceTable
    table_pagination = {"per_page": 20}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context["back_url"] = (
            reverse("employees:employees")
            + "?"
            + urlencode(self.request.session.get(key, ""))
        )
        return context

    def get_table_data(self):
        return WorkAbsence.objects.filter(employee=self.object)


class WorkAbsenceCreateAjaxView(AjaxFormMixin, CreateView):
    model = WorkAbsence
    form_class = WorkAbsenceModelForm
    title = "Nowa nieobecność"


class WorkAbsenceUpdateAjaxView(AjaxFormMixin, UpdateView):
    model = WorkAbsence
    form_class = WorkAbsenceModelForm
    title = "Edycja nieobecności"


class WorkAbsenceRemoveView(View):
    def post(self, request, *args, **kwargs):
        absence = get_object_or_404(WorkAbsence, pk=kwargs.get("pk"))
        absence.delete()
        return JsonResponse(
            {"status": "success", "message": "Nieobecność została usunięta."},
            status=200,
        )
