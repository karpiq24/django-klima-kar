import os
import zipfile
import datetime
import dropbox

from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.six import StringIO

from KlimaKar.settings import DROPBOX_TOKEN


class Command(BaseCommand):
    help = 'Backups database to dropbox'
    apps_to_backup = ['warehouse', 'invoicing', 'commission']

    def handle(self, *args, **options):
        print("Backing up database for: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        zip_name = "{}-django-klimakar-backup.zip".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        temp_zip_file = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        try:
            dbx.users_get_current_account()
        except AuthError:
            print("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
            return

        for app in self.apps_to_backup:
            out = StringIO()
            call_command('dumpdata', app, stdout=out)
            temp_zip_file.writestr('{}.json'.format(app), out.getvalue())
        temp_zip_file.close()

        try:
            with open(zip_name, 'rb') as f:
                dbx.files_upload(f.read(), '/{}'.format(zip_name), mode=WriteMode('overwrite'))
        except ApiError as err:
            if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
                print("ERROR: Cannot back up; insufficient space.")
                return
            elif err.user_message_text:
                print(err.user_message_text)
                return
            else:
                print(err)
                return
        os.remove(zip_name)
        print("Database backup uploaded to Dropbox.")
