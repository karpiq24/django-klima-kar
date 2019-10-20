import subprocess
import datetime

from urllib.parse import urlencode
from smtplib import SMTPRecipientsRefused

from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.generic import DetailView, UpdateView, CreateView, View
from django.template import Template, Context
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import get_object_or_404

from django_tables2.export.views import ExportMixin
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from KlimaKar.email import get_email_message
from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from KlimaKar.mixins import AjaxFormMixin, SingleTableAjaxMixin
from KlimaKar.templatetags.slugify import slugify
from apps.settings.models import SiteSettings
from apps.commission.models import Vehicle, Component, Commission, CommissionItem
from apps.commission.tables import VehicleTable, ComponentTable, CommissionTable, CommissionItemTable
from apps.commission.filters import VehicleFilter, ComponentFilter, CommissionFilter
from apps.commission.forms import VehicleModelForm, ComponentModelForm, CommissionModelForm, CommissionItemInline, \
    CommissionEmailForm
from apps.invoicing.dictionaries import INVOICE_TYPES


class VehicleTableView(ExportMixin, FilteredSingleTableView):
    model = Vehicle
    table_class = VehicleTable
    filter_class = VehicleFilter
    template_name = 'commission/vehicle/table.html'
    export_name = 'Pojazdy'


class VehicleUpdateView(UpdateView):
    model = Vehicle
    form_class = VehicleModelForm
    template_name = 'commission/vehicle/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja pojazdu"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("commission:vehicle_detail", kwargs={
            'pk': self.object.pk,
            'brand': slugify(self.object.brand)})


class VehicleCreateView(CreateView):
    model = Vehicle
    form_class = VehicleModelForm
    template_name = 'commission/vehicle/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowy pojazd"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejny pojazd.</a>'.format(
                reverse('commission:vehicle_create')))
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("commission:vehicle_detail", kwargs={
            'pk': self.object.pk,
            'brand': slugify(self.object.brand)})


class VehicleDetailView(SingleTableAjaxMixin, DetailView):
    model = Vehicle
    template_name = 'commission/vehicle/detail.html'
    table_class = CommissionTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('commission:vehicles') + '?' + urlencode(self.request.session.get(key, ''))
        return context

    def get_table_data(self):
        return Commission.objects.filter(vehicle=self.object)


class VehicleAutocomplete(CustomSelect2QuerySetView):
    always_show_create = True
    create_empty_label = 'Nowy pojazd'

    def get_queryset(self):
        qs = Vehicle.objects.all()
        if self.q:
            qs = qs.filter(Q(brand__icontains=self.q) | Q(model__icontains=self.q) | Q(
                vin__icontains=self.q) | Q(registration_plate__icontains=self.q))
        return qs


class VehicleCreateAjaxView(AjaxFormMixin, CreateView):
    identifier = 2
    model = Vehicle
    form_class = VehicleModelForm
    title = "Nowy pojazd"


class VehicleUpdateAjaxView(AjaxFormMixin, UpdateView):
    identifier = 2
    model = Vehicle
    form_class = VehicleModelForm
    title = "Edycja pojazdu"


class ComponentTableView(ExportMixin, FilteredSingleTableView):
    model = Component
    table_class = ComponentTable
    filter_class = ComponentFilter
    template_name = 'commission/component/table.html'
    export_name = 'Podzespoły'


class ComponentUpdateView(UpdateView):
    model = Component
    form_class = ComponentModelForm
    template_name = 'commission/component/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja podzespołu"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("commission:component_detail", kwargs={
            'pk': self.object.pk,
            'type': slugify(self.object.get_component_type_display())})


class ComponentCreateView(CreateView):
    model = Component
    form_class = ComponentModelForm
    template_name = 'commission/component/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowy podzespół"
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejny podzespół.</a>'.format(
                reverse('commission:component_create')))
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("commission:component_detail", kwargs={
            'pk': self.object.pk,
            'type': slugify(self.object.get_component_type_display())})


