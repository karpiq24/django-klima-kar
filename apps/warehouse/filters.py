import django_filters

from apps.warehouse.models import Ware, Invoice, Supplier


class WareFilter(django_filters.FilterSet):
    class Meta:
        model = Ware
        fields = {
            'index': ['icontains'],
            'name': ['icontains'],
            'description': ['icontains'],
        }


class InvoiceFilter(django_filters.FilterSet):
    class Meta:
        model = Invoice
        exclude = ['id', 'items', 'total_value']


class SupplierFilter(django_filters.FilterSet):
    class Meta:
        model = Supplier
        exclude = ['id']
