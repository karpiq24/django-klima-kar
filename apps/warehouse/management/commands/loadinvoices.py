from django.core.management.base import BaseCommand
from apps.warehouse.models import Invoice, InvoiceItem, Supplier, Ware

import xml.dom.minidom


class Command(BaseCommand):
    help = 'Loads xml file with wares data'

    def add_arguments(self, parser):
        parser.add_argument('xml_file', type=str)

    def handle(self, *args, **options):
        try:
            DOMTree = xml.dom.minidom.parse(options['xml_file'])
            collection = DOMTree.documentElement

            invoices = collection.getElementsByTagName("faktura")

            for invoice in invoices:
                supplier = Supplier.objects.get(
                    name=self.getData(invoice, "dostawca"))
                try:
                    i = Invoice.objects.get(
                        number=self.getData(invoice, "nr_faktury"),
                        supplier=supplier)
                    print(i.number + " already exists.")
                except Invoice.DoesNotExist:
                    i = Invoice(
                        date=self.getData(
                            invoice, "data").split('T', 1)[0],
                        number=self.getData(invoice, "nr_faktury"),
                        supplier=supplier,
                        total_value=self.getData(invoice, "wartosc"))
                    i.save()

                    items = invoice.getElementsByTagName(
                        "przedmioty")[0].getElementsByTagName("rzecz")

                    total_value = 0
                    for item in items:
                        ware = Ware.objects.get(
                            index=self.getData(item, "indeks"))
                        x = InvoiceItem(
                            invoice=i,
                            ware=ware,
                            quantity=self.getData(item, "ile"),
                            price=self.getData(item, "cena"))
                        x.save()
                        total_value += int(x.quantity) * float(x.price)
                        i.total_value = total_value
                        i.save()

                    print(i.number + " added to database.")

        except Exception as e:
            print(e)
        finally:
            print("Success")

    def getData(self, node, tag):
        if node.getElementsByTagName(tag)[0].childNodes != []:
            return node.getElementsByTagName(tag)[0].childNodes[0].nodeValue
        else:
            return None
