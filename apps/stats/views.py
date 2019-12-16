from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser

from django.views.generic import View
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Sum, Avg, Count, Func, F, FloatField
from django.db.models.functions import ExtractYear, ExtractMonth
from django.template.defaultfilters import date as _date

from KlimaKar.mixins import GroupAccessControlMixin
from KlimaKar.templatetags.slugify import slugify
from apps.warehouse.models import Invoice, Ware, WarePriceChange, Supplier
from apps.invoicing.models import SaleInvoice, Contractor, RefrigerantWeights
from apps.commission.models import Commission
from apps.stats.models import ReceiptPTU
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
        now = datetime.today()
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
            invoices = invoices.annotate(total=Sum(F('invoiceitem__price') * F('invoiceitem__quantity')))
        if metric == 'Avg':
            invoices = invoices.annotate(total=Round(F('invoiceitem__price') * F('invoiceitem__quantity')))
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
        now = datetime.today()
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


class BigChartHistoryMixin(ChartDataMixin, View):
    how_many_shown = 4
    model = None
    date_field = None
    price_field = None
    quantity_field = None

    def get(self, *args, **kwargs):
        self.date_option = self.request.GET.get(
            'date_select', self._get_default_date_option(**kwargs))
        self.metric = self.request.GET.get('custom_select', 'Sum')
        self.objects = self.model.objects.all()
        self._filter_objects(**kwargs)
        self._generate_response_data()
        return JsonResponse(self.response_data)

    def _filter_objects(self, **kwargs):
        pass

    def _get_default_date_option(self, **kwargs):
        return 'week'

    def _annotate(self, qs):
        annotate_functions = {
            'Sum': self._annotate_sum,
            'Avg': self._annotate_avg,
            'Count': self._annotate_count,
        }
        return annotate_functions[self.metric](qs)

    def _annotate_sum(self, qs):
        return qs.annotate(total=Sum(
            F(self.price_field) * F(self.quantity_field),
            output_field=FloatField()))

    def _annotate_avg(self, qs):
        return qs.annotate(total=Round(Avg(
            F(self.price_field) * F(self.quantity_field),
            output_field=FloatField())))

    def _annotate_count(self, qs):
        self.response_data['custom']['values_appendix'] = ''
        return qs.annotate(total=Count('id'))

    def _generate_response_data(self):
        self.response_data = self.get_response_data_template(legend_display=False, values_appendix=' zł')
        data_functions = {
            'week': self._get_week,
            'month': self._get_month,
            'year': self._get_year,
            'all_monthly': self._get_all_monthly,
            'all_yearly': self._get_all_yearly
        }
        data_functions[self.date_option]()

    def _get_date_filter_kwargs(self, date):
        return {
            '{}__gte'.format(self.date_field): date
        }

    def _get_week(self):
        date = datetime.today() - relativedelta(days=6)
        self.objects = self.objects.filter(**self._get_date_filter_kwargs(date))
        self.objects = self.objects.values(self.date_field)
        self.objects = self._annotate(self.objects)
        self.objects = self.objects.values_list('total', self.date_field).order_by(self.date_field)
        values = list(self.objects.values_list('total', flat=True))
        days_between = (datetime.today() - date).days
        for i in range(days_between + 1):
            x = date + relativedelta(days=i)
            if x.date() not in self.objects.values_list(self.date_field, flat=True):
                values.insert(i, 0)

        self.response_data['data']['labels'] = [DAYS[(date + relativedelta(days=i)).weekday()]
                                                for i in range(days_between + 1)]
        self.response_data['data']['datasets'].append(self.get_dataset(values, COLORS[0]))

    def _get_month(self):
        date = datetime.today() - relativedelta(months=1)
        self.objects = self.objects.filter(**self._get_date_filter_kwargs(date))
        self.objects = self.objects.values(self.date_field)
        self.objects = self._annotate(self.objects)
        self.objects = self.objects.values_list('total', self.date_field).order_by(self.date_field)
        values = list(self.objects.values_list('total', flat=True))
        days_between = (date.today() - date).days
        for i in range(days_between + 1):
            x = date + relativedelta(days=i)
            if x.date() not in self.objects.values_list(self.date_field, flat=True):
                values.insert(i, 0)

        self.response_data['data']['labels'] = [(date + relativedelta(days=i)).strftime('%d/%m')
                                                for i in range(days_between + 1)]
        self.response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[0]))

    def _get_year(self):
        date = (datetime.today() - relativedelta(years=1, months=-1)).replace(day=1)
        self.objects = self.objects.filter(**self._get_date_filter_kwargs(date))
        self.objects = self.objects.annotate(
                month=ExtractMonth(self.date_field), year=ExtractYear(self.date_field)).values('year', 'month')
        self.objects = self._annotate(self.objects)
        self.objects = self.objects.values_list('year', 'month', 'total').order_by('year', 'month')
        values = list(self.objects.values_list('total', flat=True))
        months = list(self.objects.values_list('month', flat=True))
        self.response_data['data']['labels'] = [MONTHS[i - 1] for i in months]
        self.response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[0]))

    def _get_all_monthly(self):
        years = self.objects.annotate(year=ExtractYear(self.date_field)).values_list(
                'year', flat=True).distinct().order_by('year')
        self.response_data['data']['labels'] = MONTHS
        self.response_data['options']['legend']['display'] = True

        colors = COLORS[len(years)-1::-1]
        for i, year in enumerate(years):
            year_objects = self.objects.filter(**{'{}__year'.format(self.date_field): year})
            year_objects = year_objects.annotate(month=ExtractMonth(self.date_field)).values('month')
            year_objects = self._annotate(year_objects)
            year_objects = year_objects.values_list('month', 'total').order_by('month')
            values = list(year_objects.values_list('total', flat=True))
            for j in range(1, 13):
                if j not in year_objects.values_list('month', flat=True):
                    values.insert(j - 1, 0)
            hidden = False
            if i < len(years) - self.how_many_shown:
                hidden = True
            if sum(values) > 0:
                self.response_data['data']['datasets'].append(self.get_dataset(
                    values, colors[i], label=year, fill=False, borderColor=colors[i], hidden=hidden))

    def _get_all_yearly(self):
        self.objects = self.objects.annotate(year=ExtractYear(self.date_field)).values('year')
        self.objects = self._annotate(self.objects)
        self.objects = self.objects.values_list('year', 'total').exclude(total=0).order_by('year')

        self.response_data['data']['labels'] = list(self.objects.values_list('year', flat=True))
        self.response_data['data']['datasets'].append(self.get_dataset(
            list(self.objects.values_list('total', flat=True)),
            COLORS[0]))


