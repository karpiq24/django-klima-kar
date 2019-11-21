import subprocess
import datetime
import os
import json
import django_rq
import unicodedata

from urllib.parse import urlencode
from smtplib import SMTPRecipientsRefused

from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.generic import DetailView, UpdateView, CreateView, View
from django.template import Template, Context
from django.template.defaultfilters import date as str_date
from django.template.defaultfilters import filesizeformat
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage

from django_tables2.export.views import ExportMixin
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from KlimaKar.email import get_email_message
from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from KlimaKar.mixins import AjaxFormMixin, SingleTableAjaxMixin
from KlimaKar import settings
from KlimaKar.templatetags.slugify import slugify
from apps.settings.models import SiteSettings
from apps.commission.models import Vehicle, Component, Commission, CommissionItem, CommissionFile
from apps.commission.tables import VehicleTable, ComponentTable, CommissionTable, CommissionItemTable
from apps.commission.filters import VehicleFilter, ComponentFilter, CommissionFilter
from apps.commission.forms import VehicleModelForm, ComponentModelForm, CommissionModelForm, CommissionItemInline, \
    CommissionEmailForm, CommissionFastModelForm
from apps.commission.functions import process_uploads, check_uploaded_files, get_temporary_files
from apps.invoicing.models import SaleInvoice


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commission_data = {
            'status': Commission.DONE,
            'start_date': datetime.date.today(),
            'end_date': datetime.date.today(),
        }
        context['status_done'] = Commission.DONE
        context['fast_commission_form'] = CommissionFastModelForm(initial=commission_data)
        context['fast_commission_url'] = reverse('commission:fast_commission')
        return context


class CommissionDetailView(SingleTableAjaxMixin, DetailView):
    model = Commission
    template_name = 'commission/commission/detail.html'
    table_class = CommissionItemTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context['back_url'] = reverse('commission:commissions') + '?' + urlencode(self.request.session.get(key, ''))
        types = dict(SaleInvoice.INVOICE_TYPES)
        types.pop(SaleInvoice.TYPE_CORRECTIVE)
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
            'recipient': self.object.contractor.email if self.object.contractor else ''
        }
        context['email_form'] = CommissionEmailForm(initial=email_data)
        context['email_url'] = reverse('commission:commission_email')

        sms = ''
        if site_settings.COMMISSION_SMS_BODY:
            sms = Template(site_settings.COMMISSION_SMS_BODY).render(Context({'commission': self.object}))
        context['sms'] = self._strip_accents(sms)
        return context

    def _strip_accents(self, text):
        return ''.join(c for c in unicodedata.normalize(
            'NFKD', text) if unicodedata.category(c) != 'Mn').replace('ł', 'l').replace('Ł', 'L')

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
        response = super().forms_valid(form, inlines)
        if check_uploaded_files(form.data['upload_key']):
            self.object.upload = True
            self.object.save()
            django_rq.enqueue(process_uploads, self.object.pk, form.data['upload_key'])
        return response

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
        upload_key = self.request.POST.get('upload_key')
        if upload_key:
            context['temp_files'] = get_temporary_files(upload_key)
        return context

    def forms_valid(self, form, inlines):
        self.generate_pdf = 'generate_pdf' in form.data
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano zmiany.')
        response = super().forms_valid(form, inlines)
        if check_uploaded_files(form.data['upload_key']):
            self.object.upload = True
            self.object.save()
            django_rq.enqueue(process_uploads, self.object.pk, form.data['upload_key'])
        return response

    def get_success_url(self, **kwargs):
        return '{}{}'.format(
            reverse("commission:commission_detail", kwargs={
                'pk': self.object.pk,
                'desc': slugify(str(self.object))
            }), '?pdf' if self.generate_pdf else '')


