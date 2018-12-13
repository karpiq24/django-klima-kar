# -*- coding: utf-8 -*-
from urllib.parse import urlencode

from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.generic import DetailView, UpdateView, CreateView, View
from django.db.models import Q, F

from django_tables2 import RequestConfig
from django_tables2.export.views import ExportMixin
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from KlimaKar.mixins import AjaxFormMixin
from apps.warehouse.models import Ware, Invoice, Supplier, InvoiceItem
from apps.warehouse.tables import WareTable, InvoiceTable, SupplierTable, InvoiceItemTable, InvoiceTableWithWare
from apps.warehouse.filters import WareFilter, InvoiceFilter, SupplierFilter
from apps.warehouse.forms import WareModelForm, InvoiceModelForm, SupplierModelForm, InvoiceItemsInline
from apps.warehouse.functions import generate_ware_inventory, check_ware_price_changes


class WareTableView(ExportMixin, FilteredSingleTableView):
    model = Ware
    table_class = WareTable
    filter_class = WareFilter
    template_name = 'warehouse/ware/ware_table.html'
    export_name = 'Towary'


class WareUpdateView(UpdateView):
    model = Ware
    form_class = WareModelForm
    template_name = 'warehouse/ware/ware_form.html'

    def get_context_data(self, **kwargs):
        context = super(WareUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Edycja towaru"
        return context

    def get_success_url(self, **kwargs):
        return reverse("warehouse:ware_detail", kwargs={'pk': self.object.pk})


class WareCreateView(CreateView):
    model = Ware
    form_class = WareModelForm
    template_name = 'warehouse/ware/ware_form.html'

    def get_context_data(self, **kwargs):
        context = super(WareCreateView, self).get_context_data(**kwargs)
        context['title'] = "Nowy towar"
        return context

    def get_success_url(self, **kwargs):
        return reverse("warehouse:ware_detail", kwargs={'pk': self.object.pk})


class WareDetailView(DetailView):
    model = Ware
    template_name = 'warehouse/ware/ware_detail.html'

    def get_context_data(self, **kwargs):
        context = super(WareDetailView, self).get_context_data(**kwargs)
        invoices = Invoice.objects.filter(invoiceitem__ware=context['ware']).annotate(
            ware_price=F('invoiceitem__price'), ware_quantity=F('invoiceitem__quantity'))
        table = InvoiceTableWithWare(invoices)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('warehouse:wares') + '?' + urlencode(self.request.session.get(key, ''))
        return context


class ExportWareInventory(View):
    def get(self, request, *args, **kwargs):
        queryset = Ware.objects.filter(stock__gte=1)
        output = generate_ware_inventory(queryset)
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=Remanent.xlsx"
        return response


class InvoiceTableView(ExportMixin, FilteredSingleTableView):
    model = Invoice
    table_class = InvoiceTable
    filter_class = InvoiceFilter
    template_name = 'warehouse/invoice/invoice_table.html'
    export_name = 'Faktury zakupowe'


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'warehouse/invoice/invoice_detail.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        table = InvoiceItemTable(InvoiceItem.objects.filter(invoice=context['invoice']))
        RequestConfig(self.request).configure(table)
        context['item_table'] = table
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('warehouse:invoices') + '?' + urlencode(self.request.session.get(key, ''))
        return context


class InvoiceCreateView(CreateWithInlinesView):
    model = Invoice
    form_class = InvoiceModelForm
    inlines = [InvoiceItemsInline]
    template_name = 'warehouse/invoice/invoice_form.html'

    def get_initial(self):
        '''
        Workaround for weird initial values caching from another app.
        '''
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowa faktura zakupowa"
        return context

    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)
        check_ware_price_changes(self.object)
        return response

    def get_success_url(self):
        return reverse("warehouse:invoice_detail", kwargs={'pk': self.object.pk})


class InvoiceUpdateView(UpdateWithInlinesView):
    model = Invoice
    form_class = InvoiceModelForm
    inlines = [InvoiceItemsInline]
    template_name = 'warehouse/invoice/invoice_form.html'

    def get_initial(self):
        '''
        Workaround for weird initial values caching from another app.
        '''
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja faktury zakupowej"
        return context

    def get_success_url(self):
        return reverse("warehouse:invoice_detail", kwargs={'pk': self.object.pk})


class SupplierTableView(ExportMixin, FilteredSingleTableView):
    model = Supplier
    table_class = SupplierTable
    filter_class = SupplierFilter
    template_name = 'warehouse/supplier/supplier_table.html'
    export_name = 'Dostawcy'


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'warehouse/supplier/supplier_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierDetailView, self).get_context_data(**kwargs)
        table = InvoiceTable(Invoice.objects.filter(supplier=context['supplier']))
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('warehouse:suppliers') + '?' + urlencode(self.request.session.get(key, ''))
        return context


class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierModelForm
    template_name = 'warehouse/supplier/supplier_form.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Edycja dostawcy"
        return context

    def get_success_url(self, **kwargs):
        return reverse("warehouse:supplier_detail", kwargs={'pk': self.object.pk})


class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierModelForm
    template_name = 'warehouse/supplier/supplier_form.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierCreateView, self).get_context_data(**kwargs)
        context['title'] = "Nowy dostawca"
        return context

    def get_success_url(self, **kwargs):
        return reverse("warehouse:supplier_detail", kwargs={'pk': self.object.pk})


class WareCreateAjaxView(AjaxFormMixin, CreateView):
    model = Ware
    form_class = WareModelForm
    title = "Nowy towar"


class GetWareData(View):
    def get(self, *args, **kwargs):
        ware_index = self.request.GET.get('index', None)
        ware_pk = self.request.GET.get('pk', None)
        ware = None
        if ware_index:
            ware = Ware.objects.get(index=ware_index)
        elif ware_pk:
            ware = Ware.objects.get(pk=ware_pk)
        if ware:
            response = {
                'index': ware.index,
                'name': ware.name,
                'last_price': ware.last_price or 0
            }
            return JsonResponse({'status': 'ok',
                                 'ware': response})
        return JsonResponse({'status': 'error', 'ware': []})


class WareAutocomplete(CustomSelect2QuerySetView):
    def get_queryset(self):
        qs = Ware.objects.all()
        if self.q:
            qs = qs.filter(Q(index__icontains=self.q) | Q(index_slug__icontains=self.q))
        return qs


class WareNameAutocomplete(View):
    def get(self, *args, **kwargs):
        query = self.request.GET.get('query')
        result = []
        if query:
            data = Ware.objects.filter(name__icontains=query).values_list(
                'name', flat=True).distinct().order_by('name')[:10]
            result = list(data)
        return JsonResponse({'suggestions': result})

    def create(self, text):
        return text


class SupplierAutocomplete(CustomSelect2QuerySetView):
    def get_queryset(self):
        qs = Supplier.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
