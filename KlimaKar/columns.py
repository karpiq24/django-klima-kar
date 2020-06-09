from django.template import Context, Template
from django.template.loader import get_template

from django_tables2.columns import TemplateColumn, library


@library.register
class RequestTemplateColumn(TemplateColumn):
    def render(self, record, table, value, bound_column, **kwargs):
        context = getattr(table, "context", Context())
        context.update(self.extra_context)
        context.update(
            {
                "default": bound_column.default,
                "column": bound_column,
                "record": record,
                "value": value,
                "row_counter": kwargs["bound_row"].row_counter,
                "request": table.request
            }
        )

        try:
            if self.template_code:
                return Template(self.template_code).render(context)
            else:
                return get_template(self.template_name).render(context.flatten())
        finally:
            context.pop()
