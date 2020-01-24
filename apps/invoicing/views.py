import datetime
import requests

from urllib.parse import urlencode
from django_tables2.export.views import ExportMixin
from smtplib import SMTPRecipientsRefused
from extra_views import CreateWithInlinesView, UpdateWithInlinesView
from zeep import Client as ZeepClient

from django.views.generic import DetailView, UpdateView, CreateView, View
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.template import Template, Context
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages

from KlimaKar.email import get_email_message
from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from KlimaKar.mixins import AjaxFormMixin, GroupAccessControlMixin, SingleTableAjaxMixin, MultiTableAjaxMixin
from KlimaKar.templatetags.slugify import slugify
from apps.invoicing.models import SaleInvoice, Contractor, SaleInvoiceItem, ServiceTemplate, CorrectiveSaleInvoice
from apps.invoicing.forms import SaleInvoiceModelForm, ContractorModelForm, SaleInvoiceItemsInline,\
    ServiceTemplateModelForm, EmailForm, RefrigerantWeightsInline, CorrectiveSaleInvoiceModelForm
from apps.invoicing.tables import SaleInvoiceTable, ContractorTable, SaleInvoiceItemTable, ServiceTemplateTable
from apps.invoicing.filters import SaleInvoiceFilter, ContractorFilter, ServiceTemplateFilter
from apps.invoicing.functions import get_next_invoice_number, generate_refrigerant_weights_report
from apps.invoicing.gus import GUS
from apps.settings.models import SiteSettings
from apps.commission.models import Commission
from apps.commission.tables import CommissionTable


class SaleInvoiceTableView(ExportMixin, FilteredSingleTableView):
    model = SaleInvoice
    table_class = SaleInvoiceTable
    filter_class = SaleInvoiceFilter
    template_name = 'invoicing/sale_invoice/table.html'
    export_name = 'Zakupy sprzedazowe'
    tab_filter = 'invoice_type'
    tab_filter_default = SaleInvoice.TYPE_VAT
    tab_filter_choices = SaleInvoice.INVOICE_TYPES


class SaleInvoiceDetailView(SingleTableAjaxMixin, DetailView):
    model = SaleInvoice
    template_name = 'invoicing/sale_invoice/detail.html'
    table_class = SaleInvoiceItemTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = SiteSettings.load()
        subject = ''
        if site_settings.SALE_INVOICE_EMAIL_TITLE:
            subject = Template(site_settings.SALE_INVOICE_EMAIL_TITLE).render(Context({'invoice': self.object}))
        message = ''
        if site_settings.SALE_INVOICE_EMAIL_BODY:
            message = Template(site_settings.SALE_INVOICE_EMAIL_BODY).render(Context({'invoice': self.object}))
        email_data = {
            'sale_invoice': self.object,
            'subject': subject,
            'message': message,
            'recipient': self.object.contractor.email
        }
        context['email_form'] = EmailForm(initial=email_data)
        context['email_url'] = reverse('invoicing:sale_invoice_email')
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('invoicing:sale_invoices') + '?' + urlencode(self.request.session.get(key, ''))
        return context

    def get_table_data(self):
        return SaleInvoiceItem.objects.filter(sale_invoice=self.object)


