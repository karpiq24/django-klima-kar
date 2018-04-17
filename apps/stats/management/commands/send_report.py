from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand

from apps.stats.functions import get_report_data


class Command(BaseCommand):
    help = 'Generate and send reports'

    def add_arguments(self, parser):
        parser.add_argument('date_option')

    def handle(self, *args, **options):
        date_option = options['date_option']
        if date_option == 'week':
            date = (datetime.now() - relativedelta(weeks=1)).date()
        elif date_option == 'month':
            date = (datetime.now() - relativedelta(months=1)).date()
        elif date_option == 'year':
            date = (datetime.now() - relativedelta(years=1)).date()

        report_data = get_report_data(date, datetime.now().date())
        print(report_data)
