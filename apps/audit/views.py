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