class SaleInvoiceCreateView(CreateWithInlinesView):
    model = SaleInvoice
    form_class = SaleInvoiceModelForm
    inlines = [SaleInvoiceItemsInline, RefrigerantWeightsInline]
    template_name = 'invoicing/sale_invoice/form.html'
    invoice_type = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowa faktura sprzedażowa ({})".format(
            dict(SaleInvoice.INVOICE_TYPES)[self.invoice_type])
        return context

    def get_initial(self):
        initial = dict()
        initial['invoice_type'] = self.invoice_type
        initial['number'] = get_next_invoice_number(self.invoice_type)
        site_settings = SiteSettings.load()
        initial['tax_percent'] = site_settings.SALE_INVOICE_TAX_PERCENT
        if self.invoice_type in [SaleInvoice.TYPE_WDT, SaleInvoice.TYPE_WDT_PRO_FORMA]:
            initial['tax_percent'] = site_settings.SALE_INVOICE_TAX_PERCENT_WDT
        return initial

    def dispatch(self, *args, **kwargs):
        for invoice_type in SaleInvoice.INVOICE_TYPES:
            if slugify(invoice_type[1]) == kwargs.get('type'):
                self.invoice_type = invoice_type[0]
                break

        if not self.invoice_type or self.invoice_type not in dict(SaleInvoice.INVOICE_TYPES):
            raise Http404()
        return super().dispatch(*args, **kwargs)

    def forms_valid(self, form, inlines):
        self.generate_pdf = 'generate_pdf' in form.data
        if self.invoice_type != SaleInvoice.TYPE_CORRECTIVE:
            messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejną fakturę.</a>'.format(
                reverse('invoicing:sale_invoice_create', kwargs={
                    'type': slugify(dict(SaleInvoice.INVOICE_TYPES)[self.invoice_type])
                })))
        else:
            messages.add_message(self.request, messages.SUCCESS, 'Zapisano fakturę.')
        return super().forms_valid(form, inlines)

    def get_success_url(self, **kwargs):
        if self.generate_pdf:
            return reverse("invoicing:sale_invoice_detail", kwargs={
                'pk': self.object.pk,
                'slug': slugify(self.object)
            }) + "?pdf"
        else:
            return reverse("invoicing:sale_invoice_detail", kwargs={
                'pk': self.object.pk,
                'slug': slugify(self.object)
            })


class SaleInvoiceCommissionCreateView(SaleInvoiceCreateView):

    def dispatch(self, *args, **kwargs):
        try:
            self.commission = Commission.objects.get(pk=kwargs.get('pk'))
            self.desc = self.request.GET.get('desc', '')
            self.kwargs['value_type'] = self.request.GET.get('value_type')
            self.kwargs['commission'] = self.commission
        except Commission.DoesNotExist:
            raise Http404()
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['contractor'] = self.commission.contractor
        initial['comment'] = self.desc
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowa faktura sprzedażowa ({}) dla zlecenia {}".format(
            dict(SaleInvoice.INVOICE_TYPES)[self.invoice_type], str(self.commission.pk))
        return context

    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)
        self.commission.sale_invoices.add(self.object)
        if not self.commission.contractor:
            self.commission.contractor = self.object.contractor
            self.commission.save()
        return response


class SaleInvoiceUpdateView(UpdateWithInlinesView):
    model = SaleInvoice
    form_class = SaleInvoiceModelForm
    inlines = [SaleInvoiceItemsInline, RefrigerantWeightsInline]
    template_name = 'invoicing/sale_invoice/form.html'

    def dispatch(self, *args, **kwargs):
        dispatch = super().dispatch(*args, **kwargs)
        if self.model == SaleInvoice and self.object.invoice_type == SaleInvoice.TYPE_CORRECTIVE:
            return redirect('invoicing:sale_invoice_update_corrective', **kwargs)
        return dispatch

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja faktury sprzedażowej ({})".format(self.get_object().get_invoice_type_display())
        return context

    def forms_valid(self, form, inlines):
        self.generate_pdf = 'generate_pdf' in form.data
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().forms_valid(form, inlines)

    def get_success_url(self, **kwargs):
        if self.generate_pdf:
            return reverse("invoicing:sale_invoice_detail", kwargs={
                'pk': self.object.pk,
                'slug': slugify(self.object)
            }) + "?pdf"
        else:
            return reverse("invoicing:sale_invoice_detail", kwargs={
                'pk': self.object.pk,
                'slug': slugify(self.object)
            })


