from urllib.parse import urlencode

from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.generic import DetailView, UpdateView, CreateView, View
from django.db.models import Q, F
from django.contrib import messages

from django_tables2.export.views import ExportMixin
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from KlimaKar.mixins import AjaxFormMixin, SingleTableAjaxMixin
from KlimaKar.templatetags.slugify import slugify
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

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("warehouse:ware_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)})


class WareCreateView(CreateView):
    model = Ware
    form_class = WareModelForm
    template_name = 'warehouse/ware/ware_form.html'

    def get_context_data(self, **kwargs):
        context = super(WareCreateView, self).get_context_data(**kwargs)
        context['title'] = "Nowy towar"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejny towar.</a>'.format(
                reverse('warehouse:ware_create')))
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("warehouse:ware_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)})


class WareDetailView(SingleTableAjaxMixin, DetailView):
    model = Ware
    template_name = 'warehouse/ware/ware_detail.html'
    table_class = InvoiceTableWithWare

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('warehouse:wares') + '?' + urlencode(self.request.session.get(key, ''))
        return context

    def get_table_data(self):
        return Invoice.objects.filter(invoiceitem__ware=self.object).annotate(
            ware_price=F('invoiceitem__price'), ware_quantity=F('invoiceitem__quantity'))


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


class InvoiceDetailView(SingleTableAjaxMixin, DetailView):
    model = Invoice
    template_name = 'warehouse/invoice/invoice_detail.html'
    table_class = InvoiceItemTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('warehouse:invoices') + '?' + urlencode(self.request.session.get(key, ''))
        return context

    def get_table_data(self):
        return InvoiceItem.objects.filter(invoice=self.object)


class InvoiceCreateView(CreateWithInlinesView):
    model = Invoice
    form_class = InvoiceModelForm
    inlines = [InvoiceItemsInline]
    template_name = 'warehouse/invoice/invoice_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowa faktura zakupowa"
        return context

    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)
        check_ware_price_changes(self.object)
        messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejną fakturę.</a>'.format(
                reverse('warehouse:invoice_create')))
        return response

    def get_success_url(self):
        return reverse("warehouse:invoice_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)
        })


class InvoiceUpdateView(UpdateWithInlinesView):
    model = Invoice
    form_class = InvoiceModelForm
    inlines = [InvoiceItemsInline]
    template_name = 'warehouse/invoice/invoice_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja faktury zakupowej"
        return context

    def forms_valid(self, form, inlines):
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("warehouse:invoice_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)
        })


class SupplierTableView(ExportMixin, FilteredSingleTableView):
    model = Supplier
    table_class = SupplierTable
    filter_class = SupplierFilter
    template_name = 'warehouse/supplier/supplier_table.html'
    export_name = 'Dostawcy'


class SupplierDetailView(SingleTableAjaxMixin, DetailView):
    model = Supplier
    template_name = 'warehouse/supplier/supplier_detail.html'
    table_class = InvoiceTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('warehouse:suppliers') + '?' + urlencode(self.request.session.get(key, ''))
        if self.get_table_data().count() > 3:
            context['chart'] = {
                'title': 'Historia zakupów',
                'url': reverse('stats:purchase_invoices_history_per_supplier', kwargs={'supplier': self.object.pk}),
                'select_date': {
                    'extra': True,
                    'default': 'year'
                },
                'custom_select': [('Sum', 'Suma'), ('Avg', 'Średnia'), ('Count', 'Ilość')]
            }
        return context

    def get_table_data(self):
        return Invoice.objects.filter(supplier=self.object)


class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierModelForm
    template_name = 'warehouse/supplier/supplier_form.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Edycja dostawcy"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("warehouse:supplier_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)
        })


class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierModelForm
    template_name = 'warehouse/supplier/supplier_form.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierCreateView, self).get_context_data(**kwargs)
        context['title'] = "Nowy dostawca"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejnego dostawcę.</a>'.format(
                reverse('warehouse:supplier_create')))
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("warehouse:supplier_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)
        })


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
