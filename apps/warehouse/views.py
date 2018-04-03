# -*- coding: utf-8 -*-

from django.urls import reverse
from django.db import IntegrityError, transaction
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.generic import DetailView, UpdateView, CreateView, View
from django.db.models import Q, F

from django_tables2 import RequestConfig
from dal import autocomplete

from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from KlimaKar.mixins import AjaxFormMixin
from apps.warehouse.models import Ware, Invoice, Supplier, InvoiceItem
from apps.warehouse.tables import WareTable, InvoiceTable, SupplierTable, InvoiceItemTable, InvoiceTableWithWare
from apps.warehouse.filters import WareFilter, InvoiceFilter, SupplierFilter
from apps.warehouse.forms import (
    WareModelForm, InvoiceModelForm, SupplierModelForm, InvoiceItemModelForm)
from apps.warehouse.functions import export_wares


class WareTableView(FilteredSingleTableView):
    model = Ware
    table_class = WareTable
    filter_class = WareFilter
    template_name = 'warehouse/ware/ware_table.html'

    def get(self, request, *args, **kwargs):
        if 'export' in request.path:
            key = "{}_params".format(self.filter_class)
            queryset = self.filter_class(request.session[key], queryset=self.model.objects.all()).qs
            output = export_wares(queryset)
            response = HttpResponse(output.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = "attachment; filename=eksport_towarow.xlsx"
            return response
        return super(FilteredSingleTableView, self).get(request, *args, **kwargs)


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
            ware_price=F('invoiceitem__price'))
        table = InvoiceTableWithWare(invoices)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        return context


class InvoiceTableView(FilteredSingleTableView):
    model = Invoice
    table_class = InvoiceTable
    filter_class = InvoiceFilter
    template_name = 'warehouse/invoice/invoice_table.html'


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'warehouse/invoice/invoice_detail.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        table = InvoiceItemTable(InvoiceItem.objects.filter(invoice=context['invoice']))
        RequestConfig(self.request).configure(table)
        context['item_table'] = table
        return context


class InvoiceFormMixin():
    model = Invoice
    form_class = InvoiceModelForm
    template_name = 'warehouse/invoice/invoice_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        InvoiceItemFormSet = modelformset_factory(
            InvoiceItem, form=InvoiceItemModelForm, extra=10, can_delete=True)
        item_data = []
        if self.object:
            items = InvoiceItem.objects.filter(invoice=self.object)
            item_data = [{'ware': i.ware, 'quantity': i.quantity, 'price': i.price} for i in items]
        if self.request.POST:
            item_formset = InvoiceItemFormSet(
                self.request.POST, queryset=InvoiceItem.objects.none(), prefix='item')
        else:
            item_formset = InvoiceItemFormSet(
                initial=item_data, queryset=InvoiceItem.objects.none(), prefix='item')
        context['item_formset'] = item_formset
        return context

    def form_valid(self, form):
        ctx = self.get_context_data()
        item_formset = ctx['item_formset']

        if form.is_valid() and item_formset.is_valid():
            self.object = form.save()
            new_items = []
            for item_form in item_formset:
                if item_form.cleaned_data.get('DELETE', True):
                    continue
                ware = item_form.cleaned_data.get('ware')
                price = item_form.cleaned_data.get('price')
                quantity = item_form.cleaned_data.get('quantity')

                if ware and price and quantity:
                    new_items.append(InvoiceItem(
                        invoice=self.object,
                        ware=ware,
                        price=price,
                        quantity=quantity))
            try:
                with transaction.atomic():
                    InvoiceItem.objects.filter(invoice=self.object).delete()
                    InvoiceItem.objects.bulk_create(new_items)
                    self.object.calculate_total_value()
            except IntegrityError:
                return self.render_to_response(self.get_context_data(form=form))
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self, **kwargs):
        return reverse("warehouse:invoice_detail", kwargs={'pk': self.object.pk})


class InvoiceUpdateView(InvoiceFormMixin, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja faktury zakupowej"
        return context


class InvoiceCreateView(InvoiceFormMixin, CreateView):
    model = Invoice
    form_class = InvoiceModelForm
    template_name = 'warehouse/invoice/invoice_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowa faktura zakupowa"
        return context


class SupplierTableView(FilteredSingleTableView):
    model = Supplier
    table_class = SupplierTable
    filter_class = SupplierFilter
    template_name = 'warehouse/supplier/supplier_table.html'


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'warehouse/supplier/supplier_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierDetailView, self).get_context_data(**kwargs)
        table = InvoiceTable(Invoice.objects.filter(supplier=context['supplier']))
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
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


class WareNameAutocomplete(autocomplete.Select2ListView):
    def get_list(self):
        return list(Ware.objects.values_list('name', flat=True).distinct())

    def create(self, text):
        return text


class SupplierAutocomplete(CustomSelect2QuerySetView):
    def get_queryset(self):
        qs = Supplier.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
