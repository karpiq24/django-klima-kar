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
    diffrence = tables.Column(
        attrs={'th': {'width': '38%'}})
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

    def render_diffrence(self, record):
        diff = record.get_diffrence(verbose=True)
        table = ('<table class="table table-dark">'
                 '<thead>'
                 '<tr>'
                 '{}'
                 '</tr>'
                 '</thead>'
                 '<tbody id="diff-body">'
                 '{}'
                 '</tbody></table>')
        rows = []
        headers = ('<th scope="col" class="bg-info" width="30%">Pole</th>'
                   '<th scope="col" class="bg-danger" width="35%">Było</th>'
                   '<th scope="col" class="bg-success" width="35%">Jest</th>')
        if record.action_type == AuditLog.CHANGE:
            for key, values in diff.items():
                val1 = values[0] if values[0] is not None else '—'
                val2 = values[1] if values[1] is not None else '—'
                rows.append(
                    '<tr>'
                    f'<td class="bg-info">{key}</td>'
                    f'<td class="bg-danger">{val1}</td>'
                    f'<td class="bg-success">{val2}</td>'
                    '</tr>'
                )
        elif record.action_type == AuditLog.DELETION:
            for key, value in diff.items():
                if value is None:
                    continue
                rows.append(
                    '<tr>'
                    f'<td class="bg-info">{key}</td>'
                    f'<td class="bg-danger">{value}</td>'
                    '<td class="bg-success">—</td>'
                    '</tr>'
                )
        return mark_safe(table.format(headers, '\n'.join(rows)))
