from django.db.models import Sum

from apps.warehouse.models import WarePriceChange, Invoice, Ware, Supplier
from apps.invoicing.models import SaleInvoice, Contractor


def get_report_data(date_from, date_to, price_change_limit):
    report_data = {
        'wares': Ware.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
        'ware_price_changes': WarePriceChange.objects.filter(created_date__date__gte=date_from,
                                                             created_date__date__lte=date_to),
        'suppliers': Supplier.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
        'purchase_invoices': Invoice.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
        'contractors': Contractor.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
        'sale_invoices': SaleInvoice.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
    }
    report_data['ware_price_changes'] = [
        obj for obj in report_data['ware_price_changes'] if obj.percent_change(absolute=True) >= price_change_limit]
    report_data['metrics'] = {
        'purchase_invoices': "{0:.2f} zł".format(
            report_data['purchase_invoices'].total()).replace('.', ','),
        'sale_invoices': "{0:.2f} zł".format(
            report_data['sale_invoices'].total(price_type='brutto')).replace('.', ','),
        'r134a': "{} g".format(
            report_data['sale_invoices'].aggregate(
                Sum('refrigerantweights__r134a'))['refrigerantweights__r134a__sum'] or 0),
        'r1234yf': "{} g".format(
            report_data['sale_invoices'].aggregate(
                Sum('refrigerantweights__r1234yf'))['refrigerantweights__r1234yf__sum'] or 0),
        'r12': "{} g".format(
            report_data['sale_invoices'].aggregate(
                Sum('refrigerantweights__r12'))['refrigerantweights__r12__sum'] or 0),
        'r404': "{} g".format(
            report_data['sale_invoices'].aggregate(
                Sum('refrigerantweights__r404'))['refrigerantweights__r404__sum'] or 0),
    }
    return report_data
