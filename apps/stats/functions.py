from apps.warehouse.models import WarePriceChange, Invoice, Ware, Supplier
from apps.invoicing.models import SaleInvoice, Contractor


def get_report_data(date_from, date_to):
    report_data = {
        'wares': Ware.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
        'ware_price_changes': WarePriceChange.objects.filter(created_date__date__gte=date_from,
                                                             created_date__date__lte=date_to),
        'suppliers': Supplier.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
        'purchase_invoices': Invoice.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
        'contractors': Contractor.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
        'sale_invoices': SaleInvoice.objects.filter(created_date__date__gte=date_from, created_date__date__lte=date_to),
    }
    return report_data
