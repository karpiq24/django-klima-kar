import six

from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.db.models import Sum
from django.core.exceptions import ImproperlyConfigured

from django_tables2 import SingleTableView
from dal import autocomplete

from apps.warehouse.models import Ware, Invoice, Supplier, WarePriceChange
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

        data = {
            'warehouse': {
                'group': 'warehouse',
                'metrics': [],
                'charts': [],
                'price_changes': WarePriceChange.objects.all().order_by('-created_date')
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
            'title': 'Liczba towarów',
            'value': Ware.objects.count()
        })
        data['warehouse']['metrics'].append({
            'icon': 'fa-truck',
            'color': '#C1456E',
            'title': 'Liczba dostawców',
            'value': Supplier.objects.count()
        })
        data['warehouse']['metrics'].append({
            'icon': 'fa-file-alt',
            'color': '#8355C5',
            'title': 'Liczba faktur zakupowych',
            'value': Invoice.objects.count()
        })
        if has_permission:
            data['warehouse']['metrics'].append({
                'icon': 'fa-file-alt',
                'color': '#8355C5',
                'title': 'Łączna wartość faktur zakupowych',
                'value': "{0:.2f} zł".format(
                    Invoice.objects.aggregate(Sum('total_value'))['total_value__sum']).replace('.', ',')
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
            'title': 'Liczba kontrahentów',
            'value': Contractor.objects.count()
        })
        data['invoicing']['metrics'].append({
            'icon': 'fa-book',
            'color': '#89D23A',
            'title': 'Liczba faktur sprzedażowych',
            'value': SaleInvoice.objects.count()
        })
        if has_permission:
            data['invoicing']['metrics'].append({
                'icon': 'fa-book',
                'color': '#89D23A',
                'title': 'Łączna wartość netto faktur sprzedażowych',
                'value': "{0:.2f} zł".format(
                    SaleInvoice.objects.exclude(invoice_type__in=['2', '3']).aggregate(
                        Sum('total_value_netto'))['total_value_netto__sum']).replace('.', ',')
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
        data['refrigerant']['metrics'].append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Łączna sprzedaż czynnika R134a',
            'value': "{} g".format(
                RefrigerantWeights.objects.aggregate(Sum('r134a'))['r134a__sum'])
        })
        data['refrigerant']['metrics'].append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Łączna sprzedaż czynnika R1234yf',
            'value': "{} g".format(
                RefrigerantWeights.objects.aggregate(Sum('r1234yf'))['r1234yf__sum'])
        })
        data['refrigerant']['metrics'].append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Łączna sprzedaż czynnika R12',
            'value': "{} g".format(
                RefrigerantWeights.objects.aggregate(Sum('r12'))['r12__sum'])
        })
        data['refrigerant']['metrics'].append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Łączna sprzedaż czynnika R404',
            'value': "{} g".format(
                RefrigerantWeights.objects.aggregate(Sum('r404'))['r404__sum'])
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
        key = "{}_params".format(self.filter_class)
        self.request.session[key] = self.request.GET
        return context
