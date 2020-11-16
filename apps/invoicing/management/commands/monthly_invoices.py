from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.utils.formats import date_format

from KlimaKar.email import mail_managers
from apps.invoicing.models import SaleInvoice


class Command(BaseCommand):
    help = "Generate monthly pdf invoices and send email"

    def add_arguments(self, parser):
        parser.add_argument("date")

    def handle(self, **options):
        input_date = date_parser.parse(options["date"]).date()
        date_from = input_date.replace(day=1)
        date_to = date_from + relativedelta(months=1) - relativedelta(days=1)
        month_name = date_format(date_from, "F").lower()
        invoices = (
            SaleInvoice.objects.taxed()
            .filter(issue_date__gte=date_from, issue_date__lte=date_to)
            .order_by("issue_date", "number_year", "number_value")
        )

        mail_managers(
            f"faktury {month_name} {date_from.year}",
            "\n".join([str(i) for i in invoices]),
            attachment={
                "filename": f"klimakar_faktury_{date_from.year}{date_from.month}.pdf",
                "file": invoices.generate_pdf(),
                "mime": "application/pdf",
            },
            fail_silently=False,
        )
