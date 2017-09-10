from django.core.management.base import BaseCommand
from apps.warehouse.models import Supplier

import xml.dom.minidom


class Command(BaseCommand):
    help = 'Loads xml file with wares data'

    def add_arguments(self, parser):
        parser.add_argument('xml_file', type=str)

    def handle(self, *args, **options):
        try:
            DOMTree = xml.dom.minidom.parse(options['xml_file'])
            collection = DOMTree.documentElement

            suppliers = collection.getElementsByTagName("string")

            for supplier in suppliers:
                try:
                    s = Supplier.objects.get(
                        name=supplier.childNodes[0].nodeValue)
                    print(s.name + " already exists.")
                except Supplier.DoesNotExist:
                    s = Supplier(
                            name=supplier.childNodes[0].nodeValue)
                    s.save()
                    print(s.name + " added to database.")

        except Exception as e:
            print(e)
        finally:
            print("Success")
