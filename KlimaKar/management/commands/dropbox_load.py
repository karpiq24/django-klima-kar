import os
import zipfile
import dropbox
import tempfile
import shutil

from dropbox.exceptions import AuthError

from django.core.management import call_command
from django.core.management.base import BaseCommand

from KlimaKar.settings import DROPBOX_TOKEN
from apps.warehouse import models as warehouse
from apps.invoicing import models as invoicing
from apps.commission import models as commission


class Command(BaseCommand):
    help = 'Loads backup from dropbox'
    apps_to_load = ['warehouse', 'invoicing', 'commission', 'stats']

    def handle(self, *args, **options):
        print("Are you sure you want to load backup?\nThis process will replace all data (Y/n)")
        if input() != 'Y':
            return

        self._clear_warehouse()
        self._clear_commission()
        self._clear_invocing()

        dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        try:
            dbx.users_get_current_account()
        except AuthError:
            print("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
            return
        path = dbx.files_list_folder('').entries[-1].path_lower
        metadata, response = dbx.files_download(path)
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, 'backup.zip')
        with open(path, 'wb') as backup:
            backup.write(response.content)

        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        for app in self.apps_to_load:
            call_command('loaddata', os.path.join(temp_dir, '{}.json'.format(app)))
        shutil.rmtree(temp_dir)

    def _clear_warehouse(self):
        print('Deleted from warehouse:')
        print(' ' * 4, warehouse.Invoice.objects.all().delete())
        print(' ' * 4, warehouse.Ware.objects.all().delete())
        print(' ' * 4, warehouse.Supplier.objects.all().delete())

    def _clear_invocing(self):
        print('Deleted from invoicing:')
        print(' ' * 4, invoicing.CorrectiveSaleInvoice.objects.all().delete())
        print(' ' * 4, invoicing.SaleInvoice.objects.all().delete())
        print(' ' * 4, invoicing.Contractor.objects.all().delete())
        print(' ' * 4, invoicing.ServiceTemplate.objects.all().delete())

    def _clear_commission(self):
        print('Deleted from commission:')
        print(' ' * 4, commission.Commission.objects.all().delete())
        print(' ' * 4, commission.Component.objects.all().delete())
        print(' ' * 4, commission.Vehicle.objects.all().delete())
