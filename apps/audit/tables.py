import django_tables2 as tables

from apps.audit.models import AuditLog


class AuditLogTable(tables.Table):
    user = tables.Column(attrs={"th": {"width": "5%"}})
    action_time = tables.Column(attrs={"th": {"width": "15%"}})
    content_type = tables.Column(
        attrs={"th": {"width": "15%"}}, accessor="content_type.name",
    )
    object_repr = tables.Column(attrs={"th": {"width": "20%"}})
    difference = tables.TemplateColumn(
        attrs={"th": {"width": "38%"}},
        template_name="audit/audit_difference.html",
        extra_context={
            "ADDITION": AuditLog.ADDITION,
            "CHANGE": AuditLog.CHANGE,
            "DELETION": AuditLog.DELETION,
        },
        orderable=False,
    )
    actions = tables.TemplateColumn(
        attrs={"th": {"width": "7%"}},
        verbose_name="Akcje",
        template_name="audit/audit_actions.html",
        orderable=False,
        exclude_from_export=True,
    )

    class Meta:
        CONTEXT_CLASS = {
            AuditLog.ADDITION: "table-success",
            AuditLog.CHANGE: "table-warning",
            AuditLog.DELETION: "table-danger",
        }

        model = AuditLog
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = [
            "user",
            "action_time",
            "content_type",
            "object_repr",
            "difference",
            "actions",
        ]
        order_by = "-action_time"
        empty_text = "Brak logów"
        row_attrs = {
            "class": lambda record: {
                AuditLog.ADDITION: "table-success",
                AuditLog.CHANGE: "table-warning",
                AuditLog.DELETION: "table-danger",
            }[record.action_type]
        }

    def order_content_type(self, queryset, is_descending):
        queryset = queryset.order_by(
            ("-" if is_descending else "") + "content_type__app_label",
            ("-" if is_descending else "") + "content_type__model",
        )
        return (queryset, True)


class ObjectAuditLogTable(AuditLogTable):
    actions = None

    class Meta(AuditLogTable.Meta):
        fields = [
            "user",
            "action_time",
            "content_type",
            "object_repr",
            "difference",
        ]
