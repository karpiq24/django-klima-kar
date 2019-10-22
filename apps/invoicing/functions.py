import datetime
import re
import time
import io

from xlsxwriter import Workbook

from apps.invoicing.models import SaleInvoice, Contractor, SaleInvoiceItem, RefrigerantWeights
from apps.invoicing.gus import gus_session


def get_next_invoice_number(invoice_type):
    year = datetime.date.today().year
    invoices = SaleInvoice.objects.filter(invoice_type=invoice_type, number_year=year)
    if invoice_type == '1':
        invoices = (invoices | SaleInvoice.objects.filter(invoice_type='4', number_year=year)).distinct()
    elif invoice_type == '4':
        invoices = (invoices | SaleInvoice.objects.filter(invoice_type='1', number_year=year)).distinct()
    elif invoice_type == '2':
        invoices = (invoices | SaleInvoice.objects.filter(invoice_type='5', number_year=year)).distinct()
    elif invoice_type == '5':
        invoices = (invoices | SaleInvoice.objects.filter(invoice_type='2', number_year=year)).distinct()
    if not invoices.exists():
        return "1/{}".format(year)
    last_number = invoices.order_by('-number_value').first().number_value
    return "{}/{}".format(last_number + 1, year)


def load_legacy_contractors(path):
    with open(path, encoding="utf8") as f:
        content = f.readlines()
    found = []
    not_found = []
    new = 0
    last_request = get_time()
    for line in content:
        match = re.search(r'(\d+-\d+-\d+-\d+)|(\d{5,})', line)
        if match:
            nip = match.group(0)
            nip = nip.replace('-', '')
            if nip == '8991071777':
                continue
            time_passed = get_time() - last_request
            if time_passed < 333:
                time.sleep(0.333 - time_passed / 1000)
            contractor_data = gus_session.get_address(nip=nip)
            last_request = get_time()
            if contractor_data:
                found.append(str(contractor_data))
                try:
                    Contractor.objects.get(nip=nip)
                except Contractor.DoesNotExist:
                    c = Contractor(nip=nip, name=contractor_data['name'],
                                   address_1=contractor_data['street_address'],
                                   postal_code=contractor_data['postal_code'],
                                   city=contractor_data['city'])
                    c.save()
                    new = new + 1
            else:
                not_found.append(nip)

    print("Saving file...")
    with open('contractors_result.txt', 'w') as f:
        f.write("FOUND TOTAL: {}\nNOT FOUND TOTAL: {}\nNEW: {}".format(len(found), len(not_found), new))
        f.write("\n______________________________\n\nNOT FOUND IN GUS:\n")
        for i in not_found:
            f.write(i + '\n')
        f.write("\n______________________________\n\nFOUND:\n")
        for i in found:
            f.write(i + '\n')


def get_time():
    return int(round(time.time() * 1000))


def load_legacy_sale_invoices(path):
    with open(path, encoding="utf8") as f:
        content = f.readlines()
    new = 0
    no_match = []

    contractor, created = Contractor.objects.get_or_create(name='BRAK NAZWY')

    for line in content:
        match = re.search(r'((\d+)\/(\d+)) F (\d{2}-\d{2}-\d{2}) (\d{2}-\d{2}-\d{2}) ([+-]?[0-9]*[,]?[0-9]+) '
                          r'([+-]?[0-9]*[,]?[0-9]+) (.+)', line)
        if match:
            try:
                SaleInvoice.objects.get(invoice_type='1', number=match.group(1))
            except SaleInvoice.DoesNotExist:
                netto = float(match.group(6).replace(',', '.'))
                brutto = float(match.group(7).replace(',', '.'))
                si = SaleInvoice(legacy=True, invoice_type='1', number=match.group(1),
                                 number_value=match.group(2), number_year=match.group(3),
                                 issue_date=datetime.datetime.strptime(match.group(4), '%d-%m-%y').date(),
                                 completion_date=datetime.datetime.strptime(match.group(5), '%d-%m-%y').date(),
                                 total_value_netto=netto, total_value_brutto=brutto, contractor=contractor,
                                 payment_type='1', tax_percent=(23 if int(match.group(3)) >= 2011 else 22))
                si.save()
                item = SaleInvoiceItem(sale_invoice=si, name="???", price_netto=netto, price_brutto=brutto)
                item.save()
                refrigerants = RefrigerantWeights(sale_invoice=si)
                refrigerants.save()
                new = new + 1
        else:
            no_match.append(line)

    print("NO MATCH TOTAL: {}\nNEW: {}".format(len(no_match), new))
    print("\n______________________________\n\nNO MATCH:\n")
    for i in no_match:
        print(i)


