import datetime
import calendar

from dateutil.relativedelta import relativedelta

from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay

from KlimaKar.mixins import GroupAccessControlMixin
from apps.warehouse.models import Invoice, Ware
from apps.invoicing.models import SaleInvoice
from apps.stats.dictionaries import MONTHS, COLORS, DAYS


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
            values, COLORS[:len(values)]))

        response_data['type'] = 'doughnut'
        return JsonResponse(response_data)


class InvoicesValueMonthly(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    years_back = 9
    how_many_shown = 4

    def get(self, *args, **kwargs):
        date = (datetime.datetime.now() - relativedelta(years=self.years_back)).replace(day=1, month=1)
        invoices = Invoice.objects.filter(date__gte=date)
        years = invoices.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct().order_by('year')

        response_data = self.get_response_data_template()
        response_data['data']['labels'] = MONTHS

        colors = COLORS[len(years)-1::-1]
        for i, year in enumerate(years):
            year_invoices = invoices.filter(date__year=year)
            year_invoices = year_invoices.annotate(month=ExtractMonth('date')).values('month').annotate(
                total=Sum('total_value')).values_list('month', 'total').order_by('month')
            values = list(year_invoices.values_list('total', flat=True))
            for j in range(1, 13):
                if j not in year_invoices.values_list('month', flat=True):
                    values.insert(j - 1, 0)
            hidden = False
            if i < len(years) - self.how_many_shown:
                hidden = True
            response_data['data']['datasets'].append(self.get_dataset(
                values, colors[i], label=year, fill=False, borderColor=colors[i], hidden=hidden))

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
            COLORS[0]))

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
            values, COLORS[:len(values)]))

        response_data['type'] = 'doughnut'
        return JsonResponse(response_data)


class WarePurchaseCost(ChartDataMixin, View):
    min_count = 3

    def get(self, *args, **kwargs):
        ware_pk = self.kwargs.get('pk')
        response_data = self.get_response_data_template()
        invoices = Invoice.objects.filter(invoiceitem__ware__pk=ware_pk).order_by('date')
        if invoices.count() < self.min_count:
            return JsonResponse({}, status=404)
        response_data['data']['labels'] = list(invoices.values_list('date', flat=True))
        values = list(invoices.values_list('invoiceitem__price', flat=True))
        response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[0]))

        response_data['options']['legend']['display'] = False
        return JsonResponse(response_data)


