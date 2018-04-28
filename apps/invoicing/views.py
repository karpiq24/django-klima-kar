from urllib.parse import urlencode
from django_tables2 import RequestConfig
from smtplib import SMTPRecipientsRefused

from django.views.generic import DetailView, UpdateView, CreateView, View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template.loader import get_template
from django.urls import reverse
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.forms import modelformset_factory
from django.core.mail import EmailMessage

from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from KlimaKar.mixins import AjaxFormMixin
from apps.invoicing.models import SaleInvoice, Contractor, RefrigerantWeights, SaleInvoiceItem, ServiceTemplate
from apps.invoicing.forms import SaleInvoiceModelForm, ContractorModelForm, SaleInvoiceItemModelForm,\
    ServiceTemplateModelForm, EmailForm
from apps.invoicing.tables import SaleInvoiceTable, ContractorTable, SaleInvoiceItemTable, ServiceTemplateTable
from apps.invoicing.filters import SaleInvoiceFilter, ContractorFilter, ServiceTemplateFilter
from apps.invoicing.dictionaries import INVOICE_TYPES
from apps.invoicing.functions import get_next_invoice_number, generate_refrigerant_weights_report
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
        email_data = {
            'sale_invoice': self.object,
            'subject': '{} {}'.format(self.object.get_invoice_type_display(), self.object.number),
            'message': get_template('invoicing/sale_invoice/email_template.txt').render(),
            'recipient': self.object.contractor.email
        }
        context['email_form'] = EmailForm(initial=email_data)
        context['email_url'] = reverse('invoicing:sale_invoice_email')
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('invoicing:sale_invoices') + '?' + urlencode(self.request.session.get(key, ''))
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
            if invoice_type == '4':
                self.initial['tax_percent'] = 0
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
        pdf_file = invoice.generate_pdf(self.print_version)
        response = HttpResponse(content_type='application/pdf')
        response.write(pdf_file)
        response['Content-Disposition'] = 'filename={} {}.pdf'.format(
            invoice.get_invoice_type_display(), invoice.number.replace('/', '_'))
        if not self.print_version:
            response['Content-Disposition'] = 'attachment;' + response['Content-Disposition']
        return response


class SendEmailView(View):
    def post(self, request, *args, **kwargs):
        invoice = get_object_or_404(SaleInvoice, pk=request.POST.get('sale_invoice'))
        pdf_file = invoice.generate_pdf()
        email = EmailMessage(
            subject=request.POST.get('subject'),
            body=request.POST.get('message'),
            to=[request.POST.get('recipient')]
        )
        email.attach('{} {}.pdf'.format(
            invoice.get_invoice_type_display(),
            invoice.number.replace('/', '_')),
            pdf_file, mimetype='application/pdf')
        try:
            result = email.send(fail_silently=False)
        except SMTPRecipientsRefused:
            return JsonResponse({'status': 'error', 'message': 'Podaj poprawny adres email'}, status=400)
        except IndexError:
            return JsonResponse({'status': 'error', 'message': 'Podaj poprawny temat wiadomości'}, status=400)
        if result == 1:
            return JsonResponse({'status': 'success', 'message': 'Wiadomość została wysłana'}, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Bład przy wysyłaniu wiadomości. Skontaktuj się z administratorem.'}, status=500)


class ExportRefrigerantWeights(View):
    def get(self, request, *args, **kwargs):
        key = "{}_params".format(SaleInvoice.__name__)
        queryset = SaleInvoiceFilter(request.session[key], queryset=SaleInvoice.objects.all()).qs
        output = generate_refrigerant_weights_report(queryset)
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=Sprzedaz czynnika.xlsx"
        return response


class ServiceTemplateTableView(FilteredSingleTableView):
    model = ServiceTemplate
    table_class = ServiceTemplateTable
    filter_class = ServiceTemplateFilter
    template_name = 'invoicing/service_template/table.html'


class ServiceTemplateDetailView(DetailView):
    model = ServiceTemplate
    template_name = 'invoicing/service_template/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse(
            'invoicing:service_templates') + '?' + urlencode(self.request.session.get(key, ''))
        return context


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
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('invoicing:contractors') + '?' + urlencode(self.request.session.get(key, ''))
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


class ContractorCreateAjaxView(AjaxFormMixin, CreateView):
    model = Contractor
    form_class = ContractorModelForm
    title = "Nowy kontrahent"


class ContractorUpdateAjaxView(AjaxFormMixin, UpdateView):
    model = Contractor
    form_class = ContractorModelForm
    title = "Edycja kontrahenta"


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


class ContractorGetDataView(View):
    def get(self, *args, **kwargs):
        contractor_pk = self.request.GET.get('pk', None)
        if contractor_pk:
            contractor = Contractor.objects.get(pk=contractor_pk)
            response = {
                'name': contractor.name,
                'nip': contractor.nip,
                'nip_prefix': contractor.nip_prefix,
                'address_1': contractor.address_1,
                'address_2': contractor.address_2,
                'city': contractor.city,
                'postal_code': contractor.postal_code,
                'email': contractor.email
            }
            return JsonResponse({'status': 'ok',
                                 'contractor': response})
        return JsonResponse({'status': 'error', 'contractor': {}})
