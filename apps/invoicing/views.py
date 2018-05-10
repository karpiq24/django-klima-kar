from urllib.parse import urlencode
from django_tables2 import RequestConfig
from django_tables2.export.views import ExportMixin
from smtplib import SMTPRecipientsRefused
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from django.views.generic import DetailView, UpdateView, CreateView, View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.template.loader import get_template
from django.urls import reverse
from django.db.models import Q
from django.core.mail import EmailMessage

from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from KlimaKar.mixins import AjaxFormMixin
from apps.invoicing.models import SaleInvoice, Contractor, SaleInvoiceItem, ServiceTemplate
from apps.invoicing.forms import SaleInvoiceModelForm, ContractorModelForm, SaleInvoiceItemsInline,\
    ServiceTemplateModelForm, EmailForm, RefrigerantWeightsInline
from apps.invoicing.tables import SaleInvoiceTable, ContractorTable, SaleInvoiceItemTable, ServiceTemplateTable
from apps.invoicing.filters import SaleInvoiceFilter, ContractorFilter, ServiceTemplateFilter
from apps.invoicing.dictionaries import INVOICE_TYPES
from apps.invoicing.functions import get_next_invoice_number, generate_refrigerant_weights_report
from apps.invoicing.gus import get_gus_address


class SaleInvoiceTableView(ExportMixin, FilteredSingleTableView):
    model = SaleInvoice
    table_class = SaleInvoiceTable
    filter_class = SaleInvoiceFilter
    template_name = 'invoicing/sale_invoice/table.html'
    export_name = 'Zakupy sprzedazowe'


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


class SaleInvoiceCreateView(CreateWithInlinesView):
    model = SaleInvoice
    form_class = SaleInvoiceModelForm
    inlines = [SaleInvoiceItemsInline, RefrigerantWeightsInline]
    template_name = 'invoicing/sale_invoice/form.html'

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

    def forms_valid(self, form, inlines):
        self.generate_pdf = 'generate_pdf' in form.data
        return super().forms_valid(form, inlines)

    def get_success_url(self, **kwargs):
        if self.generate_pdf:
            return reverse("invoicing:sale_invoice_detail", kwargs={'pk': self.object.pk}) + "?pdf"
        else:
            return reverse("invoicing:sale_invoice_detail", kwargs={'pk': self.object.pk})


class SaleInvoiceUpdateView(UpdateWithInlinesView):
    model = SaleInvoice
    form_class = SaleInvoiceModelForm
    inlines = [SaleInvoiceItemsInline, RefrigerantWeightsInline]
    template_name = 'invoicing/sale_invoice/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja faktury sprzedażowej ({})".format(self.get_object().get_invoice_type_display())
        return context

    def forms_valid(self, form, inlines):
        self.generate_pdf = 'generate_pdf' in form.data
        return super().forms_valid(form, inlines)

    def get_success_url(self, **kwargs):
        if self.generate_pdf:
            return reverse("invoicing:sale_invoice_detail", kwargs={'pk': self.object.pk}) + "?pdf"
        else:
            return reverse("invoicing:sale_invoice_detail", kwargs={'pk': self.object.pk})


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
        response['Content-Disposition'] = "attachment; filename=Sprzedaz_czynnika.xlsx"
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


class ContractorTableView(ExportMixin, FilteredSingleTableView):
    model = Contractor
    table_class = ContractorTable
    filter_class = ContractorFilter
    template_name = 'invoicing/contractor/table.html'
    export_name = 'Kontrahenci'


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
        response_data = get_gus_address(nip)
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
