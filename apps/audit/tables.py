import django_tables2 as tables
from django.utils.safestring import mark_safe

from apps.audit.models import AuditLog


class AuditLogTable(tables.Table):
    action_time = tables.Column(
        attrs={'th': {'width': '15%'}})
    content_type = tables.Column(
        attrs={'th': {'width': '15%'}})
    object_repr = tables.Column(
        attrs={'th': {'width': '25%'}})
    diffrence = tables.TemplateColumn(
        attrs={'th': {'width': '38%'}},
        template_name='audit/audit_diffrence.html',
        extra_context={
            'ADDITION': AuditLog.ADDITION,
            'CHANGE': AuditLog.CHANGE,
            'DELETION': AuditLog.DELETION
        },
        orderable=False)
    actions = tables.TemplateColumn(
        attrs={'th': {'width': '7%'}},
        verbose_name="Akcje",
        template_name='audit/audit_actions.html',
        orderable=False,
        exclude_from_export=True)

    class Meta:
        CONTEXT_CLASS = {
            AuditLog.ADDITION: 'table-success',
            AuditLog.CHANGE: 'table-warning',
            AuditLog.DELETION: 'table-danger',
        }

        model = AuditLog
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['action_time', 'content_type', 'object_repr', 'diffrence', 'actions']
        order_by = '-action_time'
        empty_text = 'Brak logów'
        row_attrs = {
            'class': lambda record: {
                AuditLog.ADDITION: 'table-success',
                AuditLog.CHANGE: 'table-warning',
                AuditLog.DELETION: 'table-danger',
            }[record.action_type]
        }
