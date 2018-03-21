from weasyprint import HTML, CSS
from django_tables2 import RequestConfig

from django.views.generic import DetailView, UpdateView, CreateView, View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template.loader import get_template
from django.urls import reverse
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.forms import modelformset_factory

from KlimaKar.views import AjaxCreateView, CustomSelect2QuerySetView, FilteredSingleTableView
from apps.invoicing.models import SaleInvoice, Contractor, RefrigerantWeights, SaleInvoiceItem, ServiceTemplate
from apps.invoicing.forms import SaleInvoiceModelForm, ContractorModelForm, SaleInvoiceItemModelForm,\
    ServiceTemplateModelForm
from apps.invoicing.tables import SaleInvoiceTable, ContractorTable, SaleInvoiceItemTable, ServiceTemplateTable
from apps.invoicing.filters import SaleInvoiceFilter, ContractorFilter, ServiceTemplateFilter
from apps.invoicing.dictionaries import INVOICE_TYPES
from apps.invoicing.functions import get_next_invoice_number
from apps.invoicing.gus import gus_session


class SaleInvoiceTableView(FilteredSingleTableView):
    model = SaleInvoice
    table_class = SaleInvoiceTable
    filter_class = SaleInvoiceFilter
    template_name = 'invoicing/sale_invoice/table.html'


class SaleInvoiceDetailView(DetailView):
    model = SaleInvoice
    template_name = 'invoicing/sale_invoice/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = SaleInvoiceItemTable(SaleInvoiceItem.objects.filter(sale_invoice=context['saleinvoice']))
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        return context


class SaleInvoiceFormMixin():
    model = SaleInvoice
    form_class = SaleInvoiceModelForm
    template_name = 'invoicing/sale_invoice/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        RefrigerantWeightsFormSet = modelformset_factory(
            RefrigerantWeights, exclude=('sale_invoice',), max_num=1, min_num=1)
        SaleInvoiceItemFormSet = modelformset_factory(
            SaleInvoiceItem, form=SaleInvoiceItemModelForm, extra=10, can_delete=True)
        item_data = []
        refrigerant_data = []
        if self.object:
            items = SaleInvoiceItem.objects.filter(sale_invoice=self.object)
            item_data = [{'ware': i.ware, 'quantity': i.quantity, 'name': i.name,
                          'description': i.description, 'price_netto': i.price_netto,
                          'price_brutto': i.price_brutto} for i in items]
            r = self.object.refrigerantweights
            refrigerant_data = [{'r134a': r.r134a, 'r1234yf': r.r1234yf, 'r12': r.r12, 'r404': r.r404}]
        if self.request.POST:
            refrigerant_formset = RefrigerantWeightsFormSet(
                self.request.POST, queryset=RefrigerantWeights.objects.none(), prefix='refrigerant')
            item_formset = SaleInvoiceItemFormSet(
                self.request.POST, queryset=SaleInvoiceItem.objects.none(), prefix='item')
        else:
            refrigerant_formset = RefrigerantWeightsFormSet(
                initial=refrigerant_data, queryset=RefrigerantWeights.objects.none(), prefix='refrigerant')
            item_formset = SaleInvoiceItemFormSet(
                initial=item_data, queryset=SaleInvoiceItem.objects.none(), prefix='item')
        context['refrigerant_formset'] = refrigerant_formset
        context['item_formset'] = item_formset
        context['title'] = "Nowa faktura sprzedażowa"
        return context

    def form_valid(self, form):
        ctx = self.get_context_data()
        refrigerant_form = ctx['refrigerant_formset'][0]
        item_formset = ctx['item_formset']
        generate_pdf = 'generate_pdf' in form.data

        if form.is_valid() and refrigerant_form.is_valid() and item_formset.is_valid():
            self.object = form.save(commit=False)
            number_data = self.object.number.split('/')
            self.object.number_value = number_data[0]
            self.object.number_year = number_data[1]
            self.object.save()

            if hasattr(self.object, 'refrigerantweights'):
                self.object.refrigerantweights.delete()
            refrigerant_obj = refrigerant_form.save(commit=False)
            refrigerant_obj.sale_invoice = self.object
            refrigerant_obj.save()

            new_items = []
            for item_form in item_formset:
                if item_form.cleaned_data.get('DELETE', True):
                    continue
                name = item_form.cleaned_data.get('name')
                description = item_form.cleaned_data.get('description')
                ware = item_form.cleaned_data.get('ware')
                price_netto = item_form.cleaned_data.get('price_netto')
                price_brutto = item_form.cleaned_data.get('price_brutto')
                quantity = item_form.cleaned_data.get('quantity')

                if name:
                    new_items.append(SaleInvoiceItem(
                        sale_invoice=self.object,
                        name=name,
                        description=description,
                        ware=ware,
                        price_netto=price_netto,
                        price_brutto=price_brutto,
                        quantity=quantity))
            try:
                with transaction.atomic():
                    SaleInvoiceItem.objects.filter(sale_invoice=self.object).delete()
                    SaleInvoiceItem.objects.bulk_create(new_items)
            except IntegrityError:
                return self.render_to_response(self.get_context_data(form=form))
            return HttpResponseRedirect(self.get_success_url(pdf=generate_pdf))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self, **kwargs):
        if kwargs.get('pdf'):
            return reverse("invoicing:sale_invoice_detail", kwargs={'pk': self.object.pk}) + "?pdf"
        else:
            return reverse("invoicing:sale_invoice_detail", kwargs={'pk': self.object.pk})