class FastCommissionCreateView(View):
    def post(self, request, *args, **kwargs):
        form = CommissionFastModelForm(data=request.POST)
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': form.errors}, status=400)
        commission = form.save()
        CommissionItem.objects.create(
            commission=commission,
            name=commission.description,
            price=commission.value
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Zlecenie zostało zapisane',
            'url': self.get_success_url(commission)}, status=200)

    def get_success_url(self, commission):
        return reverse("commission:commission_detail", kwargs={
            'pk': commission.pk,
            'desc': slugify(str(commission))})


class CommissionAutocomplete(CustomSelect2QuerySetView):
    def get_queryset(self):
        commissions = Commission.objects.all().order_by('-pk')
        qs = commissions
        if self.q:
            try:
                qs = commissions.filter(pk=self.q)
            except ValueError:
                qs = commissions.filter(vc_name__icontains=self.q)
        return qs


class CommissionPDFView(View):
    print_version = False

    def get(self, request, *args, **kwargs):
        commission = get_object_or_404(Commission, pk=kwargs.get('pk'))
        pdf_file = commission.generate_pdf()
        response = HttpResponse(content_type='application/pdf')
        response.write(pdf_file)
        response['Content-Disposition'] = 'filename="Zlecenie {}.pdf"'.format(commission.pk)
        response['Content-Encoding'] = None
        response['Content-Type'] = 'application/pdf'
        if not self.print_version:
            response['Content-Disposition'] = 'attachment;' + response['Content-Disposition']
        return response


class CommissionFileDownloadView(View):
    def get(self, request, *args, **kwargs):
        get_object_or_404(Commission, pk=kwargs.get('pk'))
        commission_file = get_object_or_404(CommissionFile, file_name=kwargs.get('name'))
        response = HttpResponse(content_type=commission_file.mime_type)
        response.write(commission_file.file_contents)
        response['Content-Disposition'] = 'filename="{}"'.format(commission_file.file_name)
        response['Content-Encoding'] = None
        response['Content-Type'] = commission_file.mime_type
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


class CommissionFileUplaodView(View):
    def post(self, request, *args, **kwargs):
        upload_key = request.POST.get('key')
        if not upload_key:
            return JsonResponse({'status': 'error', 'message': 'Coś poszło nie tak. Spróbuj ponownie.'}, status=400)

        directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, 'timestamp'), 'w') as timefile:
            timefile.write(str(datetime.datetime.now()))
        for key, file_obj in request.FILES.items():
            with open(os.path.join(directory, '{}.meta'.format(file_obj.name)), 'w') as metafile:
                metafile.write(json.dumps(
                    {'name': file_obj.name, 'size': file_obj.size, 'type': file_obj.content_type}))
            with default_storage.open('{}/{}'.format(directory, key), 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
        return JsonResponse({
            'status': 'success',
            'message': 'Pliki zostały zapisane.',
            'files': get_temporary_files(upload_key)
            }, status=200)


class CheckUploadFinishedView(View):
    def get(self, request, *args, **kwargs):
        commission = get_object_or_404(Commission, pk=request.GET.get('pk'))
        if commission.upload:
            return JsonResponse({'status': 'progress'}, status=200)
        return JsonResponse({'status': 'success', 'files': [{
            'name': f.file_name,
            'size': filesizeformat(f.file_size),
            'url': reverse('commission:commission_file_download', kwargs={
                'pk': commission.pk,
                'desc': slugify(str(commission)),
                'name': f.file_name
            })}
            for f in commission.commissionfile_set.all()]}, status=200)


class DeleteTempFile(View):
    def post(self, request, *args, **kwargs):
        upload_key = request.POST.get('key')
        fname = request.POST.get('file')
        if not upload_key or not fname:
            return JsonResponse({'status': 'error', 'message': 'Coś poszło nie tak. Spróbuj ponownie.'}, status=400)
        fpath = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
        metapath = '{}.meta'.format(fpath)
        if os.path.exists(metapath):
            os.remove(metapath)
        return JsonResponse({
            'status': 'success',
            'message': 'Plik został usunięty.',
            }, status=200)


class DeleteCommissionFile(View):
    def post(self, request, *args, **kwargs):
        get_object_or_404(Commission, pk=request.POST.get('object'))
        commission_file = get_object_or_404(CommissionFile, pk=request.POST.get('file'))
        commission_file.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Plik został usunięty.',
            }, status=200)


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
        if not commission.end_date and status in [Commission.DONE, Commission.CANCELLED]:
            commission.end_date = datetime.date.today()
        if status not in [Commission.DONE, Commission.CANCELLED]:
            commission.end_date = None
        commission.save()
        return JsonResponse({'end_date': str_date(commission.end_date) if commission.end_date else '—'})


