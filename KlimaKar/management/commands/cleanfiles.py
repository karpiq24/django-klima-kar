import os
import datetime
import shutil

from dateutil import parser as DateParser

from django.core.management.base import BaseCommand

from KlimaKar.settings import HOURS_TO_REMOVE_STALE_FILES, TEMPORARY_UPLOAD_DIRECTORY


class Command(BaseCommand):
    help = "Delete stale uploaded files"

    def handle(self, *args, **options):
        for folder in os.listdir(TEMPORARY_UPLOAD_DIRECTORY):
            path = os.path.join(TEMPORARY_UPLOAD_DIRECTORY, folder)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.exists(os.path.join(path, "lock")):
                continue
            elif os.path.exists(os.path.join(path, "timestamp")):
                with open(os.path.join(path, "timestamp"), "r") as timefile:
                    timestamp = DateParser.parse(timefile.read())
                    diff = datetime.datetime.now() - timestamp
                    hours = diff.days * 24 + diff.seconds // 3600
                    if hours >= HOURS_TO_REMOVE_STALE_FILES:
                        shutil.rmtree(path)
                    if hours < 0:
                        shutil.rmtree(path)
            else:
                shutil.rmtree(path)
