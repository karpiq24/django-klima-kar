import datetime
import sys
import logging

from django.core.management.base import BaseCommand
from django.core.management import call_command

from apps.settings.models import InvoiceDownloadSettings


class Command(BaseCommand):
    help = "Loads invoices from various suppliers"
    LOAD_COMMANDS = [
        ("DOWNLOAD_INTER_CARS", "loadintercars"),
        ("DOWNLOAD_DEKO", "loaddeko"),
        ("DOWNLOAD_GORDON", "loadgordon"),
        ("DOWNLOAD_PROFIAUTO", "loadprofiauto"),
        ("DOWNLOAD_ZATOKA", "loadzatoka"),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "date_from",
            nargs="?",
            default=(datetime.date.today() - datetime.timedelta(7)).strftime(
                "%Y-%m-%d"
            ),
        )
        parser.add_argument(
            "date_to",
            nargs="?",
            default=(datetime.date.today() + datetime.timedelta(1)).strftime(
                "%Y-%m-%d"
            ),
        )

    def handle(self, *args, **options):
        settings = InvoiceDownloadSettings.load()
        for attr, command in self.LOAD_COMMANDS:
            if getattr(settings, attr):
                try:
                    print("Calling {}".format(command))
                    call_command(command, **options)
                except Exception:
                    logging.getLogger("commands").error(
                        "Admin Command Error: {}".format(" ".join(sys.argv)),
                        exc_info=sys.exc_info(),
                    )
