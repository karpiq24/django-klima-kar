import datetime

from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser

from django.views.generic import View
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Sum, Avg, Count, Func, F, FloatField
from django.db.models.functions import ExtractYear, ExtractMonth
from django.template.defaultfilters import date as _date

from KlimaKar.mixins import GroupAccessControlMixin
from apps.warehouse.models import Invoice, Ware, WarePriceChange, Supplier
from apps.invoicing.models import SaleInvoice, Contractor, RefrigerantWeights
from apps.stats.dictionaries import MONTHS, COLORS, DAYS


class ChartDataMixin(object):
    def get_response_data_template(self, chart_type='line', legend_display=True, values_prefix='', values_appendix=''):
        response_data = {
            'type': chart_type,
            'data': {
                'labels': [],
                'datasets': []
            },
            'options': {
                'legend': {
                    'display': legend_display
                }
            },
            'custom': {
                'values_prefix': values_prefix,
                'values_appendix': values_appendix
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


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'


class SupplierPurchaseHistory(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    max_positions = 8

    def get(self, *args, **kwargs):
        date_option = self.request.GET.get('date_select', 'week')
        metric = self.request.GET.get('custom_select', 'Sum')
        now = datetime.datetime.today()
        if date_option == 'week':
            date = now - relativedelta(days=6)
        elif date_option == 'month':
            date = now - relativedelta(months=1)
        elif date_option == 'year':
            date = (now - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None

        invoices = Invoice.objects.all()
        if date:
            invoices = invoices.filter(date__gte=date)

        response_data = self.get_response_data_template(chart_type='doughnut', values_appendix=' zł')
        invoices = invoices.values('supplier')
        if metric == 'Sum':
            invoices = invoices.annotate(total=Sum('total_value'))
        if metric == 'Avg':
            invoices = invoices.annotate(total=Round(Avg('total_value')))
        elif metric == 'Count':
            invoices = invoices.annotate(total=Count('id'))
            response_data['custom']['values_appendix'] = ''
        invoices = invoices.values_list('supplier__name', 'total').order_by('-total')
        if invoices.count() > self.max_positions:
            index = self.max_positions - 1
        else:
            index = invoices.count()

        labels = list(invoices[0:index].values_list('supplier__name', flat=True))
        values = list(invoices[0:index].values_list('total', flat=True))

        if invoices.count() > self.max_positions:
            labels.append('Pozostali dostawcy')
            if metric == 'Avg':
                values.append(invoices[self.max_positions - 1:].values(
                    'total').aggregate(avg=Round(Avg('total')))['avg'])
            else:
                values.append(invoices[self.max_positions - 1:].values(
                    'total').aggregate(Sum('total'))['total__sum'])

        response_data['data']['labels'] = labels
        response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[:len(values)]))

        return JsonResponse(response_data)


class WarePurchaseHistory(ChartDataMixin, View):
    max_positions = 8

    def get(self, *args, **kwargs):
        date_option = self.request.GET.get('date_select', 'week')
        metric = self.request.GET.get('custom_select', 'Count')
        now = datetime.datetime.today()
        if date_option == 'week':
            date = now - relativedelta(days=6)
        elif date_option == 'month':
            date = now - relativedelta(months=1)
        elif date_option == 'year':
            date = (now - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None

        response_data = self.get_response_data_template(chart_type='doughnut', values_appendix=' zł')
        wares = Ware.objects.exclude(invoiceitem=None)
        if date:
            wares = wares.filter(invoiceitem__invoice__date__gte=date)

        if metric == 'Sum':
            wares = wares.annotate(total=Sum(F('invoiceitem__quantity') * F('invoiceitem__price'),
                                   output_field=FloatField()))
        elif metric == 'Count':
            wares = wares.annotate(total=Sum('invoiceitem__quantity'))
            response_data['custom']['values_appendix'] = ''
        wares = wares.values_list('index', 'total').order_by('-total')

        if wares.count() > self.max_positions:
            wares = wares[:self.max_positions]

        response_data['data']['labels'] = list(wares.values_list('index', flat=True))
        values = list(wares.values_list('total', flat=True))
        response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[:len(values)]))

        return JsonResponse(response_data)


class PurchaseInvoicesHistory(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    how_many_shown = 4

    def get(self, *args, **kwargs):
        supplier = kwargs.get('supplier')
        date_option = self.request.GET.get('date_select', 'week' if not supplier else 'year')
        metric = self.request.GET.get('custom_select', 'Sum')
        now = datetime.datetime.today()
        if date_option == 'week':
            date = now - relativedelta(days=6)
        elif date_option == 'month':
            date = now - relativedelta(months=1)
        elif date_option == 'year':
            date = (now - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None

        invoices = Invoice.objects.all()
        if supplier:
            invoices = invoices.filter(supplier__pk=supplier)
        if date:
            invoices = invoices.filter(date__gte=date)

        response_data = self.get_response_data_template(legend_display=False, values_appendix=' zł')

        if date_option == 'week':
            invoices = invoices.values('date')
            if metric == 'Sum':
                invoices = invoices.annotate(total=Sum('total_value'))
            elif metric == 'Avg':
                invoices = invoices.annotate(total=Round(Avg('total_value')))
            elif metric == 'Count':
                invoices = invoices.annotate(total=Count('id'))
                response_data['custom']['values_appendix'] = ''
            invoices = invoices.values_list('total', 'date').order_by('date')
            values = list(invoices.values_list('total', flat=True))
            days_between = (now - date).days
            for i in range(days_between + 1):
                x = date + relativedelta(days=i)
                if x.date() not in invoices.values_list('date', flat=True):
                    values.insert(i, 0)

            response_data['data']['labels'] = [DAYS[(date + relativedelta(days=i)).weekday()]
                                               for i in range(days_between + 1)]
            response_data['data']['datasets'].append(self.get_dataset(
                values, COLORS[0]))

        if date_option == 'month':
            invoices = invoices.values('date')
            if metric == 'Sum':
                invoices = invoices.annotate(total=Sum('total_value'))
            elif metric == 'Avg':
                invoices = invoices.annotate(total=Round(Avg('total_value')))
            elif metric == 'Count':
                invoices = invoices.annotate(total=Count('id'))
                response_data['custom']['values_appendix'] = ''
            invoices = invoices.values_list('total', 'date').order_by('date')
            values = list(invoices.values_list('total', flat=True))
            days_between = (now - date).days
            for i in range(days_between + 1):
                x = date + relativedelta(days=i)
                if x.date() not in invoices.values_list('date', flat=True):
                    values.insert(i, 0)

            response_data['data']['labels'] = [(date + relativedelta(days=i)).strftime('%d/%m')
                                               for i in range(days_between + 1)]
            response_data['data']['datasets'].append(self.get_dataset(
                values, COLORS[0]))

        if date_option == 'year':
            invoices = invoices.annotate(
                month=ExtractMonth('date'), year=ExtractYear('date')).values('year', 'month')
            if metric == 'Sum':
                invoices = invoices.annotate(total=Sum('total_value'))
            elif metric == 'Avg':
                invoices = invoices.annotate(total=Round(Avg('total_value')))
            elif metric == 'Count':
                invoices = invoices.annotate(total=Count('id'))
                response_data['custom']['values_appendix'] = ''
            invoices = invoices.values_list('year', 'month', 'total').order_by('year', 'month')
            values = list(invoices.values_list('total', flat=True))
            months = list(invoices.values_list('month', flat=True))
            response_data['data']['labels'] = [MONTHS[i - 1] for i in months]
            response_data['data']['datasets'].append(self.get_dataset(
                values, COLORS[0]))

        if date_option == 'all_monthly':
            years = invoices.annotate(year=ExtractYear('date')).values_list(
                'year', flat=True).distinct().order_by('year')
            response_data['data']['labels'] = MONTHS
            response_data['options']['legend']['display'] = True

            colors = COLORS[len(years)-1::-1]
            for i, year in enumerate(years):
                year_invoices = invoices.filter(date__year=year)
                year_invoices = year_invoices.annotate(month=ExtractMonth('date')).values('month')
                if metric == 'Sum':
                    year_invoices = year_invoices.annotate(total=Sum('total_value'))
                elif metric == 'Avg':
                    year_invoices = year_invoices.annotate(total=Round(Avg('total_value')))
                elif metric == 'Count':
                    year_invoices = year_invoices.annotate(total=Count('id'))
                    response_data['custom']['values_appendix'] = ''
                year_invoices = year_invoices.values_list('month', 'total').order_by('month')
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

        if date_option == 'all_yearly':
            invoices = invoices.annotate(year=ExtractYear('date')).values('year')
            if metric == 'Sum':
                invoices = invoices.annotate(total=Sum('total_value'))
            elif metric == 'Avg':
                invoices = invoices.annotate(total=Round(Avg('total_value')))
            elif metric == 'Count':
                invoices = invoices.annotate(total=Count('id'))
                response_data['custom']['values_appendix'] = ''
            invoices = invoices.values_list('year', 'total').exclude(total=0).order_by('year')

            response_data['data']['labels'] = list(invoices.values_list('year', flat=True))
            response_data['data']['datasets'].append(self.get_dataset(
                list(invoices.values_list('total', flat=True)),
                COLORS[0]))

        return JsonResponse(response_data)


class SaleInvoicesHistory(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    how_many_shown = 4

    def get(self, *args, **kwargs):
        date_option = self.request.GET.get('date_select', 'week')
        metric = self.request.GET.get('custom_select', 'Sum')
        now = datetime.datetime.today()
        if date_option == 'week':
            date = now - relativedelta(days=6)
        elif date_option == 'month':
            date = now - relativedelta(months=1)
        elif date_option == 'year':
            date = (now - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None

        invoices = SaleInvoice.objects.exclude(invoice_type__in=['2', '3'])
        if date:
            invoices = invoices.filter(issue_date__gte=date)

        response_data = self.get_response_data_template(legend_display=False, values_appendix=' zł')

        if date_option == 'week':
            invoices = invoices.values('issue_date')
            if metric == 'Sum':
                invoices = invoices.annotate(total=Sum('total_value_netto'))
            elif metric == 'Avg':
                invoices = invoices.annotate(total=Round(Avg('total_value_netto')))
            elif metric == 'Count':
                invoices = invoices.annotate(total=Count('id'))
                response_data['custom']['values_appendix'] = ''
            invoices = invoices.values_list('total', 'issue_date').order_by('issue_date')
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

        if date_option == 'month':
            invoices = invoices.values('issue_date')
            if metric == 'Sum':
                invoices = invoices.annotate(total=Sum('total_value_netto'))
            elif metric == 'Avg':
                invoices = invoices.annotate(total=Round(Avg('total_value_netto')))
            elif metric == 'Count':
                invoices = invoices.annotate(total=Count('id'))
                response_data['custom']['values_appendix'] = ''
            invoices = invoices.values_list('total', 'issue_date').order_by('issue_date')
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

        if date_option == 'year':
            invoices = invoices.annotate(
                month=ExtractMonth('issue_date'), year=ExtractYear('issue_date')).values('year', 'month')
            if metric == 'Sum':
                invoices = invoices.annotate(total=Sum('total_value_netto'))
            elif metric == 'Avg':
                invoices = invoices.annotate(total=Round(Avg('total_value_netto')))
            elif metric == 'Count':
                invoices = invoices.annotate(total=Count('id'))
                response_data['custom']['values_appendix'] = ''
            invoices = invoices.values_list('year', 'month', 'total').order_by('year', 'month')
            values = list(invoices.values_list('total', flat=True))
            months = list(invoices.values_list('month', flat=True))
            response_data['data']['labels'] = [MONTHS[i - 1] for i in months]
            response_data['data']['datasets'].append(self.get_dataset(
                values, COLORS[0]))

        if date_option == 'all_monthly':
            years = invoices.annotate(year=ExtractYear('issue_date')).values_list(
                'year', flat=True).distinct().order_by('year')
            response_data['data']['labels'] = MONTHS
            response_data['options']['legend']['display'] = True

            colors = COLORS[len(years)-1::-1]
            for i, year in enumerate(years):
                year_invoices = invoices.filter(issue_date__year=year)
                year_invoices = year_invoices.annotate(month=ExtractMonth('issue_date')).values('month')
                if metric == 'Sum':
                    year_invoices = year_invoices.annotate(total=Sum('total_value_netto'))
                elif metric == 'Avg':
                    year_invoices = year_invoices.annotate(total=Round(Avg('total_value_netto')))
                elif metric == 'Count':
                    year_invoices = year_invoices.annotate(total=Count('id'))
                    response_data['custom']['values_appendix'] = ''
                year_invoices = year_invoices.values_list('month', 'total').order_by('month')
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

        if date_option == 'all_yearly':
            invoices = invoices.annotate(year=ExtractYear('issue_date')).values('year')
            if metric == 'Sum':
                invoices = invoices.annotate(total=Sum('total_value_netto'))
            elif metric == 'Avg':
                invoices = invoices.annotate(total=Round(Avg('total_value_netto')))
            elif metric == 'Count':
                invoices = invoices.annotate(total=Count('id'))
                response_data['custom']['values_appendix'] = ''
            invoices = invoices.values_list('year', 'total').exclude(total=0).order_by('year')

            response_data['data']['labels'] = list(invoices.values_list('year', flat=True))
            response_data['data']['datasets'].append(self.get_dataset(
                list(invoices.values_list('total', flat=True)),
                COLORS[0]))

        return JsonResponse(response_data)


class RefrigerantWeightsHistory(ChartDataMixin, View):
    how_many_shown = 4

    def get(self, *args, **kwargs):
        date_option = self.request.GET.get('date_select', 'week')
        refrigerant = self.request.GET.get('custom_select', 'r134a')
        now = datetime.datetime.today()
        if date_option == 'week':
            date = now - relativedelta(days=6)
        elif date_option == 'month':
            date = now - relativedelta(months=1)
        elif date_option == 'year':
            date = (now - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None

        invoices = SaleInvoice.objects.exclude(invoice_type__in=['2', '3'])
        if date:
            invoices = invoices.filter(issue_date__gte=date)

        response_data = self.get_response_data_template(legend_display=False, values_appendix=' g')

        if date_option == 'week':
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

        elif date_option == 'month':
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

        elif date_option == 'year':
            invoices = invoices.annotate(month=ExtractMonth('issue_date'), year=ExtractYear('issue_date')).values(
                'year', 'month').annotate(total=Sum('refrigerantweights__' + refrigerant)).values_list(
                    'year', 'month', 'total').order_by('year', 'month')
            values = list(invoices.values_list('total', flat=True))
            months = list(invoices.values_list('month', flat=True))
            response_data['data']['labels'] = [MONTHS[i - 1] for i in months]
            response_data['data']['datasets'].append(self.get_dataset(
                values, COLORS[0]))

        elif date_option == 'all_monthly':
            response_data['options']['legend']['display'] = True
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

        elif date_option == 'all_yearly':
            invoices = invoices.annotate(year=ExtractYear('issue_date')).values('year').annotate(
                total=Sum('refrigerantweights__' + refrigerant)).values_list(
                    'year', 'total').exclude(total=0).order_by('year')

            response_data['data']['labels'] = list(invoices.values_list('year', flat=True))
            response_data['data']['datasets'].append(self.get_dataset(
                list(invoices.values_list('total', flat=True)),
                COLORS[0]))

        return JsonResponse(response_data)


class WarePurchaseCost(ChartDataMixin, View):
    min_count = 3

    def get(self, *args, **kwargs):
        ware_pk = self.kwargs.get('pk')
        response_data = self.get_response_data_template(values_appendix=' zł')
        invoices = Invoice.objects.filter(invoiceitem__ware__pk=ware_pk).order_by('date')
        if invoices.count() < self.min_count:
            return JsonResponse({}, status=404)
        response_data['data']['labels'] = list(invoices.values_list('date', flat=True))
        values = list(invoices.values_list('invoiceitem__price', flat=True))
        response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[0]))

        response_data['options']['legend']['display'] = False
        return JsonResponse(response_data)


class WarePriceChanges(View):
    def get(self, *args, **kwargs):
        date_from = date_parser.parse(self.request.GET.get('date_from')).date()
        date_to = date_parser.parse(self.request.GET.get('date_to')).date()
        changes = WarePriceChange.objects.filter(
            created_date__date__gte=date_from, created_date__date__lte=date_to).order_by('-created_date')
        response = {'changes': []}
        for change in changes:
            response['changes'].append({
                'invoice': {
                    'url': reverse('warehouse:invoice_detail', kwargs={'pk': change.invoice.pk}),
                    'number': change.invoice.number
                },
                'ware': {
                    'url': reverse('warehouse:ware_detail', kwargs={'pk': change.ware.pk}),
                    'index': change.ware.index,
                },
                'supplier': {
                    'url': reverse('warehouse:supplier_detail', kwargs={'pk': change.invoice.supplier.pk}),
                    'name': change.invoice.supplier.name
                },
                'is_discount': change.is_discount,
                'last_price': "{0:.2f} zł".format(change.last_price).replace('.', ','),
                'new_price': "{0:.2f} zł".format(change.new_price).replace('.', ','),
                'created_date': _date(change.created_date, "d E Y")
            })
        return JsonResponse(response)


class DuePayments(GroupAccessControlMixin, View):
    allowed_groups = ['boss']

    def get(self, *args, **kwargs):
        invoices = SaleInvoice.objects.filter(payed=False).order_by('payment_date')
        response = {'invoices': []}
        for invoice in invoices:
            response['invoices'].append({
                'url': reverse('invoicing:sale_invoice_detail', kwargs={'pk': invoice.pk}),
                'number': invoice.number,
                'brutto_price': "{0:.2f} zł".format(invoice.total_value_brutto).replace('.', ','),
                'payment_date': _date(invoice.payment_date, "d E Y"),
                'is_exceeded': invoice.payment_date < datetime.date.today(),
                'contractor': {
                    'url': reverse('invoicing:contractor_detail', kwargs={'pk': invoice.contractor.pk}),
                    'name': invoice.contractor.name
                },
                'payed_url': reverse('invoicing:sale_invoice_set_payed', kwargs={'pk': invoice.pk})
            })
        return JsonResponse(response)


class Metrics(View):
    def get(self, *args, **kwargs):
        has_permission = False
        if self.request.user.is_superuser:
            has_permission = True
        elif self.request.user.groups.filter(name='boss').exists():
            has_permission = True

        group = self.request.GET.get('group')
        date_from = date_parser.parse(self.request.GET.get('date_from')).date()
        date_to = date_parser.parse(self.request.GET.get('date_to')).date()

        if group == 'warehouse':
            response = {
                'ware_count': Ware.objects.filter(
                    created_date__date__gte=date_from, created_date__date__lte=date_to).count(),
                'supplier_count': Supplier.objects.filter(
                    created_date__date__gte=date_from, created_date__date__lte=date_to).count(),
                'invoice_count': Invoice.objects.filter(
                    created_date__date__gte=date_from, created_date__date__lte=date_to).count()
            }
            if has_permission:
                invoices = Invoice.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to)
                invoices_sum = 0
                if invoices:
                    invoices_sum = invoices.aggregate(Sum('total_value'))['total_value__sum']
                response['invoice_sum'] = "{0:.2f} zł".format(invoices_sum).replace('.', ',')

        if group == 'invoicing':
            response = {
                'contractor_count': Contractor.objects.filter(
                    created_date__date__gte=date_from, created_date__date__lte=date_to).count(),
                'sale_invoice_count': SaleInvoice.objects.filter(
                    issue_date__gte=date_from, issue_date__lte=date_to).count()
            }
            if has_permission:
                invoices = SaleInvoice.objects.filter(
                    issue_date__gte=date_from, issue_date__lte=date_to).exclude(invoice_type__in=['2', '3'])
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

                response['sale_invoice_sum'] = "{0:.2f} zł".format(invoices_sum).replace('.', ',')
                response['vat_sum'] = "{0:.2f} zł".format(tax_sum).replace('.', ',')
                response['person_vat_sum'] = "{0:.2f} zł".format(person_tax_sum).replace('.', ',')

        if group == 'refrigerant':
            weight_objects = RefrigerantWeights.objects.filter(
                sale_invoice__issue_date__gte=date_from, sale_invoice__issue_date__lte=date_to)
            r134a = 0
            r1234yf = 0
            r12 = 0
            r404 = 0
            if weight_objects:
                r134a = weight_objects.aggregate(Sum('r134a'))['r134a__sum']
                r1234yf = weight_objects.aggregate(Sum('r1234yf'))['r1234yf__sum']
                r12 = weight_objects.aggregate(Sum('r12'))['r12__sum']
                r404 = weight_objects.aggregate(Sum('r404'))['r404__sum']
            response = {
                'r134a_sum': "{} g".format(r134a),
                'r1234yf_sum': "{} g".format(r1234yf),
                'r12_sum': "{} g".format(r12),
                'r404_sum': "{} g".format(r404)
            }
        return JsonResponse(response)
