import datetime

from apps.invoicing.models import SaleInvoice


def get_next_invoice_number(invoice_type):
    year = datetime.date.today().year
    invoices = SaleInvoice.objects.filter(invoice_type=invoice_type, number_year=year)
    if not invoices.exists():
        return "1/{}".format(year)
    last_number = invoices.order_by('-number_value').first().number_value
    return "{}/{}".format(last_number + 1, year)
