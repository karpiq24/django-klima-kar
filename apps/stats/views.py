from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser

from django.views.generic import View
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Sum, Avg, Count, F, FloatField
from django.template.defaultfilters import date as _date

from KlimaKar.mixins import GroupAccessControlMixin
from KlimaKar.templatetags.slugify import slugify
from apps.warehouse.models import Invoice, Ware, WarePriceChange, Supplier
from apps.invoicing.models import SaleInvoice, Contractor, RefrigerantWeights
from apps.commission.models import Commission
from apps.stats.models import ReceiptPTU, Round
from apps.stats.mixins import ChartDataMixin, BigChartHistoryMixin
from apps.stats.dictionaries import COLORS


class SupplierPurchaseHistory(GroupAccessControlMixin, ChartDataMixin, View):
    allowed_groups = ['boss']
    max_positions = 8

    def get(self, *args, **kwargs):
        self.date_option = self.request.GET.get('date_select', 'week')
        self.metric = self.request.GET.get('custom_select', 'Sum')

        self.invoices = self.get_invoices()
        self.response_data = self.get_response_data_template(chart_type='doughnut', values_appendix=' zł')
        self.invoices = self.invoices.values('supplier')
        self.invoices = self._annotate(self.invoices)
        self.invoices = self.invoices.values_list('supplier__name', 'total').order_by('-total')
        if self.invoices.count() > self.max_positions:
            index = self.max_positions - 1
        else:
            index = self.invoices.count()

        labels = list(self.invoices[0:index].values_list('supplier__name', flat=True))
        values = list(self.invoices[0:index].values_list('total', flat=True))

        if self.invoices.count() > self.max_positions:
            labels.append('Pozostali dostawcy')
            if self.metric == 'Avg':
                values.append(self.invoices[self.max_positions - 1:].values(
                    'total').aggregate(avg=Round(Avg('total')))['avg'])
            else:
                values.append(self.invoices[self.max_positions - 1:].values(
                    'total').aggregate(Sum('total'))['total__sum'])

        self.response_data['data']['labels'] = labels
        self.response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[:len(values)]))

        return JsonResponse(self.response_data)

    def get_invoices(self):
        invoices = Invoice.objects.all()
        if self.date_option == 'week':
            date = datetime.today() - relativedelta(days=6)
        elif self.date_option == 'month':
            date = datetime.today() - relativedelta(months=1)
        elif self.date_option == 'year':
            date = (datetime.today() - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None
        if date:
            invoices = invoices.filter(date__gte=date)
        return invoices

    def _annotate(self, qs):
        if self.metric == 'Sum':
            return self.invoices.annotate(total=Sum(
                F('invoiceitem__price') * F('invoiceitem__quantity')))
        if self.metric == 'Avg':
            return self.invoices.annotate(total=Round(
                F('invoiceitem__price') * F('invoiceitem__quantity')))
        elif self.metric == 'Count':
            self.response_data['custom']['values_appendix'] = ''
            return self.invoices.annotate(total=Count('id'))


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
            wares = wares.annotate(total=Sum(
                F('invoiceitem__quantity') * F('invoiceitem__price'),
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
        self.objects = self.objects.filter(status=Commission.DONE).exclude(end_date=None)


class RefrigerantWeightsHistory(BigChartHistoryMixin):
    model = SaleInvoice
    date_field = 'issue_date'
    values_appendix = ' g'

    def _annotate(self, qs):
        return qs.annotate(total=Sum('refrigerantweights__' + self.metric))


class WarePurchaseCost(ChartDataMixin, View):
    min_count = 3

    def get(self, *args, **kwargs):
        ware_pk = self.kwargs.get('pk')
        response_data = self.get_response_data_template(values_appendix=' zł')
        invoices = Invoice.objects.filter(
            invoiceitem__ware__pk=ware_pk).order_by('date')
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
            created_date__date__gte=date_from,
            created_date__date__lte=date_to).order_by('-created_date')
        response = {'changes': []}
        for change in changes:
            response['changes'].append(
                self.get_change_dict(change))
        return JsonResponse(response)

    def get_change_dict(self, change):
        return {
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
        }


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
            response['invoices'].append(
                self.get_invoice_dict(invoice))
        return JsonResponse(response)

    def get_invoice_dict(self, invoice):
        return {
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
        }


class Metrics(View):
    wares = None
    suppliers = None
    purchase_invoices = None
    sale_invoices = None
    contractors = None
    commissions = None
    weights = None
    ptus = None

    def get(self, *args, **kwargs):
        self.has_permission = False
        if self.request.user.is_superuser:
            self.has_permission = True
        elif self.request.user.groups.filter(name='boss').exists():
            self.has_permission = True

        group = self.request.GET.get('group')
        self.date_from = date_parser.parse(self.request.GET.get('date_from')).date()
        self.date_to = date_parser.parse(self.request.GET.get('date_to')).date()

        if group == 'purchase':
            response = self._get_purchase_metrics()
        elif group == 'sale':
            response = self._get_sale_metrics()
        else:
            return {}
        return JsonResponse(response)

    def _get_purchase_metrics(self):
        response = {
            'ware_count': self.get_wares().count(),
            'supplier_count': self.get_suppliers().count(),
            'invoice_count': self.get_purchase_invoices().count()
        }
        if self.has_permission:
            response.update(self._get_purchase_secret_metrics())
        return response

    def _get_purchase_secret_metrics(self):
        invoices_sum = 0
        if self.get_purchase_invoices():
            invoices_sum = self.get_purchase_invoices().aggregate(
                total=Sum(F('invoiceitem__price') * F('invoiceitem__quantity')))['total']
        return {'invoice_sum': "{0:.2f} zł".format(invoices_sum).replace('.', ',')}

    def _get_sale_metrics(self):
        response = {
            'contractor_count': self.get_contractors().count(),
            'sale_invoice_count': self.get_sale_invoices().count(),
            'commission_count': self.get_commissions().count()
        }
        r134a = 0
        r1234yf = 0
        r12 = 0
        r404 = 0
        if self.get_weights():
            r134a = self.get_weights().aggregate(Sum('r134a'))['r134a__sum']
            r1234yf = self.get_weights().aggregate(Sum('r1234yf'))['r1234yf__sum']
            r12 = self.get_weights().aggregate(Sum('r12'))['r12__sum']
            r404 = self.get_weights().aggregate(Sum('r404'))['r404__sum']
        response['r134a_sum'] = "{} g".format(r134a)
        response['r1234yf_sum'] = "{} g".format(r1234yf)
        response['r12_sum'] = "{} g".format(r12)
        response['r404_sum'] = "{} g".format(r404)

        if self.has_permission:
            response.update(self._get_sale_secret_metrics())
        return response

    def _get_sale_secret_metrics(self):
        invoices_sum = 0
        invoices_sum_brutto = 0
        tax_sum = 0
        person_tax_sum = 0
        if self.get_sale_invoices():
            invoices_sum = self.get_sale_invoices().aggregate(
                Sum('total_value_netto'))['total_value_netto__sum']
            invoices_sum_brutto = self.get_sale_invoices().aggregate(
                Sum('total_value_brutto'))['total_value_brutto__sum']
            tax_sum = self.get_sale_invoices().annotate(
                vat=F('total_value_brutto') - F('total_value_netto')).aggregate(
                    Sum('vat'))['vat__sum']
        person_invoices = self.get_sale_invoices().filter(contractor__nip=None)
        if person_invoices:
            person_tax_sum = person_invoices.annotate(
                vat=F('total_value_brutto') - F('total_value_netto')).aggregate(
                    Sum('vat'))['vat__sum']
        response = {}
        response['sale_invoice_sum'] = "{0:.2f} zł".format(invoices_sum).replace('.', ',')
        response['sale_invoice_sum_brutto'] = "{0:.2f} zł".format(invoices_sum_brutto).replace('.', ',')
        response['vat_sum'] = "{0:.2f} zł".format(tax_sum).replace('.', ',')
        response['person_vat_sum'] = "{0:.2f} zł".format(person_tax_sum).replace('.', ',')
        response['company_vat_sum'] = "{0:.2f} zł".format(tax_sum - person_tax_sum).replace('.', ',')

        ptu_sum = 0
        if self.get_ptus():
            ptu_sum = self.get_ptus().aggregate(Sum('value'))['value__sum']
        response['ptu_sum'] = "{0:.2f} zł".format(ptu_sum).replace('.', ',')

        commissions_sum = 0
        if self.get_commissions():
            commissions_sum = self.get_commissions().aggregate(Sum('value'))['value__sum']
        response['commission_sum'] = "{0:.2f} zł".format(commissions_sum).replace('.', ',')
        return response

    def get_wares(self):
        if self.wares is not None:
            return self.wares
        self.wares = Ware.objects.filter(
            created_date__date__gte=self.date_from,
            created_date__date__lte=self.date_to)
        return self.wares

    def get_suppliers(self):
        if self.suppliers is not None:
            return self.suppliers
        self.suppliers = Supplier.objects.filter(
                created_date__date__gte=self.date_from,
                created_date__date__lte=self.date_to)
        return self.suppliers

    def get_purchase_invoices(self):
        if self.purchase_invoices is not None:
            return self.purchase_invoices
        self.purchase_invoices = Invoice.objects.filter(
            date__gte=self.date_from,
            date__lte=self.date_to)
        return self.purchase_invoices

    def get_contractors(self):
        if self.contractors is not None:
            return self.contractors
        self.contractors = Contractor.objects.filter(
                created_date__date__gte=self.date_from,
                created_date__date__lte=self.date_to)
        return self.contractors

    def get_weights(self):
        if self.weights is not None:
            return self.weights
        self.weights = RefrigerantWeights.objects.filter(
            sale_invoice__issue_date__gte=self.date_from,
            sale_invoice__issue_date__lte=self.date_to)
        return self.weights

    def get_sale_invoices(self):
        if self.sale_invoices is not None:
            return self.sale_invoices
        self.sale_invoices = SaleInvoice.objects.filter(
                issue_date__gte=self.date_from,
                issue_date__lte=self.date_to).exclude(
                    invoice_type__in=[
                        SaleInvoice.TYPE_PRO_FORMA,
                        SaleInvoice.TYPE_CORRECTIVE,
                        SaleInvoice.TYPE_WDT_PRO_FORMA])
        return self.sale_invoices

    def get_commissions(self):
        if self.commissions is not None:
            return self.commissions
        self.commissions = Commission.objects.filter(
                end_date__gte=self.date_from,
                end_date__lte=self.date_to,
                status=Commission.DONE)
        return self.commissions

    def get_ptus(self):
        if self.ptus is not None:
            return self.ptus
        self.ptus = ReceiptPTU.objects.filter(
            date__gte=self.date_from,
            date__lte=self.date_to)
        return self.ptus


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
