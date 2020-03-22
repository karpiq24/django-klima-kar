from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.warehouse.models import Ware


class Command(BaseCommand):
    help = "Export retail prices"

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("output")

    def handle(self, *args, **options):
        with open(options["path"]) as f:
            lines = f.readlines()
        with open(options["output"], "w") as o:
            for line in lines:
                index = line.strip()
                ware = Ware.objects.get(
                    Q(index=index) | Q(index_slug=Ware.slugify(index))
                )
                o.write(f"{index},{ware.retail_price}\n")
