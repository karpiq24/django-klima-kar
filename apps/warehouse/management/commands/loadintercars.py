import requests
import datetime
import dateutil.parser
import xml.dom.minidom

from django.core.management.base import BaseCommand

from apps.warehouse.models import Invoice, InvoiceItem, Supplier, Ware
from KlimaKar.settings import IC_CLIENT_NUMBER, IC_TOKEN, IC_API_URL


class Command(BaseCommand):
    help = 'Loads invoices from Inter Cars API'

    def add_arguments(self, parser):
        parser.add_argument('date')

    def handle(self, *args, **options):
        try:
            start_date = dateutil.parser.parse(options['date'])
        except ValueError:
            print("Invalid date format.")
            return

        if not IC_CLIENT_NUMBER:
            print("Inter Cars client number is not specified.")
            return
        if not IC_TOKEN:
            print("Inter Cars client number is not specified.")
            return

        today = datetime.datetime.today()
        current_date = start_date
        new_invoices = 0
        new_wares = 0

        for end_date in month_year_iter(start_date, today):
            new_objects = self.get_invoices(current_date, end_date)
            new_invoices += new_objects[0]
            new_wares += new_objects[1]
            current_date = end_date + datetime.timedelta(1)
        print("Added {} new invoices.". format(new_invoices))
        print("Added {} new wares.". format(new_wares))

    def get_invoices(self, current_date, end_date):
        url = IC_API_URL + 'GetInvoices'
        params = {
            'from': current_date.strftime('%Y%m%d'),
            'to': end_date.strftime('%Y%m%d')
        }
        headers = {'kh_kod': IC_CLIENT_NUMBER, 'token': IC_TOKEN}
        r = requests.get(url, params=params, headers=headers)
        DOMTree = xml.dom.minidom.parseString(r.text)
        collection = DOMTree.documentElement
        invoices = collection.getElementsByTagName("nag")
        new_invoices = 0
        new_wares = 0

        for invoice in invoices:
            invoice_id = getData(invoice, 'id')
            invoice_number = getData(invoice, 'numer')
            invoice_date = dateutil.parser.parse(getData(invoice, 'dat_w'))
            try:
                Invoice.objects.get(number=invoice_number)
                continue
            except Invoice.DoesNotExist:
                new_invoices += 1
                invoice_obj = Invoice.objects.create(
                    date=invoice_date.date(),
                    number=invoice_number,
                    supplier=Supplier.objects.get(name="Inter Cars")
                )
                new_wares += self.get_invoice_detail(invoice_obj, invoice_id)
        return (new_invoices, new_wares)

    def get_invoice_detail(self, invoice_obj, invoice_id):
        url = IC_API_URL + 'GetInvoice'
        params = {'id': invoice_id}
        headers = {'kh_kod': IC_CLIENT_NUMBER, 'token': IC_TOKEN}
        r = requests.get(url, params=params, headers=headers)
        DOMTree = xml.dom.minidom.parseString(r.text)
        collection = DOMTree.documentElement
        wares = collection.getElementsByTagName("poz")
        new_wares = 0

        for ware in wares:
            try:
                ware_obj = Ware.objects.get(index=getData(ware, 'indeks'))
            except Ware.DoesNotExist:
                ware_obj = Ware.objects.create(
                    index=getData(ware, 'indeks'),
                    name=getData(ware, 'nazwa'),
                    description=getData(ware, 'opis'))
                new_wares += 1
            InvoiceItem.objects.create(
                invoice=invoice_obj,
                ware=ware_obj,
                quantity=getData(ware, 'ilosc'),
                price=getData(ware, 'cena')
            )
        invoice_obj.calculate_total_value()
        return new_wares


def month_year_iter(start_date, end_date):
    for n in last_range(30, int((end_date - start_date).days), 30):
        yield start_date + datetime.timedelta(n)


def last_range(start, end, step):
    i = start
    while i < end:
        yield i
        i += step
    yield end


def getData(node, tag):
    if node.getElementsByTagName(tag)[0].childNodes != []:
        return node.getElementsByTagName(tag)[0].childNodes[0].nodeValue
    else:
        return None
