import django_tables2 as tables

from apps.invoicing.models import Contractor, SaleInvoice, SaleInvoiceItem, ServiceTemplate


class ContractorTable(tables.Table):
    name = tables.Column(attrs={'th': {'width': '38%'}})
    nip = tables.Column(attrs={'th': {'width': '15%'}})
    address_1 = tables.Column(attrs={'th': {'width': '25%'}})
    city = tables.Column(attrs={'th': {'width': '15%'}})
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='invoicing/contractor/table_actions.html',
                                    orderable=False)

    def render_nip(self, record):
        return "{}{}".format(record.nip_prefix or '', record.nip)

    class Meta:
        model = Contractor
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['name', 'nip', 'address_1', 'city', 'actions']
        order_by = 'name'
        empty_text = 'Brak kontrahentów'


class SaleInvoiceTable(tables.Table):
    invoice_type = tables.Column(attrs={'th': {'width': '10%'}}, verbose_name="Rodzaj faktury")
    number = tables.Column(attrs={'th': {'width': '20%'}}, verbose_name="Numer faktury")
    contractor = tables.Column(attrs={'th': {'width': '30%'}})
    issue_date = tables.Column(attrs={'th': {'width': '13%'}}, verbose_name="Data wystawienia")
    total_value_netto = tables.Column(attrs={'th': {'width': '20%'}}, verbose_name="Łączna wartość netto")
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='invoicing/sale_invoice/table_actions.html',
                                    orderable=False)

    def render_total_value_netto(self, value):
        return "{0:.2f} zł".format(value).replace('.', ',')

    def order_number(self, queryset, is_descending):
        queryset = queryset.order_by(
            ('-' if is_descending else '') + 'number_year',
            ('-' if is_descending else '') + 'number_value')
        return (queryset, True)

    class Meta:
        model = SaleInvoice
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['invoice_type', 'number', 'contractor', 'issue_date', 'total_value_netto']
        order_by = '-number'
        empty_text = 'Brak faktur'


class SaleInvoiceItemTable(tables.Table):
    name = tables.Column(attrs={'th': {'width': '20%'}}, verbose_name="Nazwa usługi/towaru")
    description = tables.Column(attrs={'th': {'width': '20%'}}, verbose_name="Opis usługi/towaru")
    ware = tables.Column(attrs={'th': {'width': '10%'}})
    quantity = tables.Column(attrs={'th': {'width': '10%'}})
    price_netto = tables.Column(attrs={'th': {'width': '20%'}}, verbose_name="Cena netto")
    price_brutto = tables.Column(attrs={'th': {'width': '20%'}}, verbose_name="Cena brutto")

    def render_price_netto(self, value):
        return "{0:.2f} zł".format(value).replace('.', ',')

    def render_price_brutto(self, value):
        return "{0:.2f} zł".format(value).replace('.', ',')

    class Meta:
        model = SaleInvoiceItem
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['name', 'description', 'ware', 'quantity', 'price_netto', 'price_brutto']
        empty_text = 'Brak pozycji'


class ServiceTemplateTable(tables.Table):
    name = tables.Column(attrs={'th': {'width': '40%'}}, verbose_name="Nazwa usługi/towaru")
    description = tables.Column(attrs={'th': {'width': '40%'}}, verbose_name="Opis usługi/towaru")
    ware = tables.Column(attrs={'th': {'width': '13%'}})
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='invoicing/service_template/table_actions.html',
                                    orderable=False)

    class Meta:
        model = ServiceTemplate
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['name', 'description', 'ware']
        empty_text = 'Brak pozycji'