class PurchaseInvoicesHistory(GroupAccessControlMixin, BigChartHistoryMixin):
    allowed_groups = ['boss']
    model = Invoice
    date_field = 'date'
    price_field = 'invoiceitem__price'
    quantity_field = 'invoiceitem__quantity'

    def _filter_objects(self, **kwargs):
        supplier = kwargs.get('supplier')
        if supplier:
            self.objects = self.objects.filter(supplier__pk=supplier)

    def _get_default_date_option(self, **kwargs):
        supplier = kwargs.get('supplier')
        if supplier:
            return 'year'
        return 'week'


class SaleInvoicesHistory(GroupAccessControlMixin, BigChartHistoryMixin):
    allowed_groups = ['boss']
    model = SaleInvoice
    date_field = 'issue_date'
    price_field = 'saleinvoiceitem__price_'
    quantity_field = 'saleinvoiceitem__quantity'

    def _annotate(self, qs):
        if self.metric == 'SumBrutto':
            self.metric = 'Sum'
            self.price_field = '{}brutto'.format(self.price_field)
        if self.metric == 'SumNetto':
            self.metric = 'Sum'
            self.price_field = '{}netto'.format(self.price_field)
        if self.metric == 'AvgBrutto':
            self.metric = 'Avg'
            self.price_field = '{}brutto'.format(self.price_field)
        if self.metric == 'AvgNetto':
            self.metric = 'Avg'
            self.price_field = '{}netto'.format(self.price_field)
        return super()._annotate(qs)


