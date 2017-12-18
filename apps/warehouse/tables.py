from django.db.models import F, Sum
from django.db.models.fields import FloatField

import django_tables2 as tables

from apps.warehouse.models import Ware, Invoice, Supplier, InvoiceItem


class WareTable(tables.Table):
    index = tables.Column(attrs={'th': {'width': '20%'}})
    name = tables.Column(attrs={'th': {'width': '30%'}})
    description = tables.Column(attrs={'th': {'width': '38%'}})
    stock = tables.Column(attrs={'th': {'width': '5%'}})
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='warehouse/ware/ware_actions.html',
                                    orderable=False)

    class Meta:
        model = Ware
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['index', 'name', 'description', 'stock']
        order_by = 'index'
        empty_text = 'Brak towarów'


class InvoiceTable(tables.Table):
    supplier = tables.Column(attrs={'th': {'width': '28%'}}, verbose_name="Dostawca")
    number = tables.Column(attrs={'th': {'width': '30%'}}, verbose_name="Numer faktury")
    date = tables.Column(attrs={'th': {'width': '20%'}}, verbose_name="Data")
    total_value = tables.Column(attrs={'th': {'width': '15%'}}, verbose_name="Łączna wartość")
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='warehouse/invoice/invoice_actions.html',
                                    orderable=False)

    def render_total_value(self, value):
        return "{} zł".format(value)

    class Meta:
        model = Invoice
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['supplier', 'number', 'date', 'total_value']
        order_by = '-date'
        empty_text = 'Brak faktur'


class SupplierTable(tables.Table):
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='warehouse/supplier/supplier_actions.html',
                                    orderable=False)

    class Meta:
        model = Supplier
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['name']
        order_by = 'name'
        empty_text = 'Brak dostawców'


class InvoiceItemTable(tables.Table):
    index = tables.Column(attrs={'th': {'width': '28%'}}, accessor='ware.index')
    name = tables.Column(attrs={'th': {'width': '35%'}}, accessor='ware.name')
    quantity = tables.Column(attrs={'th': {'width': '10%'}})
    price = tables.Column(attrs={'th': {'width': '10%'}}, verbose_name="Cena netto")
    total = tables.Column(attrs={'th': {'width': '10%'}}, empty_values=(), verbose_name="Razem")
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='warehouse/invoice/invoiceitem_actions.html',
                                    orderable=False)

    class Meta:
        model = InvoiceItem
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['index', 'name', 'quantity', 'price', 'total']
        empty_text = 'Brak towarów'

    def render_price(self, value):
        return "{} zł".format(value)

    def render_total(self, record):
        return "{} zł".format(record.quantity * record.price)

    def order_total(self, queryset, is_descending):
        queryset = queryset.annotate(
            total=Sum(F('quantity') * F('price'), output_field=FloatField())
        ).order_by(('-' if is_descending else '') + 'total')
        return (queryset, True)
