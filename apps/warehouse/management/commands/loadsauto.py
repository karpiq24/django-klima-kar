import dateutil.parser
import requests
import datetime

from bs4 import BeautifulSoup
from xml.dom.minidom import parseString

from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from django.db.models import Q

from KlimaKar.settings import SAUTO_LOGIN, SAUTO_PASSWORD
from apps.warehouse.models import Invoice, Ware, InvoiceItem, Supplier
from apps.warehouse.functions import check_ware_price_changes


class Command(BaseCommand):
    help = 'Loads invoices from S-AUTO'

    def add_arguments(self, parser):
        parser.add_argument('date_from', nargs='?',
                            default=(datetime.date.today() - datetime.timedelta(7)).strftime('%Y-%m-%d'))
        parser.add_argument('date_to', nargs='?',
                            default=(datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'))

    def handle(self, *args, **options):
        with requests.Session() as s:
            url = 'https://s-auto.profiauto.net/Uzt/Login'
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                               ' Chrome/75.0.3770.80 Safari/537.36')
            }
            data = {
                "Login": SAUTO_LOGIN,
                'Haslo': SAUTO_PASSWORD
            }
            r = s.post(url, headers=headers, data=data)
            if r.status_code != 200:
                message = "Initial get invalid.\n{}".format(r.content)
                print(message)
                self.report_admins(message)
                return

            url = 'https://s-auto.profiauto.net/klient/faktury'
            data = {
                'status': '---',
                'from':	options['date_from'],
                'to': options['date_to'],
                'page': '0',
                'sort': 'date',
                'kr': 'desc'
            }
            r = s.get(url, headers=headers, data=data)
            if r.status_code != 200:
                message = "Get invoices failed.\n{}".format(r.text)
                print(message)
                self.report_admins(message)
                return

            soup = BeautifulSoup(r.content, 'html5lib')
            new_invoices = 0
            new_wares = 0
            for row in soup.find('tbody').find_all('tr'):
                number = row.find_all('td')[1].find('a').text.strip()
                if number and not Invoice.objects.filter(number=number).exists():
                    invoice_id = row.find('a')['href'].split('/')[-1]
                    url = 'https://s-auto.profiauto.net/Klient/faktury/EksportXML/{}'.format(invoice_id)
                    r = s.get(url, headers=headers)
                    result = self.parse_invoice(r.text)
                    new_invoices = new_invoices + result[0]
                    new_wares = new_wares + result[1]
            print("Added {} new invoices.". format(new_invoices))
            print("Added {} new wares.\n". format(new_wares))

    def parse_invoice(self, xml_string):
        xml_doc = parseString(xml_string).documentElement
        invoice_xml = xml_doc.getElementsByTagName('nag')[0]
        number = self.getData(invoice_xml, 'numer')
        issue_date = dateutil.parser.parse(self.getData(invoice_xml, 'dat_w')).date()
        netto_price = float(self.getData(invoice_xml, 'war_n'))

        try:
            Invoice.objects.get(number=number)
            return 0, 0
        except Invoice.DoesNotExist:
            invoice = Invoice.objects.create(
                number=number,
                date=issue_date,
                supplier=Supplier.objects.get(name="S-auto"),
                total_value=netto_price
            )

        new_wares = 0
        for item in xml_doc.getElementsByTagName('poz'):
            price = float(self.getData(item, 'cena'))
            quantity = int(self.getData(item, 'ilosc'))
            index = self.getData(item, 'tow_kod').strip()
            name = self.getData(item, 'nazwa').strip().capitalize()
            description = self.getData(item, 'opis')
            if description:
                description = description.strip()
            else:
                description = ''
            if not index:
                print("Skipped ware without index.")
                self.report_admins('Invalid data in invoice {}. Please verify.'.format(number))
                continue
            try:
                ware = Ware.objects.get(Q(index=index) | Q(index_slug=Ware.slugify(index)))
            except Ware.DoesNotExist:
                ware = Ware.objects.create(index=index, name=name, description=description)
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
        mail_admins('S-AUTO invoice download failed!', message)

    def getData(self, node, tag):
        if node.getElementsByTagName(tag)[0].childNodes != []:
            return node.getElementsByTagName(tag)[0].childNodes[0].nodeValue
        else:
            return None
