from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from KlimaKar import settings
from apps.warehouse.models import WarePriceChange


class Command(BaseCommand):
    help = 'Deletes old price changes alerts'

    def handle(self, *args, **options):
        WarePriceChange.objects.filter(created_date__gte=datetime.now()-timedelta(
            days=settings.PRICE_CHANGE_DAYS)).delete()
        print("Deleted old ware price changes alerts")
