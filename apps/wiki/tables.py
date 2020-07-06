import django_tables2 as tables

from apps.wiki.models import Article


class ArticleTable(tables.Table):
    image = tables.Column(attrs={"th": {"width": "73%"}})
    contents = tables.Column(
        attrs={"th": {"width": "20%"}}, verbose_name="Łączna wartość zakupów"
    )
    actions = tables.TemplateColumn(
        attrs={"th": {"width": "7%"}},
        verbose_name="Akcje",
        template_name="warehouse/supplier/supplier_actions.html",
        orderable=False,
        exclude_from_export=True,
    )

    class Meta:
        model = Article
        fields = ["image", "contents", "actions"]
        order_by = "-pk"
        empty_text = "Brak artykułów"
        template_name = "wiki/article/article_table.html"
