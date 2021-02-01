from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin

from django_tables2 import SingleTableMixin
from django_tables2.views import TableMixinBase
from django_tables2.config import RequestConfig


class StaffOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class SuperUserOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class AjaxFormMixin(object):
    title = None
    url = None
    identifier = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["url"] = self.request.path
        context["identifier"] = self.identifier
        return context

    def get(self, *args, **kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            self.initial = self.request.GET.dict()
            super().get(self.request)
            html_form = render_to_string(
                "forms/modal_form.html", self.get_context_data(), request=self.request,
            )
            return JsonResponse({"html_form": html_form})
        return JsonResponse({"error": "Not allowed"})

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html_form = render_to_string(
                "forms/modal_form.html", self.get_context_data(), request=self.request,
            )
            return JsonResponse({"html_form": html_form}, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = (
                dict(
                    {"pk": self.object.pk, "text": str(self.object)},
                    **self.extend_result_data(self.object)
                )
                if hasattr(self, "object")
                else {}
            )
            return JsonResponse(data)
        else:
            return response

    def extend_result_data(self, data):
        return {}

    def get_success_url(self, **kwargs):
        return None


class SingleTableAjaxMixin(SingleTableMixin):
    table_pagination = {"per_page": 10}

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            table = self.get_table(**self.get_table_kwargs())
            return JsonResponse({"table": table.as_html(request)})
        else:
            return response


class MultiTableAjaxMixin(TableMixinBase):
    table_pagination = {"per_page": 10}
    table_classes = None
    table_data = None
    tables_context_key = "tables"

    def get(self, request, *args, **kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            table_id = request.GET.get("table_id")
            table = self.get_table(table_id, **self.get_table_kwargs(table_id))
            return JsonResponse({"table": table.as_html(request)})
        else:
            return super().get(request, args, kwargs)

    def get_table_class(self, table_id):
        if self.table_classes and self.table_classes.get(table_id):
            return self.table_classes.get(table_id)

        raise ImproperlyConfigured(
            "You must specify {0}.table_classes".format(type(self).__name__)
        )

    def get_table(self, table_id, **kwargs):
        table_class = self.get_table_class(table_id)
        table = table_class(data=self.get_table_data(table_id), **kwargs)
        table.table_id = table_id
        return RequestConfig(
            self.request, paginate=self.get_table_pagination(table)
        ).configure(table)

    def get_table_data(self, table_id):
        if self.table_data and self.table_data.get("table_id"):
            return self.table_data["table_id"]
        elif hasattr(self, "get_tables_data"):
            return self.get_tables_data()[table_id]

        klass = type(self).__name__
        raise ImproperlyConfigured(
            "Table data was not specified. Define {}.table_data".format(klass)
        )

    def get_table_kwargs(self, table_id):
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tables = {}
        for table_id, klass in self.table_classes.items():
            tables[table_id] = self.get_table(
                table_id, **self.get_table_kwargs(table_id)
            )
        context[self.tables_context_key] = tables
        return context


class ObjectEditableAccessMixin(object):
    def dispatch(self, *args, **kwargs):
        object = self.get_object()
        if self.request.user.is_staff:
            return super().dispatch(*args, **kwargs)
        if not object.is_editable:
            raise PermissionDenied
        return super().dispatch(*args, **kwargs)
