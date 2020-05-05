import django_tables2 as tables

from apps.invoicing.models import (
    Contractor,
    SaleInvoice,
    SaleInvoiceItem,
    ServiceTemplate,
)


class ContractorTable(tables.Table):
    name = tables.Column(attrs={"th": {"width": "36%"}})
    nip = tables.Column(attrs={"th": {"width": "15%"}})
    phone = tables.TemplateColumn(
        attrs={"th": {"width": "10%"}},
        empty_values=(),
        template_name="invoicing/contractor/phone_table_field.html",
        verbose_name="Telefon",
    )
    address_1 = tables.Column(attrs={"th": {"width": "20%"}})
    city = tables.Column(attrs={"th": {"width": "12%"}})
    actions = tables.TemplateColumn(
        attrs={"th": {"width": "7%"}},
        verbose_name="Akcje",
        template_name="invoicing/contractor/table_actions.html",
        orderable=False,
        exclude_from_export=True,
    )

    def render_nip(self, record):
        return "{}{}".format(record.nip_prefix or "", record.nip)

    def order_phone(self, queryset, is_descending):
        queryset = queryset.order_by(
            ("-" if is_descending else "") + "phone_1",
            ("-" if is_descending else "") + "phone_2",
        )
        return (queryset, True)

    class Meta:
        model = Contractor
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = ["name", "nip", "phone", "address_1", "city", "actions"]
        order_by = "name"
        empty_text = "Brak kontrahentów"


class SaleInvoiceTable(tables.Table):
    number = tables.Column(attrs={"th": {"width": "22%"}}, verbose_name="Numer faktury")
    contractor = tables.Column(attrs={"th": {"width": "36%"}})
    issue_date = tables.Column(
        attrs={"th": {"width": "15%"}}, verbose_name="Data wystawienia"
    )
    total_value_brutto = tables.Column(
        attrs={"th": {"width": "20%"}}, empty_values=(), verbose_name="Cena brutto"
    )
    actions = tables.TemplateColumn(
        attrs={"th": {"width": "7%"}},
        verbose_name="Akcje",
        template_name="invoicing/sale_invoice/table_actions.html",
        orderable=False,
        exclude_from_export=True,
    )

    def render_total_value_brutto(self, value):
        return "{0:.2f} zł".format(value or 0).replace(".", ",")

    def order_total_value_brutto(self, queryset, is_descending):
        queryset = queryset.order_by_total(is_descending, price_type="brutto")
        return (queryset, True)

    def order_number(self, queryset, is_descending):
        queryset = queryset.order_by(
            ("-" if is_descending else "") + "number_year",
            ("-" if is_descending else "") + "number_value",
        )
        return (queryset, True)

    class Meta:
        model = SaleInvoice
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = ["number", "contractor", "issue_date", "total_value_brutto"]
        order_by = "-number"
        empty_text = "Brak faktur"


class SaleInvoiceWithTypeTable(SaleInvoiceTable):
    invoice_type = tables.Column(attrs={"th": {"width": "10%"}})

    class Meta:
        model = SaleInvoice
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = [
            "invoice_type",
            "number",
            "contractor",
            "issue_date",
            "total_value_brutto",
        ]
        order_by = "-number"
        empty_text = "Brak faktur"


class SaleInvoiceItemTable(tables.Table):
    name = tables.Column(
        attrs={
            "th": {"width": "20%"},
            "tf": {"colspan": "4", "class": "text-right border-right-0"},
        },
        verbose_name="Nazwa usługi/towaru",
        footer="Razem:",
    )
    description = tables.Column(
        attrs={"th": {"width": "20%"}, "tf": {"class": "d-none"}},
        verbose_name="Opis usługi/towaru",
    )
    ware = tables.Column(attrs={"th": {"width": "10%"}, "tf": {"class": "d-none"}})
    quantity = tables.Column(attrs={"th": {"width": "10%"}, "tf": {"class": "d-none"}})
    price_netto = tables.Column(
        attrs={"th": {"width": "20%"}, "tf": {"class": "border-left-0 border-right-0"}},
        verbose_name="Cena netto",
        footer=lambda table: "{0:.2f} zł".format(
            table.data[0].sale_invoice.total_value_netto if table.data else 0
        ).replace(".", ","),
    )
    price_brutto = tables.Column(
        attrs={"th": {"width": "20%"}, "tf": {"class": "border-left-0"}},
        verbose_name="Cena brutto",
        footer=lambda table: "{0:.2f} zł".format(
            table.data[0].sale_invoice.total_value_brutto
        ).replace(".", ","),
    )

    def render_price_netto(self, value):
        return "{0:.2f} zł".format(value).replace(".", ",")

    def render_price_brutto(self, value):
        return "{0:.2f} zł".format(value).replace(".", ",")

    class Meta:
        model = SaleInvoiceItem
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = [
            "name",
            "description",
            "ware",
            "quantity",
            "price_netto",
            "price_brutto",
        ]
        empty_text = "Brak pozycji"


class ServiceTemplateTable(tables.Table):
    name = tables.Column(
        attrs={"th": {"width": "25%"}}, verbose_name="Nazwa usługi/towaru"
    )
    description = tables.Column(
        attrs={"th": {"width": "25%"}}, verbose_name="Opis usługi/towaru"
    )
    ware = tables.Column(attrs={"th": {"width": "13%"}})
    quantity = tables.Column(attrs={"th": {"width": "10%"}})
    price_netto = tables.Column(attrs={"th": {"width": "10%"}})
    price_brutto = tables.Column(attrs={"th": {"width": "10%"}})
    actions = tables.TemplateColumn(
        attrs={"th": {"width": "7%"}},
        verbose_name="Akcje",
        template_name="invoicing/service_template/table_actions.html",
        orderable=False,
    )

    def render_price_netto(self, value):
        return "{0:.2f} zł".format(value).replace(".", ",")

    def render_price_brutto(self, value):
        return "{0:.2f} zł".format(value).replace(".", ",")

    class Meta:
        model = ServiceTemplate
        attrs = {"class": "table table-striped table-hover table-bordered"}
        fields = ["name", "description", "ware", "price_netto", "price_brutto"]
        empty_text = "Brak pozycji"
