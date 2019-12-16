import requests
import datetime

from bs4 import BeautifulSoup
from dateutil import rrule, parser as date_parser

from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from django.db.models import Q

from KlimaKar.settings import ZATOKA_LOGIN, ZATOKA_PASSWORD, ZATOKA_PK
from apps.warehouse.models import Invoice, Ware, InvoiceItem, Supplier
from apps.warehouse.functions import check_ware_price_changes


class Command(BaseCommand):
    help = 'Loads invoices from Auto-Zatoka'

    def add_arguments(self, parser):
        parser.add_argument('date_from', nargs='?',
                            default=(datetime.date.today() - datetime.timedelta(7)).strftime('%Y-%m-%d'))
        parser.add_argument('date_to', nargs='?',
                            default=(datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'))

    def handle(self, *args, **options):
        date_from = date_parser.parse(options['date_from']).date().replace(day=1)
        date_to = date_parser.parse(options['date_to']).date()
        month_dates = list(rrule.rrule(rrule.MONTHLY, bymonthday=1, dtstart=date_from, until=date_to))
        with requests.Session() as s:
            url = 'https://auto-zatoka.webterminal.com.pl/login'
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                               ' Chrome/75.0.3770.80 Safari/537.36')
            }
            ajax_headers = {'X-Requested-With': 'XMLHttpRequest'}
            r = s.get(url, headers=headers)
            if r.status_code != 200:
                message = "Initial get invalid.\n{}".format(r.content)
                print(message)
                self.report_admins(message)
                return

            soup = BeautifulSoup(r.content, 'html5lib')
            data = {
                '_csrf_token': soup.find('input', attrs={'name': '_csrf_token'})['value'],
                '_username': ZATOKA_LOGIN,
                '_password': ZATOKA_PASSWORD,
            }
            url = 'https://auto-zatoka.webterminal.com.pl/login_check'
            r = s.post(url, data=data, headers=headers)
            if r.status_code != 200:
                message = "Login invalid.\n{}".format(r.content)
                print(message)
                self.report_admins(message)
                return

            new_invoices = 0
            new_wares = 0
            for date in month_dates:
                url = 'https://auto-zatoka.webterminal.com.pl/documents/invoices/{}'.format(date.strftime('%Y-%m-%d'))
                r = s.get(url, params={'page': 1}, headers=ajax_headers)
                if r.status_code != 200:
                    message = "Get invoices failed.\n{}".format(r.text)
                    print(message)
                    self.report_admins(message)
                    return

                for invoice in r.json().get('data', []):
                    number = invoice['number']
                    if number and not Invoice.objects.filter(number=number, supplier__pk=ZATOKA_PK).exists():
                        issue_date = invoice['created']
                        value_netto = invoice['netto']
                        invoice_id = invoice['id']
                        url = 'https://auto-zatoka.webterminal.com.pl/documents/invoice/{}/positions'.format(invoice_id)
                        r = s.get(url, headers=ajax_headers)
                        result = self.parse_invoice(r.content, number, issue_date, value_netto)
                        new_invoices = new_invoices + result[0]
                        new_wares = new_wares + result[1]

            print("Added {} new invoices.". format(new_invoices))
            print("Added {} new wares.\n". format(new_wares))

    def parse_invoice(self, html_content, number, issue_date, value_netto):
        soup = BeautifulSoup(html_content, 'html5lib')

        invoice = Invoice.objects.create(
            number=number,
            date=issue_date,
            supplier=Supplier.objects.get(pk=ZATOKA_PK)
        )

        new_wares = 0
        for row in soup.find_all('tr', {'class': 'mod-list-item'}):
            cells = row.find_all('td')
            price = float(cells[5].find(text=True, recursive=False).strip().replace(',', '.'))
            quantity = cells[3].text.strip()
            index = cells[1].text.strip()
            name = cells[2].text.strip()
            if not index:
                print("Skipped ware without index.")
                self.report_admins('Invalid data in invoice {}. Please verify.'.format(number))
                continue
            try:
                ware = Ware.objects.get(Q(index=index) | Q(index_slug=Ware.slugify(index)))
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
        mail_admins('GORDON invoice download failed!', message)
