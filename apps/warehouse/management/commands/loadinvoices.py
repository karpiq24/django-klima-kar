import datetime
import traceback

from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Loads invoices from various suppliers'
    LOAD_COMMANDS = ['loadintercars', 'loaddeko', 'loadgordon', 'loadsauto', 'loadzatoka']

    def add_arguments(self, parser):
        parser.add_argument('date_from', nargs='?',
                            default=(datetime.date.today() - datetime.timedelta(7)).strftime('%Y-%m-%d'))
        parser.add_argument('date_to', nargs='?',
                            default=(datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'))

    def handle(self, *args, **options):
        for command in self.LOAD_COMMANDS:
            print('Calling {}'.format(command))
            try:
                call_command(command, **options)
            except Exception:
                self.report_admins(command, traceback.format_exc())

    def report_admins(self, command, message):
        mail_admins('{} invoice download failed!', command, message)