def load_legacy_refrigerant_weights(path):
    no_invoice = []
    loaded = 0

    with open(path, encoding="utf8") as f:
        content = f.readlines()

    for line in content:
        match = re.search(r'(\d+\/\d+)\t(\d+)?\t?(\d+)?', line)
        if match:
            try:
                rw = RefrigerantWeights.objects.get(sale_invoice__invoice_type='1', sale_invoice__number=match.group(1))
                rw.r134a = int(match.group(2) or 0)
                rw.r12 = int(match.group(3) or 0)
                rw.save()
                loaded = loaded + 1
            except RefrigerantWeights.DoesNotExist:
                no_invoice.append(line)
                continue

    print("NO INVOICE TOTAL: {}\nLOADED: {}".format(len(no_invoice), loaded))
    print("\n______________________________\n\nNO INVOICE:\n")
    for i in no_invoice:
        print(i)


def generate_refrigerant_weights_report(queryset):
    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    worksheet.freeze_panes(1, 0)
    worksheet.set_row(0, 30)

    bold = workbook.add_format({'bold': True})
    bold_weight = workbook.add_format({'num_format': '#0 "g"', 'bold': True})
    border = workbook.add_format({'border': 1})
    bold_border = workbook.add_format({'border': 1, 'bold': True})
    border_weight = workbook.add_format({'border': 1, 'num_format': '#0 "g"'})
    big_bold = workbook.add_format({'font_size': 22, 'bold': True})
    columns = [
        ('Typ faktury', 15),
        ('Numer', 15),
        ('Data wystawienia', 15),
        ('Kontrahent', 50),
        ('R134a', 10),
        ('R1234yf', 10),
        ('R12', 10),
        ('R404', 10),
    ]

    row = 0
    col = 0

    for column in columns:
        worksheet.write(row, col, column[0], bold_border)
        worksheet.set_column(col, col, column[1])
        col += 1

    row = 1
    col = 0

    for invoice in queryset.order_by('number_year', 'number_value'):
        worksheet.write(row, col, invoice.get_invoice_type_display(), border)
        worksheet.write(row, col + 1, invoice.number, border)
        worksheet.write(row, col + 2, invoice.issue_date.strftime('%d.%m.%Y'), border)
        worksheet.write(row, col + 3, invoice.contractor.name, border)
        worksheet.write(row, col + 4, invoice.refrigerantweights.r134a, border_weight)
        worksheet.write(row, col + 5, invoice.refrigerantweights.r1234yf, border_weight)
        worksheet.write(row, col + 6, invoice.refrigerantweights.r12, border_weight)
        worksheet.write(row, col + 7, invoice.refrigerantweights.r404, border_weight)
        row += 1

    worksheet.write(row + 1, 0, 'SUMA', bold)
    worksheet.write(row + 1, 4, '=SUM(E2:E{})'.format(row), bold_weight)
    worksheet.write(row + 1, 5, '=SUM(F2:F{})'.format(row), bold_weight)
    worksheet.write(row + 1, 6, '=SUM(G2:G{})'.format(row), bold_weight)
    worksheet.write(row + 1, 7, '=SUM(H2:H{})'.format(row), bold_weight)

    worksheet.write(0, 9, 'R134a', big_bold)
    worksheet.write(0, 10, '=E{}'.format(row + 2), big_bold)
    worksheet.set_column(9, 9, 15)
    worksheet.set_column(10, 10, 25)
    worksheet.write(0, 11, 'R1234yf', big_bold)
    worksheet.write(0, 12, '=F{}'.format(row + 2), big_bold)
    worksheet.set_column(11, 11, 15)
    worksheet.set_column(12, 12, 25)
    worksheet.write(0, 13, 'R12', big_bold)
    worksheet.write(0, 14, '=G{}'.format(row + 2), big_bold)
    worksheet.set_column(13, 13, 15)
    worksheet.set_column(14, 14, 25)
    worksheet.write(0, 15, 'R404', big_bold)
    worksheet.write(0, 16, '=H{}'.format(row + 2), big_bold)
    worksheet.set_column(15, 15, 15)
    worksheet.set_column(16, 16, 25)

    workbook.close()
    output.seek(0)
    return output
