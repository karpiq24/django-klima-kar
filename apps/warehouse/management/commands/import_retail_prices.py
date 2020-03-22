from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.warehouse.models import Ware


class Command(BaseCommand):
    help = "Import retail prices"

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        with open(options["path"]) as f:
            lines = f.readlines()
        for line in lines:
            index, price = line.split(",")
            index = line.strip()
            try:
                price = float(price)
            except ValueError:
                print(index)
                continue
            ware = Ware.objects.get(Q(index=index) | Q(index_slug=Ware.slugify(index)))
            ware.retail_price = price
            ware.save()
