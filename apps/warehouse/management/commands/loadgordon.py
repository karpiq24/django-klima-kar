import requests
import datetime

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.db.models import Q

from KlimaKar.settings import GORDON_LOGIN, GORDON_PASSWORD, GORDON_PK
from KlimaKar.email import mail_admins
from apps.warehouse.models import Invoice, Ware, InvoiceItem, Supplier


class Command(BaseCommand):
    help = 'Loads invoices from GORDON'

    def add_arguments(self, parser):
        parser.add_argument('date_from', nargs='?',
                            default=(datetime.date.today() - datetime.timedelta(7)).strftime('%Y-%m-%d'))
        parser.add_argument('date_to', nargs='?',
                            default=(datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'))

    def handle(self, *args, **options):
        with requests.Session() as s:
            url = 'http://katalog.gordon.com.pl/loginform-gordon.aspx'
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
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                '__EVENTVALIDATION': __EVENTVALIDATION,
                'tbLoginName': GORDON_LOGIN,
                'tbPassword': GORDON_PASSWORD,
                'ctl07': 'ctl08|btnLogin',
                '__ASYNCPOST': 'true',
                'btnLogin': 'Zaloguj się'
            }
            r = s.post(url, data=data, headers=headers)
            if r.status_code != 200:
                message = "Login invalid.\n{}".format(r.content)
                print(message)
                self.report_admins(message)
                return

            url = 'http://katalog.gordon.com.pl/customers/documents.aspx'
            data = {
                'from': options['date_from'],
                'to': options['date_to'],
                'searchID': ''
            }
            r = s.get(url, params=data, headers=headers)
            if r.status_code != 200:
                message = "Get invoices failed.\n{}".format(r.text)
                print(message)
                self.report_admins(message)
                return

            soup = BeautifulSoup(r.content, 'html5lib')
            new_invoices = 0
            new_wares = 0
            for row in soup.find_all('tr', {'class': 'clickable'}):
                number = row.find('td', {'class': 'doc-item-doc-id-col'}).find('a').text.strip()
                date = row.find('td', {'class': 'doc-item-date-create-col'}).text.strip()
                value_netto = float(
                    row.find('td', {'class': 'doc-item-net-col'}).text.strip().split(' ')[0].replace(',', '.'))
                invoice_id = row['data-id'].strip()
                if number and not Invoice.objects.filter(number=number, supplier__pk=GORDON_PK).exists():
                    url = 'http://katalog.gordon.com.pl/customers/documentitems.aspx?id={}'.format(invoice_id)
                    r = s.get(url, headers=headers)
                    result = self.parse_invoice(r.content, number, date, value_netto)
                    new_invoices = new_invoices + result[0]
                    new_wares = new_wares + result[1]
            print("Added {} new invoices.". format(new_invoices))
            print("Added {} new wares.\n". format(new_wares))

    def parse_invoice(self, html_content, number, issue_date, value_netto):
        soup = BeautifulSoup(html_content, 'html5lib')

        invoice = Invoice.objects.create(
            number=number,
            date=issue_date,
            supplier=Supplier.objects.get(pk=GORDON_PK)
        )

        new_wares = 0
        for row in soup.find_all('tr', {'class': 'dgriditem'}) + soup.find_all('tr', {'class': 'dgridaltitem'}):
            cells = row.find_all('td')
            price = float(cells[4].text.strip().split(' ')[0].replace(',', '.'))
            quantity = cells[2].text.strip()
            index = cells[0].text.strip()
            name = cells[1].text.strip()
            if not index:
                print("Skipped ware without index.")
                self.report_admins('Invalid data in invoice {}. Please verify.'.format(number))
                continue
            try:
                index_split = index.split(' ')
                index2 = '{} {}'.format(index_split[-1], ' '.join(index_split[:-1])).strip()
                index3 = ' '.join(index_split[:-1])
                ware = Ware.objects.get(
                    Q(index=index) | Q(index_slug=Ware.slugify(index)) |
                    Q(index=index2) | Q(index_slug=Ware.slugify(index2)) |
                    Q(index=index3) | Q(index_slug=Ware.slugify(index3)))
            except Ware.DoesNotExist:
                ware = Ware.objects.create(index=index2, name=name)
                new_wares = new_wares + 1

            InvoiceItem.objects.create(
                invoice=invoice,
                ware=ware,
                quantity=quantity,
                price=price
            )

        invoice.check_ware_price_changes()
        return 1, new_wares

    def report_admins(self, message):
        mail_admins('GORDON invoice download failed!', message)
