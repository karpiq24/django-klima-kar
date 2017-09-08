from django.core.management.base import BaseCommand
from apps.warehouse.models import Ware

import xml.dom.minidom


class Command(BaseCommand):
    help = 'Loads xml file with wares data'

    def add_arguments(self, parser):
        parser.add_argument('xml_file', type=str)

    def handle(self, *args, **options):
            try:
                DOMTree = xml.dom.minidom.parse(options['xml_file'])
                collection = DOMTree.documentElement

                wares = collection.getElementsByTagName("towar")

                for ware in wares:
                    try:
                        w = Ware.objects.get(
                            index=self.getData(ware, "indeks"))
                        print(w.index + " already exists.")
                    except Ware.DoesNotExist:
                        w = Ware(
                            index=self.getData(ware, "indeks"),
                            name=self.getData(ware, "nazwa"),
                            description=self.getData(ware, "uwagi"),
                            stock=self.getData(ware, "stan"),
                        )
                        w.save()
                        print(w.index + " added to database.")

            except Exception as e:
                print(e)
            finally:
                print("Success")

    def getData(self, node, tag):
        if node.getElementsByTagName(tag)[0].childNodes != []:
            return node.getElementsByTagName(tag)[0].childNodes[0].nodeValue
        else:
            return None
