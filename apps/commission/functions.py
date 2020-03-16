import os
import json
import shutil

from KlimaKar import settings
from apps.settings.models import MyCloudHome
from apps.commission.models import Commission, CommissionFile


def check_uploaded_files(upload_key):
    directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
    if not os.path.exists(directory):
        return False
    metafiles = [m for m in os.listdir(directory) if m.endswith('meta')]
    if not metafiles:
        return False
    return True


def get_temporary_files(upload_key):
    directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
    files = []
    if not os.path.exists(directory):
        return files
    for f in [m for m in os.listdir(directory) if m.endswith('meta')]:
        with open(os.path.join(directory, f)) as metafile:
            files.append(json.loads(metafile.read()))
    return files


def get_commission_directory(commission):
    cloud = MyCloudHome.load()
    if commission.mch_id:
        return commission.mch_id
    else:
        r = cloud.create_folder(str(commission.pk), cloud.COMMISSION_DIR_ID)
        if r.status_code == 201:
            commission.mch_id = r.headers['Location'].split('/')[-1]
        else:
            for f in cloud.get_files(cloud.COMMISSION_DIR_ID)['files']:
                if f['name'] == str(commission.pk):
                    commission.mch_id = f['id']
                    break
        commission.save()
    return commission.mch_id


def process_uploads(commission_pk, upload_key):
    files_added = 0
    directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
    metafiles = get_temporary_files(upload_key)
    if not metafiles:
        shutil.rmtree(directory)
        return files_added
    try:
        commission = Commission.objects.get(pk=commission_pk)
    except Commission.DoesNotExist:
        shutil.rmtree(directory)
        return files_added
    cloud = MyCloudHome.load()
    commission_dir = get_commission_directory(commission)
    for meta in metafiles:
        file_path = os.path.join(directory, meta['name'])
        if not os.path.exists(file_path):
            continue
        r = cloud.create_file(meta['name'], open(
            file_path, 'rb').read(), commission_dir)
        if r.status_code == 409 or r.status_code != 201:
            continue
        mch_id = r.headers['Location'].split('/')[-1]
        CommissionFile.objects.create(
            commission=commission,
            file_name=meta['name'],
            file_size=meta['size'],
            mime_type=meta['type'],
            mch_id=mch_id
        )
        files_added += 1
    shutil.rmtree(directory)
    commission.upload = False
    commission.save()
    return files_added
