from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.views.generic import TemplateView

from apps.audit.tables import AuditLogTable, ObjectAuditLogTable
from apps.audit.models import AuditLog
from apps.audit.filters import AuditLogFilter
from KlimaKar.views import FilteredSingleTableView
from KlimaKar.mixins import StaffOnlyMixin, SingleTableAjaxMixin


class AuditLogTableView(StaffOnlyMixin, FilteredSingleTableView):
    model = AuditLog
    table_class = AuditLogTable
    filter_class = AuditLogFilter
    template_name = "audit/audit_table.html"


class ObjectAuditLogTableView(StaffOnlyMixin, SingleTableAjaxMixin, TemplateView):
    table_class = ObjectAuditLogTable
    template_name = "audit/object_audit_table.html"
    table_pagination = {"per_page": 25}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.object
        return context

    def get_table_data(self):
        model = ContentType.objects.get_for_id(
            self.kwargs["content_type"]
        ).model_class()
        try:
            self.object = model.objects.get(pk=self.kwargs.get("object_id"))
        except model.DoesNotExist:
            raise Http404
        return self.object.get_logs()
