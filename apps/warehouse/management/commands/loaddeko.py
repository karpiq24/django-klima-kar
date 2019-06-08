import dateutil.parser
import requests
import datetime

from bs4 import BeautifulSoup
from xml.dom.minidom import parseString

from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from django.db.models import Q

from KlimaKar.settings import DEKO_LOGIN, DEKO_PASSWORD
from apps.warehouse.models import Invoice, Ware, InvoiceItem, Supplier
from apps.warehouse.functions import check_ware_price_changes


class Command(BaseCommand):
    help = 'Loads invoices from DEKO'

    def add_arguments(self, parser):
        parser.add_argument('date_from', nargs='?',
                            default=(datetime.date.today() - datetime.timedelta(7)).strftime('%Y-%m-%d'))
        parser.add_argument('date_to', nargs='?',
                            default=(datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'))

    def handle(self, *args, **options):
        with requests.Session() as s:
            url = 'http://sklep.dekoautoparts.pl/pl'
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                               ' Chrome/75.0.3770.80 Safari/537.36')
            }
            r = s.get(url, headers=headers)
            if r.status_code != 200:
                message = "Initial get invalid.\n{}".format(r.content)
                print(message)
                self.report_admins(message)
                return

            soup = BeautifulSoup(r.content, 'html5lib')
            __VIEWSTATE = soup.find('input', attrs={'name': '__VIEWSTATE'})['value']
            __VIEWSTATEGENERATOR = soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value']
            __EVENTVALIDATION = soup.find('input', attrs={'name': '__EVENTVALIDATION'})['value']
            data = {
                '__EVENTTARGET': 'ctl00$ctl00$BodyContentPlaceHolder$LoginForm$LoginButton',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                '__EVENTVALIDATION': __EVENTVALIDATION,
                'ctl00$ctl00$BodyContentPlaceHolder$LoginForm$Username': DEKO_LOGIN,
                'ctl00$ctl00$BodyContentPlaceHolder$LoginForm$Password': DEKO_PASSWORD,
            }
            r = s.post(url, data=data, headers=headers)
            if r.status_code != 200:
                message = "Login invalid.\n{}".format(r.content)
                print(message)
                self.report_admins(message)
                return

            url = 'http://sklep.dekoautoparts.pl/AjaxWS.svc/GetFilteredInvoices'
            data = {
                'dateFrom': options['date_from'],
                'dateTo': options['date_to'],
                'overdueOnly': False
            }
            r = s.post(url, json=data, headers=headers)
            if r.status_code != 200:
                message = "Get invoices failed.\n{}".format(r.text)
                print(message)
                self.report_admins(message)
                return

            soup = BeautifulSoup(r.json()['d'], 'html5lib')
            new_invoices = 0
            new_wares = 0
            for row in soup.find_all('tr')[1:]:
                number = row.find('td').text.strip()
                invoice_id = row.find('a')['href'].strip().split('/')[-1]
                if number and not Invoice.objects.filter(number=number).exists():
                    url = 'http://sklep.dekoautoparts.pl/Download.ashx?type=4&id={}&typedoc=1'.format(invoice_id)
                    r = s.get(url, headers=headers)
                    result = self.parse_invoice(r.text)
                    new_invoices = new_invoices + result[0]
                    new_wares = new_wares + result[1]
            print("Added {} new invoices.". format(new_invoices))
            print("Added {} new wares.\n". format(new_wares))

    def parse_invoice(self, xml_string):
        xml_invoice = parseString(xml_string).documentElement.getElementsByTagName('Invoice')[0]
        number = xml_invoice.getAttribute('Number')
        issue_date = dateutil.parser.parse(xml_invoice.getAttribute('IssueDate'), dayfirst=True).date()
        netto_price = float(xml_invoice.getAttribute('Price').replace(',', '.'))

        try:
            Invoice.objects.get(number=number)
            return 0, 0
        except Invoice.DoesNotExist:
            invoice = Invoice.objects.create(
                number=number,
                date=issue_date,
                supplier=Supplier.objects.get(name="DEKO"),
                total_value=netto_price
            )
        new_wares = 0
        for item in xml_invoice.getElementsByTagName('Item'):
            price = float(item.getAttribute('PerPiecePrice').replace(',', '.'))
            quantity = int(item.getAttribute('Amount'))
            index = item.getAttribute('GroupCode').strip()
            name = item.getAttribute('Name').strip().capitalize()
            if not index:
                print("Skipped ware without index.")
                self.report_admins('Invalid data in invoice {}. Please verify.'.format(number))
                continue
            try:
                ware = Ware.objects.get(Q(index=index) | Q(index_slug=Ware.slugify(index)))
            except Ware.DoesNotExist:
                try:
                    index2 = '{}{}'.format(item.getAttribute('Manufacturer').strip(), index)
                    ware = Ware.objects.get(Q(index=index2) | Q(index_slug=Ware.slugify(index2)))
                except Ware.DoesNotExist:
                    ware = Ware.objects.create(index=index, name=name)
                    new_wares = new_wares + 1
            InvoiceItem.objects.create(
                invoice=invoice,
                ware=ware,
                quantity=quantity,
                price=price
            )
        check_ware_price_changes(invoice)
        return 1, new_wares

    def report_admins(self, message):
        mail_admins('DEKO invoice download failed!', message)