class CorrectiveSaleInvoiceCreateView(SaleInvoiceCreateView):
    model = CorrectiveSaleInvoice
    form_class = CorrectiveSaleInvoiceModelForm
    inlines = [SaleInvoiceItemsInline, RefrigerantWeightsInline]
    template_name = 'invoicing/sale_invoice/corrective_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['title'].replace(')', ' do faktury {})'.format(self.original_invoice))
        context['original_invoice'] = self.original_invoice
        return context

    def dispatch(self, *args, **kwargs):
        kwargs['type'] = SaleInvoice.TYPE_CORRECTIVE
        self.invoice_type = SaleInvoice.TYPE_CORRECTIVE
        self.original_invoice = SaleInvoice.objects.get(pk=kwargs.get('pk'))
        self.kwargs['original_invoice'] = self.original_invoice
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = model_to_dict(self.original_invoice)
        initial.pop('issue_date', None)
        initial.pop('payment_date', None)
        initial['original_invoice'] = self.original_invoice
        initial['invoice_type'] = self.invoice_type
        initial['number'] = get_next_invoice_number(self.invoice_type)
        return initial


class CorrectiveSaleInvoiceUpdateView(SaleInvoiceUpdateView):
    model = CorrectiveSaleInvoice
    form_class = CorrectiveSaleInvoiceModelForm
    inlines = [SaleInvoiceItemsInline, RefrigerantWeightsInline]
    template_name = 'invoicing/sale_invoice/corrective_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['title'].replace(')', ' do faktury {})'.format(self.invoice.original_invoice))
        context['original_invoice'] = self.invoice.original_invoice
        return context

    def dispatch(self, *args, **kwargs):
        self.invoice = CorrectiveSaleInvoice.objects.get(pk=kwargs.get('pk'))
        self.kwargs['original_invoice'] = self.invoice.original_invoice
        return super().dispatch(*args, **kwargs)


class SaleInvoiceAutocomplete(CustomSelect2QuerySetView):
    def get_queryset(self):
        invoices = SaleInvoice.objects.all().order_by('-number_year', '-number_value')
        qs = invoices
        if self.q:
            qs = invoices.filter(number__iexact=self.q)
            if qs.count() < 1:
                qs = invoices.filter(number__icontains=self.q)
        return qs


class SaleInvoicePDFView(View):
    print_version = False

    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(SaleInvoice, pk=kwargs.get('pk'))
        pdf_file = invoice.generate_pdf(self.print_version)
        response = HttpResponse(content_type='application/pdf')
        response.write(pdf_file)
        response['Content-Disposition'] = 'filename="{} {}.pdf"'.format(
            invoice.get_invoice_type_display(), invoice.number.replace('/', '_'))
        response['Content-Encoding'] = None
        response['Content-Type'] = 'application/pdf'
        if not self.print_version:
            response['Content-Disposition'] = 'attachment;' + response['Content-Disposition']
        return response


class SendEmailView(View):
    def post(self, request, *args, **kwargs):
        invoice = get_object_or_404(SaleInvoice, pk=request.POST.get('sale_invoice'))
        pdf_file = invoice.generate_pdf()
        email = get_email_message(
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
        except Exception:
            result = 0
        if result == 1:
            return JsonResponse({'status': 'success', 'message': 'Wiadomość została wysłana'}, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Bład przy wysyłaniu wiadomości. Sprawdź konfigurację serwera e-mail.'}, status=500)


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

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejną usługę.</a>'.format(
                reverse('invoicing:service_template_create')))
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("invoicing:service_template_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)
        })


class ServiceTemplateUpdateView(UpdateView):
    model = ServiceTemplate
    form_class = ServiceTemplateModelForm
    template_name = 'invoicing/service_template/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja usługi"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("invoicing:service_template_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)
        })


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


