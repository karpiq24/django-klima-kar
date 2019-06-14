import six
import datetime

from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.db.models import Sum, F
from django.core.exceptions import ImproperlyConfigured

from dateutil.relativedelta import relativedelta
from django_tables2 import SingleTableView
from dal import autocomplete

from apps.warehouse.models import Ware, Invoice, Supplier
from apps.invoicing.models import SaleInvoice, Contractor, RefrigerantWeights


class HomeView(TemplateView):
    template_name = "stats/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        has_permission = False
        if self.request.user.is_superuser:
            has_permission = True
        elif self.request.user.groups.filter(name='boss').exists():
            has_permission = True

        now = datetime.datetime.today()
        this_week = (now - relativedelta(days=now.weekday())).date()

        data = {
            'warehouse': {
                'group': 'warehouse',
                'metrics': [],
                'charts': [],
                'ware_price_changes_url': reverse('stats:ware_price_changes')
            },
            'invoicing': {
                'group': 'invoicing',
                'metrics': [],
                'charts': []
            },
            'refrigerant': {
                'group': 'refrigerant',
                'metrics': [],
                'charts': []
            }
        }
        # Charts for warehouse
        if has_permission:
            data['warehouse']['charts'].append({
                'title': 'Historia faktur zakupowych',
                'url': reverse('stats:purchase_invoices_history'),
                'big': True,
                'select_date': {
                    'extra': True
                },
                'custom_select': [('Sum', 'Suma'), ('Avg', 'Średnia'), ('Count', 'Ilość')]
            })
            data['warehouse']['charts'].append({
                'title': 'Historia zakupów u dostawców',
                'select_date': True,
                'custom_select': [('Sum', 'Suma'), ('Avg', 'Średnia'), ('Count', 'Ilość')],
                'url': reverse('stats:supplier_purchase_history')
            })
        data['warehouse']['charts'].append({
            'title': 'Historia zakupów towarów',
            'select_date': True,
            'custom_select': [('Count', 'Ilość'), ('Sum', 'Suma')],
            'url': reverse('stats:ware_purchase_history')
        })

        # Metrics for warehouse
        data['warehouse']['metrics'].append({
            'icon': 'fa-tags',
            'color': '#E21E00',
            'title': 'Liczba nowych towarów',
            'value': Ware.objects.filter(created_date__date__gte=this_week).count(),
            'class': 'ware_count'
        })
        data['warehouse']['metrics'].append({
            'icon': 'fa-truck',
            'color': '#C1456E',
            'title': 'Liczba nowych dostawców',
            'value': Supplier.objects.filter(created_date__date__gte=this_week).count(),
            'class': 'supplier_count'
        })
        data['warehouse']['metrics'].append({
            'icon': 'fa-file-alt',
            'color': '#8355C5',
            'title': 'Liczba nowych faktur',
            'value': Invoice.objects.filter(created_date__date__gte=this_week).count(),
            'class': 'invoice_count'
        })
        if has_permission:
            invoices = Invoice.objects.filter(created_date__date__gte=this_week)
            invoices_sum = 0
            if invoices:
                invoices_sum = invoices.aggregate(Sum('total_value'))['total_value__sum']
            data['warehouse']['metrics'].append({
                'icon': 'fa-file-alt',
                'color': '#8355C5',
                'title': 'Kwota netto nowych faktur',
                'value': "{0:.2f} zł".format(invoices_sum).replace('.', ','),
                'class': 'invoice_sum'
            })

        # Charts for invoicing
        if has_permission:
            data['invoicing']['charts'].append({
                'title': 'Historia faktur sprzedażowych',
                'url': reverse('stats:sale_invoices_history'),
                'big': True,
                'select_date': {
                    'extra': True
                },
                'custom_select': [('Sum', 'Suma'), ('Avg', 'Średnia'), ('Count', 'Ilość')]
            })

        # Metrics for invoicing
        data['invoicing']['metrics'].append({
            'icon': 'fa-users',
            'color': '#00A0DF',
            'title': 'Liczba nowych kontrahentów',
            'value': Contractor.objects.filter(created_date__date__gte=this_week).count(),
            'class': 'contractor_count'
        })
        data['invoicing']['metrics'].append({
            'icon': 'fa-book',
            'color': '#89D23A',
            'title': 'Liczba nowych faktur',
            'value': SaleInvoice.objects.filter(issue_date__gte=this_week).count(),
            'class': 'sale_invoice_count'
        })
        if has_permission:
            invoices = SaleInvoice.objects.filter(
                issue_date__gte=this_week).exclude(invoice_type__in=['2', '3'])
            invoices_sum = 0
            tax_sum = 0
            person_tax_sum = 0
            if invoices:
                invoices_sum = invoices.aggregate(Sum('total_value_netto'))['total_value_netto__sum']
                tax_sum = invoices.annotate(
                    vat=F('total_value_brutto') - F('total_value_netto')).aggregate(Sum('vat'))['vat__sum']
            invoices = invoices.filter(contractor__nip=None)
            if invoices:
                person_tax_sum = invoices.annotate(
                    vat=F('total_value_brutto') - F('total_value_netto')).aggregate(Sum('vat'))['vat__sum']
            data['invoicing']['metrics'].append({
                'icon': 'fa-book',
                'color': '#89D23A',
                'title': 'Kwota netto nowych faktur',
                'value': "{0:.2f} zł".format(invoices_sum).replace('.', ','),
                'class': 'sale_invoice_sum'
            })
            data['invoicing']['metrics'].append({
                'icon': 'fa-percentage',
                'color': '#E21E00',
                'title': 'Podatek VAT',
                'value': "{0:.2f} zł".format(tax_sum).replace('.', ','),
                'class': 'vat_sum'
            })
            data['invoicing']['metrics'].append({
                'icon': 'fa-percentage',
                'color': '#E21E00',
                'title': 'Podatek VAT od firm',
                'value': "{0:.2f} zł".format(person_tax_sum).replace('.', ','),
                'class': 'company_vat_sum'
            })
            data['invoicing']['metrics'].append({
                'icon': 'fa-percentage',
                'color': '#E21E00',
                'title': 'Podatek VAT od osób fizycznych',
                'value': "{0:.2f} zł".format(person_tax_sum).replace('.', ','),
                'class': 'person_vat_sum'
            })

        # Charts for refrigerant
        data['refrigerant']['charts'].append({
            'title': 'Historia sprzedaży czynników',
            'url': reverse('stats:refrigerant_history'),
            'big': True,
            'select_date': {
                'extra': True
            },
            'custom_select': [('r134a', 'R134a'), ('r1234yf', 'R1234yf'), ('r12', 'R12'), ('r404', 'R404')]
        })
        # Metrics for refrigerant
        weight_objects = RefrigerantWeights.objects.filter(sale_invoice__issue_date__gte=this_week)
        r134a = 0
        r1234yf = 0
        r12 = 0
        r404 = 0
        if weight_objects:
            r134a = weight_objects.aggregate(Sum('r134a'))['r134a__sum']
            r1234yf = weight_objects.aggregate(Sum('r1234yf'))['r1234yf__sum']
            r12 = weight_objects.aggregate(Sum('r12'))['r12__sum']
            r404 = weight_objects.aggregate(Sum('r404'))['r404__sum']
        data['refrigerant']['metrics'].append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Sprzedaż czynnika R134a',
            'value': "{} g".format(r134a),
            'class': 'r134a_sum'
        })
        data['refrigerant']['metrics'].append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Sprzedaż czynnika R1234yf',
            'value': "{} g".format(r1234yf),
            'class': 'r1234yf_sum'
        })
        data['refrigerant']['metrics'].append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Sprzedaż czynnika R12',
            'value': "{} g".format(r12),
            'class': 'r12_sum'
        })
        data['refrigerant']['metrics'].append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Sprzedaż czynnika R404',
            'value': "{} g".format(r404),
            'class': 'r404_sum'
        })

        context['stats'] = data
        return context


