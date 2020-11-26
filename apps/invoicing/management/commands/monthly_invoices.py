from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.utils.formats import date_format

from KlimaKar.email import get_email_message
from apps.invoicing.models import SaleInvoice
from apps.settings.models import SiteSettings


class Command(BaseCommand):
    help = "Generate pdf invoices from previous month and send email"

    def add_arguments(self, parser):
        parser.add_argument("date")

    def handle(self, **options):
        config = SiteSettings.load()
        if not config.SEND_SALE_INVOICE:
            print("Sending email is disabled in settings.")
            return
        if not config.SEND_SALE_INVOICE_EMAILS:
            print("Email addresses list is empty.")
            return
        input_date = date_parser.parse(options["date"]).date()
        date_from = input_date.replace(day=1) - relativedelta(months=1)
        date_to = date_from + relativedelta(months=1) - relativedelta(days=1)
        month_name = date_format(date_from, "F").lower()
        invoices = (
            SaleInvoice.objects.taxed()
            .filter(issue_date__gte=date_from, issue_date__lte=date_to)
            .order_by("issue_date", "number_year", "number_value")
        )

        mail = get_email_message(
            subject=config.SEND_SALE_INVOICE_TITLE.format(
                month_name=month_name, month=date_from.month, year=date_from.year
            ),
            body=config.SEND_SALE_INVOICE_BODY.format(
                month_name=month_name, month=date_from.month, year=date_from.year
            ),
            to=config.SEND_SALE_INVOICE_EMAILS.split(","),
            bcc=True,
        )
        mail.attach(
            f"klimakar_faktury_{date_from.year}{date_from.month}.pdf",
            invoices.generate_pdf(),
            "application/pdf",
        )
        mail.send(fail_silently=False)