class ContractorDetailView(MultiTableAjaxMixin, DetailView):
    SALE_INVOIDE_ID = 'sale_invoice'
    COMMISSION_ID = 'commission'

    model = Contractor
    template_name = 'invoicing/contractor/detail.html'
    table_classes = {
        'sale_invoice': SaleInvoiceTable,
        'commission': CommissionTable
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('invoicing:contractors') + '?' + urlencode(self.request.session.get(key, ''))
        return context

    def get_tables_data(self):
        return {
            self.SALE_INVOIDE_ID: SaleInvoice.objects.filter(contractor=self.get_object()),
            self.COMMISSION_ID: Commission.objects.filter(contractor=self.get_object())
        }


class ContractorCreateView(CreateView):
    model = Contractor
    form_class = ContractorModelForm
    template_name = 'invoicing/contractor/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowy kontrahent"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejnego kontrahenta.</a>'.format(
                reverse('invoicing:contractor_create')))
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("invoicing:contractor_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)
        })


class ContractorUpdateView(UpdateView):
    model = Contractor
    form_class = ContractorModelForm
    template_name = 'invoicing/contractor/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja kontrahenta"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("invoicing:contractor_detail", kwargs={
            'pk': self.object.pk,
            'slug': slugify(self.object)
        })


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
            qs = qs.filter(Q(name__icontains=self.q) | Q(nip__icontains=self.q) |
                           Q(phone_1__icontains=self.q) | Q(phone_2__icontains=self.q))
        return qs


class ContractorGUS(View):
    def get(self, request, *args, **kwargs):
        nip = request.GET.get('nip')
        request_type = request.GET.get('type', 'address')
        if len(str(nip)) != 10:
            return JsonResponse({}, status=400)
        response_data = None
        if request_type == 'address':
            response_data = GUS.get_gus_address(nip)
        elif request_type == 'pkd':
            response_data = {'pkd': sorted(GUS.get_gus_pkd(nip), key=lambda k: k['main'], reverse=True)}
        elif request_type == 'all':
            response_data = {'pkd': sorted(GUS.get_gus_pkd(nip), key=lambda k: k['main'], reverse=True),
                             'info': GUS.get_gus_data(nip)}
        if not response_data:
            return JsonResponse({}, status=404)
        return JsonResponse(response_data)


class ContractorGetDataView(View):
    def get(self, *args, **kwargs):
        contractor_pk = self.request.GET.get('pk', None)
        validate_vat = self.request.GET.get('validate_vat', False)
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
                'email': contractor.email,
                'phone': contractor.phone_1 or contractor.phone_2 or None,
                'vat_valid': None
            }
            if validate_vat:
                response.update(self._validate_vat(contractor))
            return JsonResponse({'status': 'success',
                                 'contractor': response})
        return JsonResponse({'status': 'error', 'contractor': {}})

    def _validate_vat(self, contractor):
        try:
            if contractor.nip:
                if contractor.nip_prefix:
                    return self._check_ue_vat(contractor)
                else:
                    return self._check_polish_vat(contractor)
        except Exception:
            return {'vat_valid': 'failed'}
        return {}

    def _check_polish_vat(self, contractor):
        url = 'https://wl-api.mf.gov.pl/api/search/nip/{}?date={}'.format(
                        contractor.nip, str(datetime.date.today()))
        r = requests.get(url)
        vat_subject = r.json().get('result', {}).get('subject', {})
        if vat_subject is None:
            vat_valid = False
        else:
            vat_valid = vat_subject.get('statusVat', False)
        return {
            'vat_valid': vat_valid == 'Czynny',
            'vat_url': 'https://www.podatki.gov.pl/wykaz-podatnikow-vat-wyszukiwarka'
        }

    def _check_ue_vat(self, contractor):
        client = ZeepClient('http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl')
        vat = client.service.checkVat(contractor.nip_prefix, contractor.nip)
        return {
            'vat_valid': vat['valid'],
            'vat_url': 'http://ec.europa.eu/taxation_customs/vies/?locale=pl'
        }


class SaleInvoiceSetPayed(GroupAccessControlMixin, View):
    allowed_groups = ['boss']

    def get(self, *args, **kwargs):
        invoice = SaleInvoice.objects.get(pk=kwargs.get('pk'))
        invoice.payed = True
        invoice.save()
        return JsonResponse({'status': 'success'})