class ComponentDetailView(SingleTableAjaxMixin, DetailView):
    model = Component
    template_name = 'commission/component/detail.html'
    table_class = CommissionTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('commission:components') + '?' + urlencode(self.request.session.get(key, ''))
        return context

    def get_table_data(self):
        return Commission.objects.filter(component=self.object)


class ComponentAutocomplete(CustomSelect2QuerySetView):
    always_show_create = True
    create_empty_label = 'Nowy pojazd'

    def get_queryset(self):
        qs = Component.objects.all()
        if self.q:
            qs = qs.filter(Q(model__icontains=self.q) | Q(
                serial_number__icontains=self.q) | Q(catalog_number__icontains=self.q))
        return qs


class ComponentCreateAjaxView(AjaxFormMixin, CreateView):
    identifier = 3
    model = Component
    form_class = ComponentModelForm
    title = "Nowy podzespół"


class ComponentUpdateAjaxView(AjaxFormMixin, UpdateView):
    identifier = 3
    model = Component
    form_class = ComponentModelForm
    title = "Edycja podzespołu"


class CommissionTableView(ExportMixin, FilteredSingleTableView):
    model = Commission
    table_class = CommissionTable
    filter_class = CommissionFilter
    template_name = 'commission/commission/table.html'
    export_name = 'Zlecenia'
    tab_filter = 'status'
    tab_filter_default = Commission.OPEN
    tab_filter_choices = Commission.STATUS_CHOICES


class CommissionDetailView(SingleTableAjaxMixin, DetailView):
    model = Commission
    template_name = 'commission/commission/detail.html'
    table_class = CommissionItemTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('commission:commissions') + '?' + urlencode(self.request.session.get(key, ''))
        types = dict(INVOICE_TYPES)
        types.pop('3')
        context['invoice_types'] = types

        site_settings = SiteSettings.load()
        subject = ''
        if site_settings.COMMISSION_EMAIL_TITLE:
            subject = Template(site_settings.COMMISSION_EMAIL_TITLE).render(Context({'commission': self.object}))
        message = ''
        if site_settings.COMMISSION_EMAIL_BODY:
            message = Template(site_settings.COMMISSION_EMAIL_BODY).render(Context({'commission': self.object}))
        email_data = {
            'commission': self.object,
            'subject': subject,
            'message': message,
            'recipient': self.object.contractor.email
        }
        context['email_form'] = CommissionEmailForm(initial=email_data)
        context['email_url'] = reverse('commission:commission_email')
        return context

    def get_table_data(self):
        return CommissionItem.objects.filter(commission=self.object)


class CommissionCreateView(CreateWithInlinesView):
    model = Commission
    form_class = CommissionModelForm
    inlines = [CommissionItemInline]
    template_name = 'commission/commission/form.html'
    commission_type = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nowe zlecenie ({})".format(
            dict(Commission.COMMISSION_TYPES)[self.commission_type])
        return context

    def get_initial(self):
        initial = dict()
        site_settings = SiteSettings.load()
        initial['tax_percent'] = site_settings.COMMISSION_TAX_PERCENT
        initial['commission_type'] = self.commission_type
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['commission_type'] = self.commission_type
        return kwargs

    def forms_valid(self, form, inlines):
        self.generate_pdf = 'generate_pdf' in form.data
        if self.commission_type is Commission.VEHICLE:
            url = 'commission:commission_create_vehicle'
        else:
            url = 'commission:commission_create_component'
        messages.add_message(self.request, messages.SUCCESS, '<a href="{}">Dodaj kolejne zlecenie.</a>'.format(
            reverse(url)))
        return super().forms_valid(form, inlines)

    def get_success_url(self, **kwargs):
        return '{}{}'.format(
            reverse("commission:commission_detail", kwargs={
                'pk': self.object.pk,
                'desc': slugify(str(self.object))
            }), '?pdf' if self.generate_pdf else '')


