import os
import json
import shutil

from KlimaKar import settings
from KlimaKar.models import MyCloudHome
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
    for f in os.listdir(directory):
        if f.endswith('meta'):
            with open(os.path.join(directory, f)) as metafile:
                files.append(json.loads(metafile.read()))
    return files


def process_uploads(commission_pk, upload_key):
    files_added = 0
    directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
    metafiles = [m for m in os.listdir(directory) if m.endswith('meta')]
    try:
        commission = Commission.objects.get(pk=commission_pk)
    except Commission.DoesNotExist:
        shutil.rmtree(directory)
        return files_added
    cloud = MyCloudHome.load()
    cloud.create_folder(str(commission.pk), cloud.COMMISSION_DIR_ID)
    pk_dir = None
    for f in cloud.get_files(cloud.COMMISSION_DIR_ID)['files']:
        if f['name'] == str(commission.pk):
            pk_dir = f['id']
            break
    for meta in metafiles:
        meta_path = os.path.join(directory, meta)
        with open(meta_path) as metafile:
            data = json.loads(metafile.read())
        file_path = os.path.join(directory, data['name'])
        if not os.path.exists(file_path):
            os.remove(meta_path)
            continue
        r = cloud.create_file(data['name'], open(file_path, 'rb').read(), pk_dir)
        if r.status_code == 409:
            continue
        mch_id = None
        for f in cloud.get_files(pk_dir)['files']:
            if f['name'] == data['name']:
                mch_id = f['id']
                break
        if mch_id:
            CommissionFile.objects.create(
                commission=commission,
                file_name=data['name'],
                file_size=data['size'],
                mime_type=data['type'],
                mch_id=mch_id
            )
            files_added += 1
    shutil.rmtree(directory)
    commission.upload = False
    commission.save()
    return files_added
