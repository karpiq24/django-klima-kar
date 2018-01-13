from django.db.models import F, Sum, Max
from django.db.models.fields import FloatField

import django_tables2 as tables

from apps.warehouse.models import Ware, Invoice, Supplier, InvoiceItem


class WareTable(tables.Table):
    index = tables.Column(attrs={'th': {'width': '20%'}})
    name = tables.Column(attrs={'th': {'width': '25%'}})
    description = tables.Column(attrs={'th': {'width': '30%'}})
    stock = tables.Column(attrs={'th': {'width': '5%'}})
    last_price = tables.Column(attrs={'th': {'width': '13%'}}, verbose_name="Ostatnia cena")
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='warehouse/ware/ware_actions.html',
                                    orderable=False)

    def render_last_price(self, value):
        return "{} zł".format(value)

    def order_last_price(self, queryset, is_descending):
        queryset = queryset.annotate(
            max_price=Max('invoiceitem__price')).order_by(('-' if is_descending else '') + 'max_price')
        return (queryset, True)

    class Meta:
        model = Ware
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['index', 'name', 'description', 'last_price', 'stock']
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
    name = tables.Column(attrs={'th': {'width': '73%'}})
    all_invoices_value = tables.Column(attrs={'th': {'width': '20%'}}, verbose_name="Łączna wartość zakupów")
    actions = tables.TemplateColumn(attrs={'th': {'width': '7%'}}, verbose_name="Akcje",
                                    template_name='warehouse/supplier/supplier_actions.html',
                                    orderable=False)

    def render_all_invoices_value(self, value):
        return "{} zł".format(value)

    def order_all_invoices_value(self, queryset, is_descending):
        queryset = queryset.annotate(
            max_price=Sum('invoice__invoiceitem__price')).order_by(('-' if is_descending else '') + 'max_price')
        return (queryset, True)

    class Meta:
        model = Supplier
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['name', 'all_invoices_value']
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
