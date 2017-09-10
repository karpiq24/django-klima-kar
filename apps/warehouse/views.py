from django_tables2 import SingleTableView

from apps.warehouse.models import Ware, Invoice, Supplier
from apps.warehouse.tables import WareTable, InvoiceTable, SupplierTable
from apps.warehouse.filters import WareFilter, InvoiceFilter, SupplierFilter


class FilteredSingleTableView(SingleTableView):
    filter_class = None

    def get_table_data(self):
        data = super(FilteredSingleTableView, self).get_table_data()
        self.filter = self.filter_class(self.request.GET, queryset=data)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(FilteredSingleTableView, self).get_context_data(**kwargs)
        context['filter'] = self.filter
        return context


class WareFilteredSingleTableView(FilteredSingleTableView):
    model = Ware
    table_class = WareTable
    filter_class = WareFilter
    template_name = 'warehouse/ware_table.html'


class InvoiceFilteredSingleTableView(FilteredSingleTableView):
    model = Invoice
    table_class = InvoiceTable
    filter_class = InvoiceFilter
    template_name = 'warehouse/invoice_table.html'


class SupplierFilteredSingleTableView(FilteredSingleTableView):
    model = Supplier
    table_class = SupplierTable
    filter_class = SupplierFilter
    template_name = 'warehouse/supplier_table.html'