class SaleInvoicesValueMonthly(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    years_back = 9
    how_many_shown = 4

    def get(self, *args, **kwargs):
        date = (datetime.datetime.now() - relativedelta(years=self.years_back)).replace(day=1, month=1)
        invoices = SaleInvoice.objects.filter(issue_date__gte=date).exclude(invoice_type__in=['2', '3'])
        years = invoices.annotate(year=ExtractYear('issue_date')).values_list(
            'year', flat=True).distinct().order_by('year')

        response_data = self.get_response_data_template()
        response_data['data']['labels'] = MONTHS

        colors = COLORS[len(years)-1::-1]
        for i, year in enumerate(years):
            year_invoices = invoices.filter(issue_date__year=year)
            year_invoices = year_invoices.annotate(month=ExtractMonth('issue_date')).values('month').annotate(
                total=Sum('total_value_netto')).values_list('month', 'total').order_by('month')
            values = list(year_invoices.values_list('total', flat=True))
            for j in range(1, 13):
                if j not in year_invoices.values_list('month', flat=True):
                    values.insert(j - 1, 0)
            hidden = False
            if i < len(years) - self.how_many_shown:
                hidden = True
            response_data['data']['datasets'].append(self.get_dataset(
                values, colors[i], label=year, fill=False, borderColor=colors[i], hidden=hidden))

        return JsonResponse(response_data)


class SaleInvoicesValueYearly(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    years_back = 10

    def get(self, *args, **kwargs):
        date = (datetime.datetime.now() - relativedelta(years=self.years_back)).replace(day=1, month=1)
        invoices = SaleInvoice.objects.filter(issue_date__gte=date)
        invoices = invoices.annotate(year=ExtractYear('issue_date')).values('year').annotate(
            total=Sum('total_value_netto')).values_list('year', 'total').order_by('year')

        response_data = self.get_response_data_template()
        response_data['data']['labels'] = list(invoices.values_list('year', flat=True))
        response_data['data']['datasets'].append(self.get_dataset(
            list(invoices.values_list('total', flat=True)),
            COLORS[1]))

        response_data['options']['legend']['display'] = False
        response_data['type'] = 'bar'
        return JsonResponse(response_data)


class RefrigerantWeightsHistory(ChartDataMixin, View):
    years_back = 9
    how_many_shown = 4

    def get(self, *args, **kwargs):
        date_option = self.request.GET.get('date_select', '0')
        refrigerant = ['r134a', 'r1234yf', 'r12', 'r404'][int(self.request.GET.get('custom_select'), 0) - 1]
        now = datetime.datetime.today()
        if date_option == '0':
            date = now - relativedelta(days=6)
        elif date_option == '1':
            date = now - relativedelta(months=1)
        elif date_option == '2':
            date = (now - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None

        invoices = SaleInvoice.objects.exclude(invoice_type__in=['2', '3'])
        if date:
            invoices = invoices.filter(issue_date__gte=date)

        response_data = self.get_response_data_template()

        if date_option == '0':
            invoices = invoices.values('issue_date').annotate(
                total=Sum('refrigerantweights__' + refrigerant)).values_list(
                    'total', 'issue_date').order_by('issue_date')
            values = list(invoices.values_list('total', flat=True))
            days_between = (now - date).days
            for i in range(days_between + 1):
                x = date + relativedelta(days=i)
                if x.date() not in invoices.values_list('issue_date', flat=True):
                    values.insert(i, 0)

            response_data['data']['labels'] = [DAYS[(date + relativedelta(days=i)).weekday()]
                                               for i in range(days_between + 1)]
            response_data['data']['datasets'].append(self.get_dataset(
                values, COLORS[0]))
            response_data['options']['legend']['display'] = False

        if date_option == '1':
            invoices = invoices.values('issue_date').annotate(
                total=Sum('refrigerantweights__' + refrigerant)).values_list(
                    'total', 'issue_date').order_by('issue_date')
            values = list(invoices.values_list('total', flat=True))
            days_between = (now - date).days
            for i in range(days_between + 1):
                x = date + relativedelta(days=i)
                if x.date() not in invoices.values_list('issue_date', flat=True):
                    values.insert(i, 0)

            response_data['data']['labels'] = [(date + relativedelta(days=i)).strftime('%d/%m')
                                               for i in range(days_between + 1)]
            response_data['data']['datasets'].append(self.get_dataset(
                values, COLORS[0]))
            response_data['options']['legend']['display'] = False

        if date_option == '2':
            invoices = invoices.annotate(month=ExtractMonth('issue_date'), year=ExtractYear('issue_date')).values(
                'year', 'month').annotate(total=Sum('refrigerantweights__' + refrigerant)).values_list(
                    'year', 'month', 'total').order_by('year', 'month')
            values = list(invoices.values_list('total', flat=True))
            months = list(invoices.values_list('month', flat=True))
            response_data['data']['labels'] = [MONTHS[i - 1] for i in months]
            response_data['data']['datasets'].append(self.get_dataset(
                values, COLORS[0]))
            response_data['options']['legend']['display'] = False

        if date_option == '3':
            years = invoices.annotate(year=ExtractYear('issue_date')).values_list(
                'year', flat=True).distinct().order_by('year')
            response_data['data']['labels'] = MONTHS

            colors = COLORS[len(years)-1::-1]
            for i, year in enumerate(years):
                year_invoices = invoices.filter(issue_date__year=year)
                year_invoices = year_invoices.annotate(month=ExtractMonth('issue_date')).values('month').annotate(
                    total=Sum('refrigerantweights__' + refrigerant)).values_list('month', 'total').order_by('month')
                values = list(year_invoices.values_list('total', flat=True))
                for j in range(1, 13):
                    if j not in year_invoices.values_list('month', flat=True):
                        values.insert(j - 1, 0)
                hidden = False
                if i < len(years) - self.how_many_shown:
                    hidden = True
                if sum(values) > 0:
                    response_data['data']['datasets'].append(self.get_dataset(
                        values, colors[i], label=year, fill=False, borderColor=colors[i], hidden=hidden))

        if date_option == '4':
            invoices = invoices.annotate(year=ExtractYear('issue_date')).values('year').annotate(
                total=Sum('refrigerantweights__' + refrigerant)).values_list(
                    'year', 'total').exclude(total=0).order_by('year')

            response_data = self.get_response_data_template()
            response_data['data']['labels'] = list(invoices.values_list('year', flat=True))
            response_data['data']['datasets'].append(self.get_dataset(
                list(invoices.values_list('total', flat=True)),
                COLORS[0]))

            response_data['options']['legend']['display'] = False
            response_data['type'] = 'bar'

        return JsonResponse(response_data)
