
import os
import tempfile
import zipfile
import datetime
import shutil
import dropbox

from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from subprocess import Popen, STDOUT

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import mail_admins

from apps.settings.models import MyCloudHome


class Command(BaseCommand):
    help = "Backup postgres database with sql dump."
    ENGINE = 'django.db.backends.postgresql_psycopg2'

    def add_arguments(self, parser):
        parser.add_argument('directory', nargs='?')
        parser.add_argument('--mycloud', action='store_true')
        parser.add_argument('--dropbox', action='store_true')

    def handle(self, *args, **options):
        if not options['directory'] and not options['mycloud'] and not options['dropbox']:
            print("Output directory or --mycloud or --dropbox flag is required.")
        if options['directory'] and not os.path.isdir(options['directory']):
            print("{} is not a directory".format(options['directory']))

        db = settings.DATABASES.get('default')
        if db.get('ENGINE') != self.ENGINE:
            print("Invalid database engine.")
            return
        command = [
            f'pg_dump',
            f'--host={db["HOST"]}',
            f'--dbname={db["NAME"]}',
            f'--username={db["USER"]}',
            f'--no-password'
        ]

        temp_dir = tempfile.mkdtemp()
        file_name = "{}-django-klimakar-backup.sql".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        if options['directory']:
            write_path = os.path.join(options['directory'], file_name)
        else:
            write_path = os.path.join(temp_dir, file_name)

        process = Popen(
            command,
            stdout=open(write_path, 'w'),
            stderr=STDOUT,
            env={'PGPASSWORD': db['PASSWORD']}
        )
        process.wait()
        if options['mycloud'] or options['dropbox']:
            zip_name = "{}-django-klimakar-sqldump.zip".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
            zip_path = os.path.join(temp_dir, zip_name)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as temp_zip_file:
                temp_zip_file.write(write_path, file_name)
            if options['mycloud']:
                self.upload_to_mycloud(zip_name, zip_path)
            if options['dropbox']:
                self.upload_to_dropbox(zip_name, zip_path)

        shutil.rmtree(temp_dir)

    def upload_to_mycloud(self, file_name, file_path):
        cloud = MyCloudHome.load()
        r = cloud.create_file(file_name, open(file_path, 'rb').read(), cloud.BACKUP_DIR_ID)
        if r.status_code == 409 or r.status_code != 201:
            mail_admins('Postgres backup save failed!', r.text)

    def upload_to_dropbox(self, file_name, file_path):
        dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
        try:
            dbx.users_get_current_account()
        except AuthError:
            mail_admins(
                'Postgres backup dropbox save failed!',
                "ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
            print("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
            return
        try:
            with open(file_path, 'rb') as f:
                dbx.files_upload(f.read(), '/sqldump/{}'.format(file_name), mode=WriteMode('overwrite'))
        except ApiError as err:
            if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
                mail_admins(
                    'Postgres backup dropbox save failed!',
                    "ERROR: Cannot back up; insufficient space")
                print("ERROR: Cannot back up; insufficient space.")
                return
            elif err.user_message_text:
                mail_admins(
                    'Postgres backup dropbox save failed!',
                    err.user_message_text)
                print(err.user_message_text)
                return
            else:
                mail_admins(
                    'Postgres backup dropbox save failed!',
                    err)
                print(err)
                return
