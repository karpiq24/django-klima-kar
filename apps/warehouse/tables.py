import django_tables2 as tables


from apps.warehouse.models import Ware, Invoice, Supplier


class WareTable(tables.Table):
    index = tables.Column(attrs={'th': {'width': '20%'}})
    name = tables.Column(attrs={'th': {'width': '30%'}})
    description = tables.Column(attrs={'th': {'width': '45%'}})
    stock = tables.Column(attrs={'th': {'width': '5%'}})

    class Meta:
        model = Ware
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['index', 'name', 'description', 'stock']


class InvoiceTable(tables.Table):
    supplier = tables.Column(attrs={'th': {'width': '30%'}})
    number = tables.Column(attrs={'th': {'width': '30%'}})
    date = tables.Column(attrs={'th': {'width': '20%'}})
    total_value = tables.Column(attrs={'th': {'width': '20%'}})

    def render_total_value(self, value):
        return "{} zł".format(value)

    class Meta:
        model = Invoice
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['supplier', 'number', 'date', 'total_value']


class SupplierTable(tables.Table):
    class Meta:
        model = Supplier
        attrs = {'class': 'table table-striped table-hover table-bordered table-responsive'}
        fields = ['name']
