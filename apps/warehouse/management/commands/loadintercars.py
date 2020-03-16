import requests
import datetime
import dateutil.parser
import xml.dom.minidom

from django.core.management.base import BaseCommand
from django.urls import reverse

from apps.warehouse.models import Invoice, InvoiceItem, Ware
from apps.settings.models import InvoiceDownloadSettings
from KlimaKar.settings import IC_API_URL, ABSOLUTE_URL
from KlimaKar.templatetags.slugify import slugify
from KlimaKar.email import mail_managers, mail_admins


class Command(BaseCommand):
    help = 'Loads invoices from Inter Cars API'

    def add_arguments(self, parser):
        parser.add_argument('date_from', nargs='?',
                            default=(datetime.date.today() - datetime.timedelta(7)).strftime('%Y-%m-%d'))
        parser.add_argument('date_to', nargs='?',
                            default=(datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'))

    def handle(self, *args, **options):
        self.settings = InvoiceDownloadSettings.load()
        try:
            date_from = dateutil.parser.parse(options['date_from'])
            date_to = dateutil.parser.parse(options['date_to'])
            print("Loading invoices from date: {} to: {}".format(
                options['date_from'], options['date_to']))
        except ValueError:
            print("Invalid date format.\n")
            return

        current_date = date_from
        new_invoices = 0
        new_wares = 0

        for end_date in month_year_iter(date_from, date_to):
            print(current_date, end_date)
            new_objects = self.get_invoices(current_date, end_date)
            new_invoices += new_objects[0]
            new_wares += new_objects[1]
            current_date = end_date + datetime.timedelta(1)
        print("Added {} new invoices.". format(new_invoices))
        print("Added {} new wares.\n". format(new_wares))

    def get_invoices(self, current_date, end_date):
        url = IC_API_URL + 'GetInvoices'
        params = {
            'from': current_date.strftime('%Y%m%d'),
            'to': end_date.strftime('%Y%m%d')
        }
        headers = {'kh_kod': self.settings.INTER_CARS_CLIENT_NUMBER,
                   'token': self.settings.INTER_CARS_TOKEN}
        r = requests.get(url, params=params, headers=headers)
        if r.status_code != 200:
            report_admins('Invoice list download failed.\n{}'.format(r.text))
        DOMTree = xml.dom.minidom.parseString(r.text)
        collection = DOMTree.documentElement
        invoices = collection.getElementsByTagName("nag")
        new_invoices = 0
        new_wares = 0

        for invoice in invoices:
            invoice_id = getData(invoice, 'id')
            invoice_number = getData(invoice, 'numer')
            invoice_total = float(getData(invoice, 'war_n'))
            invoice_date = dateutil.parser.parse(getData(invoice, 'dat_w'))
            try:
                Invoice.objects.get(number=invoice_number,
                                    supplier=self.settings.INTER_CARS_SUPPLIER)
                continue
            except Invoice.DoesNotExist:
                new_invoices += 1
                invoice_obj = Invoice.objects.create(
                    date=invoice_date.date(),
                    number=invoice_number,
                    supplier=self.settings.INTER_CARS_SUPPLIER
                )
                new_wares += self.get_invoice_detail(invoice_obj, invoice_id)
                self.check_total_price(invoice_obj, invoice_total)
                invoice_obj.check_ware_price_changes()
        return (new_invoices, new_wares)

    def get_invoice_detail(self, invoice_obj, invoice_id):
        url = IC_API_URL + 'GetInvoice'
        params = {'id': invoice_id}
        headers = {'kh_kod': self.settings.INTER_CARS_CLIENT_NUMBER,
                   'token': self.settings.INTER_CARS_TOKEN}
        r = requests.get(url, params=params, headers=headers)
        if r.status_code != 200:
            report_admins('Invoice {} details download failed.\n{}'.format(
                invoice_obj.number, r.text))
        DOMTree = xml.dom.minidom.parseString(r.text)
        collection = DOMTree.documentElement
        wares = collection.getElementsByTagName("poz")
        new_wares = 0

        for ware in wares:
            if not getData(ware, 'indeks') or not getData(ware, 'nazwa'):
                report_admins(
                    'Invalid data in invoice {}. Please verify.'.format(invoice_obj.number))
                continue
            try:
                ware_obj = Ware.objects.get(index=getData(ware, 'indeks'))
            except Ware.DoesNotExist:
                ware_obj = Ware.objects.filter(
                    index_slug=getData(ware, 'indeks')).first()
                if not ware_obj:
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
        return new_wares

    def check_total_price(self, invoice, total):
        if invoice.total_value == total:
            return
        if invoice.total_value == -total:
            for item in invoice.invoiceitem_set.all():
                item.quantity = -item.quantity
                item.save()
        else:
            mail_managers(
                'Błąd w fakturze Inter Cars',
                'Kwota całkowita faktury nie zgadza się z cenami pozycji. Proszę o sprawdzenie.\n\n{}{}'.format(
                    ABSOLUTE_URL,
                    reverse(
                        'warehouse:invoice_detail',
                        kwargs={
                            'pk': invoice.pk,
                            'slug': slugify(invoice)
                        })))


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


def report_admins(message):
    mail_admins('Inter Cars invoice download failed!', message)
