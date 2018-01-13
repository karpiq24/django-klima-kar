import datetime

from dateutil.relativedelta import relativedelta

from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Sum

from apps.warehouse.models import Supplier, Invoice, Ware
from apps.stats.functions import get_random_colors


class SupplierAllInvoicesValue(View):
    def get(self, *args, **kwargs):
        data = {}
        for supplier in Supplier.objects.all():
            value = supplier.all_invoices_value
            if value:
                data[supplier.name] = supplier.all_invoices_value
        data_ordered = sorted(data.items(), key=lambda kv: kv[1], reverse=True)
        response_data = {
            'labels': [],
            'values': []
        }
        if len(data_ordered) > 6:
            for d in data_ordered[0:5]:
                response_data['labels'].append(d[0])
                response_data['values'].append(d[1])

            total_rest = 0
            for d in data_ordered[5:]:
                total_rest += d[1]
            response_data['labels'].append('Pozostali dostawcy')
            response_data['values'].append(total_rest)
        else:
            for d in data_ordered:
                response_data['labels'].append(d[0])
                response_data['values'].append(d[1])

        response_data['options'] = {
            'type': 'doughnut',
            'colors': get_random_colors(len(response_data['values'])),
            'legend': True
        }
        return JsonResponse(response_data)


class InvoicesValueOverTime(View):
    last_year = False

    def get(self, *args, **kwargs):
        data = {}
        if self.last_year:
            date = (datetime.datetime.now() - relativedelta(years=1, months=1)).replace(day=1)
            invoices = Invoice.objects.filter(date__gte=date).order_by('date')
        else:
            invoices = Invoice.objects.all().order_by('date')

        for invoice in invoices:
            if invoice.date.strftime('%Y-%m') not in data:
                data[invoice.date.strftime('%Y-%m')] = 0
            data[invoice.date.strftime('%Y-%m')] += invoice.total_value
        response_data = {
            'labels': [],
            'values': []
        }
        for key, value in data.items():
            response_data['labels'].append(key)
            response_data['values'].append(value)

        response_data['options'] = {
            'type': 'line',
            'colors': get_random_colors(1),
            'legend': False
        }
        return JsonResponse(response_data)


class WarePurchaseQuantity(View):
    def get(self, *args, **kwargs):
        wares_quantity = Ware.objects.exclude(invoiceitem=None).annotate(
            quantity=Sum('invoiceitem__quantity')).values_list('index', 'quantity').order_by('-quantity')[:10]

        response_data = {
            'labels': list(wares_quantity.values_list('index', flat=True)),
            'values': list(wares_quantity.values_list('quantity', flat=True))
        }

        response_data['options'] = {
            'type': 'pie',
            'colors': get_random_colors(10),
            'legend': True
        }
        return JsonResponse(response_data)
