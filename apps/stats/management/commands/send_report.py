from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from KlimaKar import settings
from apps.stats.functions import get_report_data


class Command(BaseCommand):
    help = 'Generate and send reports'

    def add_arguments(self, parser):
        parser.add_argument('date_option')

    def handle(self, *args, **options):
        date_option = options['date_option']
        date_to = datetime.now().date()
        if date_option == 'week':
            date_from = (date_to - relativedelta(weeks=1))
            title = 'Raport tygodniowy'
        elif date_option == 'month':
            date_from = (date_to - relativedelta(months=1))
            title = 'Raport miesięczny'
        elif date_option == 'year':
            date_from = (date_to - relativedelta(years=1))
            title = 'Raport roczny'
        else:
            print("Invalid date option (allowed are: 'week', 'month', 'year').")
            return

        report_data = get_report_data(date_from, date_to)
        report_data['title'] = title
        report_data['date_from'] = date_from
        report_data['date_to'] = date_to

        template = get_template('stats/report.html')
        content = template.render(report_data)
        email = EmailMultiAlternatives(
            subject="Klima-Kar: {}".format(title),
            body="Twój klient poczty nie wspiera wiadomości HTML",
            to=settings.REPORT_EMAILS
        )
        email.attach_alternative(content, "text/html")
        print(email.send(fail_silently=False))