class PrepareInvoiceUrl(View):
    def post(self, request, *args, **kwargs):
        desc = ' '.join(request.POST.getlist('desc'))
        pk = request.POST.get('pk')
        done = request.POST.get('done')
        invoice_type = request.POST.get('invoice_type')
        value_type = request.POST.get('value_type')

        try:
            commission = Commission.objects.get(pk=pk)
        except Commission.DoesNotExist:
            return JsonResponse({}, status=400)
        if done and commission.status != Commission.DONE:
            commission.status = Commission.DONE
            commission.save()

        url = '{}{}{}'.format(
            reverse('invoicing:sale_invoice_commission_create', kwargs={
                'kind': dict(SaleInvoice.INVOICE_TYPES)[invoice_type],
                'type': invoice_type,
                'slug': slugify(commission),
                'pk': pk
            }),
            '?value_type={}'.format(value_type),
            '&desc={}'.format(desc) if desc else '')
        return JsonResponse({'url': url})


class AssignInoiceView(View):
    def post(self, request, *args, **kwargs):
        commission = request.POST.get('commission')
        invoice = request.POST.get('invoice')
        try:
            commission = Commission.objects.get(pk=commission)
        except Commission.DoesNotExist:
            return JsonResponse({'message': 'Takie zlecenie nie istnieje.'}, status=400)
        try:
            invoice = SaleInvoice.objects.get(pk=invoice)
        except SaleInvoice.DoesNotExist:
            return JsonResponse({'message': 'Taka faktura nie istnieje.'}, status=400)
        if invoice in commission.sale_invoices.all():
            return JsonResponse({
                'status': 'warning',
                'message': 'Ta faktura była już wcześniej przypisana do tego zlecenia.'
            }, status=200)
        commission.sale_invoices.add(invoice)
        return JsonResponse({
            'status': 'success',
            'message': 'Faktura została przypisana do zlecenia.',
            'commission': {
                'name': str(commission),
                'url': reverse("commission:commission_detail", kwargs={
                    'pk': commission.pk,
                    'desc': slugify(str(commission))
                })
            },
            'sale_invoice': {
                'name': str(invoice),
                'url': reverse("invoicing:sale_invoice_detail", kwargs={
                    'pk': invoice.pk,
                    'kind': slugify(invoice.get_invoice_type_display()),
                    'number': slugify(invoice.number)
                })
            }
            }, status=200)


class UnassignInoiceView(View):
    def post(self, request, *args, **kwargs):
        commission = request.POST.get('commission')
        invoice = request.POST.get('invoice')
        try:
            commission = Commission.objects.get(pk=commission)
        except Commission.DoesNotExist:
            return JsonResponse({'message': 'Takie zlecenie nie istnieje.'}, status=400)
        try:
            invoice = SaleInvoice.objects.get(pk=invoice)
        except SaleInvoice.DoesNotExist:
            return JsonResponse({'message': 'Taka faktura nie istnieje.'}, status=400)
        if invoice not in commission.sale_invoices.all():
            return JsonResponse({
                'status': 'warning',
                'message': 'Ta faktura nie jest przypisana do wskazanego zlecenia.'
            }, status=200)
        commission.sale_invoices.remove(invoice)
        return JsonResponse({
            'status': 'success',
            'message': 'Faktura odłączona od zlecenia.',
            }, status=200)


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