class CustomSelect2QuerySetView(autocomplete.Select2QuerySetView):
    modal_create = False

    def get_create_option(self, context, q):
        create_option = []
        display_create_option = False
        if self.modal_create and q:
            display_create_option = True
        elif self.create_field and q:
            page_obj = context.get('page_obj', None)
            if ((page_obj is None or page_obj.number == 1)
                    and not self.get_queryset().filter(**{self.create_field: q}).exists()):
                display_create_option = True

        if display_create_option:
            create_option = [{
                'id': q,
                'text': ('Dodaj "%(new_value)s"') % {'new_value': q},
                'create_id': True,
            }]
        return create_option

    def post(self, request):
        if self.modal_create:
            return JsonResponse({'status': 'disabled'})
        if not self.create_field:
            raise ImproperlyConfigured('Missing "create_field"')

        text = request.POST.get('text', None)

        if text is None:
            return HttpResponseBadRequest()

        result = self.create_object(text)

        return JsonResponse({
            'id': result.pk,
            'text': six.text_type(result),
        })


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

    def get(self, request, *args, **kwargs):
        key = "{}_params".format(self.model.__name__)
        self.request.session[key] = self.request.GET
        if self.request.is_ajax():
            table = self.get_table(**self.get_table_kwargs())
            return JsonResponse({"table": table.as_html(request)})
        else:
            return super().get(request, args, kwargs)
