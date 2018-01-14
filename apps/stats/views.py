import datetime

from dateutil.relativedelta import relativedelta

from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from apps.warehouse.models import Invoice, Ware
from apps.stats.functions import get_random_colors


class SupplierAllInvoicesValue(View):
    max_positions = 8

    def get(self, *args, **kwargs):
        data = Invoice.objects.values('supplier').annotate(
            total=Sum('total_value')).values_list('supplier__name', 'total').order_by('-total')
        if data.count() > self.max_positions:
            index = self.max_positions - 1
        else:
            index = data.count()
        response_data = {
            'labels': list(data[0:index].values_list('supplier__name', flat=True)),
            'values': list(data[0:index].values_list('total', flat=True))
        }
        if data.count() > self.max_positions:
            response_data['labels'].append('Pozostali dostawcy')
            response_data['values'].append(data[self.max_positions - 1:].values(
                'total').aggregate(Sum('total'))['total__sum'])

        response_data['options'] = {
            'type': 'doughnut',
            'colors': get_random_colors(len(response_data['values'])),
            'legend': True
        }
        return JsonResponse(response_data)


class InvoicesValueOverTime(View):
    last_year = False

    def get(self, *args, **kwargs):
        if self.last_year:
            date = (datetime.datetime.now() - relativedelta(years=1, months=1)).replace(day=1)
            invoices = Invoice.objects.filter(date__gte=date)
        else:
            date = (datetime.datetime.now() - relativedelta(years=5, months=1)).replace(day=1)
            invoices = Invoice.objects.filter(date__gte=date)

        invoices = invoices.annotate(month=TruncMonth('date')).values('month').annotate(
            total=Sum('total_value')).values_list('month', 'total').order_by('month')
        response_data = {
            'labels': list(invoices.values_list('month', flat=True)),
            'values': list(invoices.values_list('total', flat=True))
        }

        response_data['options'] = {
            'type': 'line',
            'colors': get_random_colors(1),
            'legend': False
        }
        return JsonResponse(response_data)


class WarePurchaseQuantity(View):
    max_positions = 8

    def get(self, *args, **kwargs):
        wares_quantity = Ware.objects.exclude(invoiceitem=None).annotate(
            quantity=Sum('invoiceitem__quantity')).values_list('index', 'quantity').order_by('-quantity')
        if wares_quantity.count() > self.max_positions:
            wares_quantity = wares_quantity[:self.max_positions]

        response_data = {
            'labels': list(wares_quantity.values_list('index', flat=True)),
            'values': list(wares_quantity.values_list('quantity', flat=True))
        }

        response_data['options'] = {
            'type': 'doughnut',
            'colors': get_random_colors(self.max_positions),
            'legend': True
        }
        return JsonResponse(response_data)