class CommissionHistory(GroupAccessControlMixin, BigChartHistoryMixin):
    allowed_groups = ['boss']
    model = Commission
    date_field = 'end_date'
    price_field = 'commissionitem__price'
    quantity_field = 'commissionitem__quantity'

    def _filter_objects(self, **kwargs):
        self.objects = self.objects.filter(status=Commission.DONE)


class RefrigerantWeightsHistory(ChartDataMixin, View):
    how_many_shown = 4

    def get(self, *args, **kwargs):
        date_option = self.request.GET.get('date_select', 'week')
        refrigerant = self.request.GET.get('custom_select', 'r134a')
        now = datetime.today()
        if date_option == 'week':
            date = now - relativedelta(days=6)
        elif date_option == 'month':
            date = now - relativedelta(months=1)
        elif date_option == 'year':
            date = (now - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None

        invoices = SaleInvoice.objects.exclude(invoice_type__in=[
            SaleInvoice.TYPE_PRO_FORMA, SaleInvoice.TYPE_CORRECTIVE, SaleInvoice.TYPE_WDT_PRO_FORMA])
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
                    'url': reverse('warehouse:invoice_detail', kwargs={
                        'pk': change.invoice.pk,
                        'slug': slugify(change.invoice),
                        }),
                    'number': change.invoice.number
                },
                'ware': {
                    'url': reverse('warehouse:ware_detail', kwargs={
                        'pk': change.ware.pk,
                        'slug': slugify(change.ware)}),
                    'index': change.ware.index,
                },
                'supplier': {
                    'url': reverse('warehouse:supplier_detail', kwargs={
                        'pk': change.invoice.supplier.pk,
                        'slug': slugify(change.invoice.supplier)
                        }),
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
        invoices = SaleInvoice.objects.exclude(invoice_type__in=[
            SaleInvoice.TYPE_PRO_FORMA, SaleInvoice.TYPE_WDT_PRO_FORMA]).filter(
                payed=False).order_by('payment_date')
        response = {'invoices': []}
        for invoice in invoices:
            if not invoice.payment_date:
                invoice.payed = True
                invoice.save()
                continue
            response['invoices'].append({
                'url': reverse('invoicing:sale_invoice_detail', kwargs={
                    'pk': invoice.pk,
                    'slug': slugify(invoice)
                }),
                'number': invoice.number,
                'brutto_price': "{0:.2f} zł".format(invoice.total_value_brutto).replace('.', ','),
                'payment_date': _date(invoice.payment_date, "d E Y"),
                'is_exceeded': invoice.payment_date < date.today(),
                'contractor': {
                    'url': reverse('invoicing:contractor_detail', kwargs={
                        'pk': invoice.contractor.pk,
                        'slug': slugify(invoice.contractor)
                    }),
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

        if group == 'purchase':
            response = {
                'ware_count': Ware.objects.filter(
                    created_date__date__gte=date_from, created_date__date__lte=date_to).count(),
                'supplier_count': Supplier.objects.filter(
                    created_date__date__gte=date_from, created_date__date__lte=date_to).count(),
                'invoice_count': Invoice.objects.filter(
                    created_date__date__gte=date_from, created_date__date__lte=date_to).count()
            }
            if has_permission:
                invoices = Invoice.objects.filter(date__gte=date_from, date__lte=date_to)
                invoices_sum = 0
                if invoices:
                    invoices_sum = invoices.aggregate(
                        total=Sum(F('invoiceitem__price') * F('invoiceitem__quantity')))['total']
                response['invoice_sum'] = "{0:.2f} zł".format(invoices_sum).replace('.', ',')

        if group == 'sale':
            response = {
                'contractor_count': Contractor.objects.filter(
                    created_date__date__gte=date_from, created_date__date__lte=date_to).count(),
                'sale_invoice_count': SaleInvoice.objects.filter(
                    issue_date__gte=date_from, issue_date__lte=date_to).count()
            }
            if has_permission:
                invoices = SaleInvoice.objects.filter(
                    issue_date__gte=date_from, issue_date__lte=date_to).exclude(invoice_type__in=[
                        SaleInvoice.TYPE_PRO_FORMA, SaleInvoice.TYPE_CORRECTIVE, SaleInvoice.TYPE_WDT_PRO_FORMA])
                invoices_sum = 0
                invoices_sum_brutto = 0
                tax_sum = 0
                person_tax_sum = 0
                if invoices:
                    invoices_sum = invoices.aggregate(Sum('total_value_netto'))['total_value_netto__sum']
                    invoices_sum_brutto = invoices.aggregate(Sum('total_value_brutto'))['total_value_brutto__sum']
                    tax_sum = invoices.annotate(
                        vat=F('total_value_brutto') - F('total_value_netto')).aggregate(Sum('vat'))['vat__sum']
                invoices = invoices.filter(contractor__nip=None)
                if invoices:
                    person_tax_sum = invoices.annotate(
                        vat=F('total_value_brutto') - F('total_value_netto')).aggregate(Sum('vat'))['vat__sum']

                response['sale_invoice_sum'] = "{0:.2f} zł".format(invoices_sum).replace('.', ',')
                response['sale_invoice_sum_brutto'] = "{0:.2f} zł".format(invoices_sum_brutto).replace('.', ',')
                response['vat_sum'] = "{0:.2f} zł".format(tax_sum).replace('.', ',')
                response['person_vat_sum'] = "{0:.2f} zł".format(person_tax_sum).replace('.', ',')
                response['company_vat_sum'] = "{0:.2f} zł".format(tax_sum - person_tax_sum).replace('.', ',')

                ptu_sum = 0
                ptu_objects = ReceiptPTU.objects.filter(date__gte=date_from, date__lte=date_to)
                if ptu_objects:
                    ptu_sum = ptu_objects.aggregate(Sum('value'))['value__sum']
                response['ptu_sum'] = "{0:.2f} zł".format(ptu_sum).replace('.', ',')

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
            response['r134a_sum'] = "{} g".format(r134a)
            response['r1234yf_sum'] = "{} g".format(r1234yf)
            response['r12_sum'] = "{} g".format(r12)
            response['r404_sum'] = "{} g".format(r404)

            commissions = Commission.objects.filter(
                    end_date__gte=date_from, end_date__lte=date_to, status=Commission.DONE)
            response['commission_count'] = commissions.count()
            if has_permission:
                commissions_sum = 0
                if commissions:
                    commissions_sum = commissions.aggregate(Sum('value'))['value__sum']
                response['commission_sum'] = "{0:.2f} zł".format(commissions_sum).replace('.', ',')
        return JsonResponse(response)


class PTUList(GroupAccessControlMixin, View):
    allowed_groups = ['boss']

    def get(self, *args, **kwargs):
        try:
            date_from = date_parser.parse(self.request.GET.get('date_from')).date()
            date_to = date_parser.parse(self.request.GET.get('date_to')).date()
        except TypeError:
            return JsonResponse({'status': 'error', 'message': 'Niepoprawny zakres dat.'}, status=400)
        delta = date_to - date_from
        response = {'ptu': []}
        ptu_sum = 0
        for i in range(delta.days + 1):
            date = date_from + timedelta(days=i)
            try:
                ptu = ReceiptPTU.objects.get(date=date)
                ptu_sum += ptu.value
                response['ptu'].append({
                    'date': _date(ptu.date, "d E Y (l)"),
                    'date_value': _date(ptu.date, "d.m.Y"),
                    'value': "{0:.2f} zł".format(ptu.value).replace('.', ','),
                    'warning': False
                })
            except ReceiptPTU.DoesNotExist:
                response['ptu'].append({
                    'date': _date(date, "d E Y (l)"),
                    'date_value': _date(date, "d.m.Y"),
                    'value': '0,00 zł',
                    'warning': True
                })
        response['sum'] = "{0:.2f} zł".format(ptu_sum).replace('.', ','),
        return JsonResponse(response)


class GetPTUValue(GroupAccessControlMixin, View):
    allowed_groups = ['boss']

    def get(self, *args, **kwargs):
        try:
            date = date_parser.parse(self.request.GET.get('date')).date()
        except TypeError:
            return JsonResponse({'status': 'error', 'message': 'Niepoprawna data.'}, status=400)
        try:
            ptu = ReceiptPTU.objects.get(date=date)
            return JsonResponse({'value': ptu.value})
        except ReceiptPTU.DoesNotExist:
            return JsonResponse({'value': 0})


class SavePTU(GroupAccessControlMixin, View):
    allowed_groups = ['boss']

    def post(self, *args, **kwargs):
        date = date_parser.parse(self.request.POST.get('date'), dayfirst=True).date()
        value = self.request.POST.get('value')
        if not date or not value:
            return JsonResponse({'status': 'error', 'message': 'Niepoprawne dane.'}, status=400)
        try:
            ptu = ReceiptPTU.objects.get(date=date)
        except ReceiptPTU.DoesNotExist:
            ptu = ReceiptPTU(date=date)
        ptu.value = value
        ptu.save()
        return JsonResponse({'status': 'success', 'message': 'Poprawnie zapisano PTU.'})


class GetSummary(GroupAccessControlMixin, View):
    allowed_groups = ['boss']

    def get(self, *args, **kwargs):
        try:
            date_from = date_parser.parse(self.request.GET.get('date_from')).date()
            date_to = date_parser.parse(self.request.GET.get('date_to')).date()
        except TypeError:
            return JsonResponse({'status': 'error', 'message': 'Niepoprawny zakres dat.'}, status=400)
        response = {}
        ptu_sum = self._get_ptu(date_from, date_to)
        response['ptu'] = "{0:.2f} zł".format(ptu_sum).replace('.', ',')

        commissions_sum = self._get_commissions(date_from, date_to)
        response['commissions'] = "{0:.2f} zł".format(commissions_sum).replace('.', ',')

        vat_sum = self._get_vat(date_from, date_to)
        response['vat'] = "{0:.2f} zł".format(vat_sum).replace('.', ',')

        purchase_sum = self._get_purchase(date_from, date_to)
        response['purchase'] = "{0:.2f} zł".format(purchase_sum).replace('.', ',')

        all_sum = commissions_sum - ptu_sum - vat_sum - purchase_sum
        response['sum'] = "{0:.2f} zł".format(all_sum).replace('.', ',')
        date_range = self._get_date_range(date_from, date_to)
        response['urls'] = {
            'commissions': '{}?end_date={}&status=__ALL__'.format(reverse('commission:commissions'), date_range),
            'invoices': '{}?issue_date={}'.format(reverse('invoicing:sale_invoices'), date_range),
            'purchase': '{}?date={}'.format(reverse('warehouse:invoices'), date_range),
            'wares': '{}?purchase_date={}'.format(reverse('warehouse:wares'), date_range),
        }
        return JsonResponse(response)

    def _get_date_range(self, date_from, date_to):
        return '{}+-+{}'.format(
            date_from.strftime('%d.%m.%Y'),
            date_to.strftime('%d.%m.%Y'))

    def _get_ptu(self, date_from, date_to):
        ptu_sum = 0
        ptu_objects = ReceiptPTU.objects.filter(date__gte=date_from, date__lte=date_to)
        if ptu_objects:
            ptu_sum = ptu_objects.aggregate(Sum('value'))['value__sum']
        return ptu_sum

    def _get_commissions(self, date_from, date_to):
        commissions_sum = 0
        commissions = Commission.objects.filter(
                    end_date__gte=date_from, end_date__lte=date_to, status=Commission.DONE)
        if commissions:
            commissions_sum = commissions.aggregate(Sum('value'))['value__sum']
        return commissions_sum

    def _get_vat(self, date_from, date_to):
        vat_sum = 0
        invoices = SaleInvoice.objects.filter(
            issue_date__gte=date_from, issue_date__lte=date_to).exclude(contractor__nip=None)
        if invoices:
            vat_sum = invoices.annotate(
                vat=F('total_value_brutto') - F('total_value_netto')).aggregate(Sum('vat'))['vat__sum']
        return vat_sum

    def _get_purchase(self, date_from, date_to):
        purchase_sum = 0
        invoices = Invoice.objects.filter(date__gte=date_from, date__lte=date_to)
        if invoices:
            purchase_sum = invoices.aggregate(
                total=Sum(F('invoiceitem__price') * F('invoiceitem__quantity')))['total']
        return purchase_sum
