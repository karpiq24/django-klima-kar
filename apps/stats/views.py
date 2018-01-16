import datetime

from dateutil.relativedelta import relativedelta

from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import ExtractYear, ExtractMonth

from KlimaKar.mixins import GroupAccessControlMixin
from apps.warehouse.models import Invoice, Ware
from apps.stats.functions import get_random_colors
from apps.stats.dictionaries import MONTHS


class ChartDataMixin(object):
    def get_response_data_template(self):
        response_data = {
            'type': 'line',
            'data': {
                'labels': [],
                'datasets': []
            },
            'options': {
                'legend': {
                    'display': True
                },
            }
        }
        return response_data

    def get_dataset(self, data, colors, label='', borderWidth=1, borderColor='#ffffff', fill=True, hidden=False):
        dataset = {
            'label': label,
            'fill': fill,
            'data': data,
            'borderWidth': borderWidth,
            'backgroundColor': colors,
            'borderColor': borderColor,
            'hidden': hidden
        }
        return dataset


class SupplierAllInvoicesValue(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    max_positions = 8
    last_year = False

    def get(self, *args, **kwargs):
        if self.last_year:
            date = (datetime.datetime.now() - relativedelta(years=1))
            invoices = Invoice.objects.filter(date__gte=date)
        else:
            invoices = Invoice.objects.all()
        data = invoices.values('supplier').annotate(
            total=Sum('total_value')).values_list('supplier__name', 'total').order_by('-total')
        if data.count() > self.max_positions:
            index = self.max_positions - 1
        else:
            index = data.count()

        response_data = self.get_response_data_template()
        labels = list(data[0:index].values_list('supplier__name', flat=True))
        values = list(data[0:index].values_list('total', flat=True))

        if data.count() > self.max_positions:
            labels.append('Pozostali dostawcy')
            values.append(data[self.max_positions - 1:].values(
                'total').aggregate(Sum('total'))['total__sum'])

        response_data['data']['labels'] = labels
        response_data['data']['datasets'].append(self.get_dataset(
            values, get_random_colors(len(values))))

        response_data['type'] = 'doughnut'
        return JsonResponse(response_data)


class InvoicesValueMonthly(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    years_back = 10
    how_many_shown = 4

    def get(self, *args, **kwargs):
        date = (datetime.datetime.now() - relativedelta(years=self.years_back)).replace(day=1, month=1)
        invoices = Invoice.objects.filter(date__gte=date)
        years = invoices.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct().order_by('year')

        response_data = self.get_response_data_template()
        response_data['data']['labels'] = MONTHS

        colors = get_random_colors(len(years))
        for i, year in enumerate(years):
            year_invoices = invoices.filter(date__year=year)
            year_invoices = year_invoices.annotate(month=ExtractMonth('date')).values('month').annotate(
                total=Sum('total_value')).values_list('month', 'total').order_by('month')
            hidden = False
            if i < len(years) - self.how_many_shown:
                hidden = True
            response_data['data']['datasets'].append(self.get_dataset(
                list(year_invoices.values_list('total', flat=True)),
                colors[i], label=year, fill=False, borderColor=colors[i], hidden=hidden))

        return JsonResponse(response_data)


class InvoicesValueYearly(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    years_back = 10

    def get(self, *args, **kwargs):
        date = (datetime.datetime.now() - relativedelta(years=self.years_back)).replace(day=1, month=1)
        invoices = Invoice.objects.filter(date__gte=date)
        invoices = invoices.annotate(year=ExtractYear('date')).values('year').annotate(
            total=Sum('total_value')).values_list('year', 'total').order_by('year')

        response_data = self.get_response_data_template()
        response_data['data']['labels'] = list(invoices.values_list('year', flat=True))
        response_data['data']['datasets'].append(self.get_dataset(
            list(invoices.values_list('total', flat=True)),
            get_random_colors(1)))

        response_data['options']['legend']['display'] = False
        response_data['type'] = 'bar'
        return JsonResponse(response_data)


class WarePurchaseQuantity(ChartDataMixin, View):
    max_positions = 8
    last_year = False

    def get(self, *args, **kwargs):
        if self.last_year:
            wares = Ware.objects.filter(invoiceitem__invoice__date__year=2017)
        else:
            wares = Ware.objects.all()
        wares_quantity = wares.exclude(invoiceitem=None).annotate(
            quantity=Sum('invoiceitem__quantity')).values_list('index', 'quantity').order_by('-quantity')
        if wares_quantity.count() > self.max_positions:
            wares_quantity = wares_quantity[:self.max_positions]

        response_data = self.get_response_data_template()
        response_data['data']['labels'] = list(wares_quantity.values_list('index', flat=True))
        values = list(wares_quantity.values_list('quantity', flat=True))
        response_data['data']['datasets'].append(self.get_dataset(
            values, get_random_colors(len(values))))

        response_data['type'] = 'doughnut'
        return JsonResponse(response_data)
