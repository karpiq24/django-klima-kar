from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser

from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from KlimaKar import settings
from apps.stats.functions import get_report_data


class Command(BaseCommand):
    help = 'Generate and send reports'

    def add_arguments(self, parser):
        parser.add_argument('date_option')
        parser.add_argument('date')

    def handle(self, *args, **options):
        date_option = options['date_option']
        input_date = date_parser.parse(options['date']).date()
        if date_option == 'week':
            date_from = input_date.replace(day=(input_date.day - input_date.weekday()))
            date_to = date_from + relativedelta(days=6)
            title = 'Raport tygodniowy'
        elif date_option == 'month':
            date_from = input_date.replace(day=1)
            date_to = date_from + relativedelta(months=1) - relativedelta(days=1)
            title = 'Raport miesięczny'
        elif date_option == 'year':
            date_from = input_date.replace(day=1, month=1)
            date_to = date_from + relativedelta(years=1) - relativedelta(days=1)
            title = 'Raport roczny'
        else:
            print("Invalid date option (allowed are: 'week', 'month', 'year').")
            return

        print("Sending {} report from {} to {}".format(date_option, date_from, date_to))
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