class CommissionUpdateView(UpdateWithInlinesView):
    model = Commission
    form_class = CommissionModelForm
    inlines = [CommissionItemInline]
    template_name = 'commission/commission/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edycja zlecenia ({})".format(str(self.get_object()))
        return context

    def forms_valid(self, form, inlines):
        self.generate_pdf = 'generate_pdf' in form.data
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        return super().forms_valid(form, inlines)

    def get_success_url(self, **kwargs):
        return '{}{}'.format(
            reverse("commission:commission_detail", kwargs={
                'pk': self.object.pk,
                'desc': slugify(str(self.object))
            }), '?pdf' if self.generate_pdf else '')


class CommissionPDFView(View):
    print_version = False

    def get(self, request, *args, **kwargs):
        commission = get_object_or_404(Commission, pk=kwargs.get('pk'))
        pdf_file = commission.generate_pdf(self.print_version)
        response = HttpResponse(content_type='application/pdf')
        response.write(pdf_file)
        response['Content-Disposition'] = 'filename="Zlecenie {}.pdf"'.format(commission.pk)
        response['Content-Encoding'] = None
        response['Content-Type'] = 'application/pdf'
        if not self.print_version:
            response['Content-Disposition'] = 'attachment;' + response['Content-Disposition']
        return response


class CommissionSendEmailView(View):
    def post(self, request, *args, **kwargs):
        commission = get_object_or_404(Commission, pk=request.POST.get('commission'))
        pdf_file = commission.generate_pdf()
        email = get_email_message(
            subject=request.POST.get('subject'),
            body=request.POST.get('message'),
            to=[request.POST.get('recipient')]
        )
        email.attach('Zlecenie {}.pdf'.format(commission.pk),
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


class ChangeCommissionStatus(View):
    def post(self, request, *args, **kwargs):
        status = request.POST.get('status')
        pk = request.POST.get('pk')
        if status not in dict(Commission.STATUS_CHOICES).keys():
            return JsonResponse({}, status=400)
        try:
            commission = Commission.objects.get(pk=pk)
        except Commission.DoesNotExist:
            return JsonResponse({}, status=400)
        commission.status = status
        if not commission.end_date and status == Commission.DONE:
            commission.end_date = datetime.date.today()
        commission.save()
        return JsonResponse({})


class PrepareInvoiceUrl(View):
    def post(self, request, *args, **kwargs):
        desc = ' '.join(request.POST.getlist('desc'))
        pk = request.POST.get('pk')
        done = request.POST.get('done')
        invoice_type = request.POST.get('invoice_type')

        try:
            commission = Commission.objects.get(pk=pk)
        except Commission.DoesNotExist:
            return JsonResponse({}, status=400)
        if done and commission.status != Commission.DONE:
            commission.status = Commission.DONE
            commission.save()

        url = '{}{}'.format(
            reverse('invoicing:sale_invoice_commission_create', kwargs={
                'kind': dict(INVOICE_TYPES)[invoice_type],
                'type': invoice_type,
                'slug': slugify(commission),
                'pk': pk
            }),
            '?desc={}'.format(desc) if desc else '')
        return JsonResponse({'url': url})


class DecodeAztecCode(View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        try:
            output = subprocess.check_output(['./scripts/aztec', code])
            output = output.decode("utf-16", errors='ignore').strip()
        except subprocess.CalledProcessError:
            return JsonResponse({}, status=400)
        values = output.split('|')
        response_data = {
            'registration_plate': values[7],
            'vin': values[13],
            'brand': values[8],
            'model': values[12],
            'engine_volume': int(values[48].split(',')[0]),
            'engine_power': int(values[49].split(',')[0]),
            'production_year': int(values[56]),
        }
        try:
            vehicle = Vehicle.objects.get(vin=response_data['vin'])
            response_data['pk'] = vehicle.pk
            response_data['label'] = str(vehicle)
        except Vehicle.DoesNotExist:
            response_data['pk'] = None
        return JsonResponse(response_data)