class SaleInvoiceCreateView(SaleInvoiceFormMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowa faktura sprzedażowa ({})".format(dict(INVOICE_TYPES)[self.initial['invoice_type']])
        return context

    def dispatch(self, *args, **kwargs):
        invoice_type = kwargs.get('type')
        if invoice_type and invoice_type in dict(INVOICE_TYPES):
            self.initial = {
                'invoice_type': invoice_type,
                'number': get_next_invoice_number(invoice_type)
            }
        else:
            raise Http404()
        return super().dispatch(*args, **kwargs)


class SaleInvoiceUpdateView(SaleInvoiceFormMixin, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja faktury sprzedażowej ({})".format(self.get_object().get_invoice_type_display())
        return context


class SaleInvoicePDFView(View):
    print_version = False

    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(SaleInvoice, pk=kwargs.get('pk'))
        context = {
                'invoice': invoice
        }
        template = get_template('invoicing/invoice.html')
        rendered_tpl = template.render(context).encode()
        documents = []
        documents.append(
            HTML(string=rendered_tpl).render(stylesheets=[CSS(filename='KlimaKar/static/css/invoice.css')]))
        if self.print_version:
            documents.append(
                HTML(string=rendered_tpl).render(stylesheets=[CSS(filename='KlimaKar/static/css/invoice.css')]))
        all_pages = []
        for doc in documents:
            for p in doc.pages:
                all_pages.append(p)
        pdf_file = documents[0].copy(all_pages).write_pdf()
        response = HttpResponse(content_type='application/pdf')
        response.write(pdf_file)
        response['Content-Disposition'] = 'filename={} {}.pdf'.format(
            invoice.get_invoice_type_display(), invoice.number.replace('/', '_'))
        if not self.print_version:
            response['Content-Disposition'] = 'attachment;' + response['Content-Disposition']
        return response


class ServiceTemplateTableView(FilteredSingleTableView):
    model = ServiceTemplate
    table_class = ServiceTemplateTable
    filter_class = ServiceTemplateFilter
    template_name = 'invoicing/service_template/table.html'


class ServiceTemplateDetailView(DetailView):
    model = ServiceTemplate
    template_name = 'invoicing/service_template/detail.html'


class ServiceTemplateCreateView(CreateView):
    model = ServiceTemplate
    form_class = ServiceTemplateModelForm
    template_name = 'invoicing/service_template/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowa usługa"
        return context

    def get_success_url(self, **kwargs):
        return reverse("invoicing:service_template_detail", kwargs={'pk': self.object.pk})


class ServiceTemplateUpdateView(UpdateView):
    model = ServiceTemplate
    form_class = ServiceTemplateModelForm
    template_name = 'invoicing/service_template/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja usługi"
        return context

    def get_success_url(self, **kwargs):
        return reverse("invoicing:service_template_detail", kwargs={'pk': self.object.pk})


class ServiceTemplateAutocomplete(CustomSelect2QuerySetView):
    def get_queryset(self):
        qs = ServiceTemplate.objects.all()
        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(description__icontains=self.q))
        return qs


class ServiceTemplateGetDataView(View):
    def get(self, *args, **kwargs):
        service_pk = self.request.GET.get('pk', None)
        if service_pk:
            service = ServiceTemplate.objects.get(pk=service_pk)
            response = {
                'name': service.name,
                'description': service.description,
                'ware': None,
                'quantity': service.quantity,
                'price_netto': service.price_netto,
                'price_brutto': service.price_brutto
            }
            if service.ware:
                response['ware'] = {
                    'pk': service.ware.pk,
                    'index': service.ware.index,
                }
            return JsonResponse({'status': 'ok',
                                 'service': response})
        return JsonResponse({'status': 'error', 'service': []})


class ContractorTableView(FilteredSingleTableView):
    model = Contractor
    table_class = ContractorTable
    filter_class = ContractorFilter
    template_name = 'invoicing/contractor/table.html'


class ContractorDetailView(DetailView):
    model = Contractor
    template_name = 'invoicing/contractor/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = SaleInvoiceTable(SaleInvoice.objects.filter(contractor=context['contractor']))
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        return context


class ContractorCreateView(CreateView):
    model = Contractor
    form_class = ContractorModelForm
    template_name = 'invoicing/contractor/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowy kontrahent"
        return context

    def get_success_url(self, **kwargs):
        return reverse("invoicing:contractor_detail", kwargs={'pk': self.object.pk})


class ContractorUpdateView(UpdateView):
    model = Contractor
    form_class = ContractorModelForm
    template_name = 'invoicing/contractor/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja kontrahenta"
        return context

    def get_success_url(self, **kwargs):
        return reverse("invoicing:contractor_detail", kwargs={'pk': self.object.pk})


class ContractorCreateAjaxView(AjaxCreateView):
    model = Contractor
    form_class = ContractorModelForm
    title = "Nowy kontrahent"
    url = 'invoicing:contractor_create_ajax'


class ContractorAutocomplete(CustomSelect2QuerySetView):
    def get_queryset(self):
        qs = Contractor.objects.all()
        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(nip__icontains=self.q))
        return qs


class ContractorGUS(View):
    def get(self, request, *args, **kwargs):
        nip = request.GET.get('nip')
        if len(str(nip)) != 10:
            return JsonResponse({}, status=400)
        response_data = gus_session.get_address(nip=nip)
        if not response_data:
            return JsonResponse({}, status=404)
        return JsonResponse(response_data)
