from django.urls import reverse
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import DetailView, UpdateView, CreateView, View
from django.db.models import Q

from django_tables2 import SingleTableView
from django_tables2 import RequestConfig
from dal import autocomplete

from apps.warehouse.models import Ware, Invoice, Supplier, InvoiceItem
from apps.warehouse.tables import WareTable, InvoiceTable, SupplierTable, InvoiceItemTable
from apps.warehouse.filters import WareFilter, InvoiceFilter, SupplierFilter
from apps.warehouse.forms import (
    WareModelForm, InvoiceModelForm, SupplierModelForm, InvoiceItemModelForm)


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


class WareTableView(FilteredSingleTableView):
    model = Ware
    table_class = WareTable
    filter_class = WareFilter
    template_name = 'warehouse/ware/ware_table.html'


class WareUpdateView(UpdateView):
    model = Ware
    form_class = WareModelForm
    template_name = 'warehouse/ware/ware_form.html'

    def get_context_data(self, **kwargs):
        context = super(WareUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Edycja towaru"
        return context

    def get_success_url(self, **kwargs):
        return reverse("warehouse:ware_detail", kwargs={'pk': self.kwargs['pk']})


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
        invoices = [x.invoice for x in InvoiceItem.objects.filter(ware=context['ware'])]
        table = InvoiceTable(invoices)
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


class InvoiceUpdateView(UpdateView):
    model = Invoice
    form_class = InvoiceModelForm
    template_name = 'warehouse/invoice/invoice_form.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceUpdateView, self).get_context_data(**kwargs)
        InvoiceItemFormSet = formset_factory(InvoiceItemModelForm, extra=10, can_delete=True)
        items = InvoiceItem.objects.filter(invoice=self.object)
        item_data = [{'ware': i.ware, 'quantity': i.quantity, 'price': i.price} for i in items]
        if self.request.POST:
            item_formset = InvoiceItemFormSet(self.request.POST)
        else:
            item_formset = InvoiceItemFormSet(initial=item_data)
        context['item_formset'] = item_formset
        context['title'] = "Edycja faktury"
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
        return reverse("warehouse:invoice_detail", kwargs={'pk': self.kwargs['pk']})


class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceModelForm
    template_name = 'warehouse/invoice/invoice_form.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        InvoiceItemFormSet = formset_factory(InvoiceItemModelForm, extra=10)

        if self.request.POST:
            item_formset = InvoiceItemFormSet(self.request.POST)
        else:
            item_formset = InvoiceItemFormSet()
        context['item_formset'] = item_formset
        context['title'] = "Nowa faktura"
        return context

    def form_valid(self, form):
        ctx = self.get_context_data()
        item_formset = ctx['item_formset']

        if form.is_valid() and item_formset.is_valid():
            self.object = form.save()
            new_items = []
            for item_form in item_formset:
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
        return reverse("warehouse:supplier_detail", kwargs={'pk': self.kwargs['pk']})


class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierModelForm
    template_name = 'warehouse/supplier/supplier_form.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierCreateView, self).get_context_data(**kwargs)
        context['title'] = "Nowy dostawca"
        return context

    def get_success_url(self, **kwargs):
        return reverse("warehouse:suppliers_detail", kwargs={'pk': self.object.pk})


class GetWareData(View):
    def get(self, *args, **kwargs):
        ware_index = self.request.GET.get('index', None)
        if ware_index:
            ware = Ware.objects.get(index=ware_index)
            response = {
                'name': ware.name,
                'last_price': ware.last_price
            }
            return JsonResponse({'status': 'ok',
                                 'ware': response})
        return JsonResponse({'status': 'error', 'ware': []})


class WareAutocomplete(autocomplete.Select2QuerySetView):
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


class SupplierAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Supplier.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
