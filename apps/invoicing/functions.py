import datetime
import re
import time

from apps.invoicing.models import SaleInvoice, Contractor
from apps.invoicing.gus import gus_session


def get_next_invoice_number(invoice_type):
    year = datetime.date.today().year
    invoices = SaleInvoice.objects.filter(invoice_type=invoice_type, number_year=year)
    if not invoices.exists():
        return "1/{}".format(year)
    last_number = invoices.order_by('-number_value').first().number_value
    return "{}/{}".format(last_number + 1, year)


def load_contractors_from_file(path):
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