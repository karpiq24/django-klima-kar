from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.audit.tables import AuditLogTable
from apps.audit.models import AuditLog
from apps.audit.filters import AuditLogFilter
from KlimaKar.views import FilteredSingleTableView
from KlimaKar.mixins import GroupAccessControlMixin


class AuditLogTableView(GroupAccessControlMixin, FilteredSingleTableView):
    allowed_groups = ['boss']
    model = AuditLog
    table_class = AuditLogTable
    filter_class = AuditLogFilter
    template_name = 'audit/audit_table.html'


class GetAuditLogDiffrence(GroupAccessControlMixin, View):
    allowed_groups = ['boss']

    def get(self, request, *args, **kwargs):
        audit_log = get_object_or_404(AuditLog, pk=request.GET.get('pk'))
        if not audit_log.diffrence:
            return JsonResponse({})
        return JsonResponse(audit_log.get_diffrence(verbose=True))
