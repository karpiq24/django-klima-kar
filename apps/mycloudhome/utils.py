import json
import os
import shutil

import django_rq
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from apps.settings.models import MyCloudHome


def file_pre_delete_handler(sender, instance, **kwargs):
    if instance.mch_id:
        cache.delete(f"file_{instance.mch_id}")
        cloud = MyCloudHome.load()
        return cloud.delete_file(instance.mch_id)


def temporary_files_exist(upload_key):
    directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
    if not os.path.exists(directory):
        return False
    metafiles = [m for m in os.listdir(directory) if m.endswith("meta")]
    if not metafiles:
        return False
    return True


def get_temporary_files(upload_key):
    directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
    files = []
    if not os.path.exists(directory):
        return files
    for f in [m for m in os.listdir(directory) if m.endswith("meta")]:
        with open(os.path.join(directory, f)) as metafile:
            files.append(json.loads(metafile.read()))
    return files


def get_mch_directory_id(directory, obj):
    cloud = MyCloudHome.load()
    if obj.mch_id:
        return obj.mch_id
    else:
        r = cloud.create_folder(str(obj.pk), directory)
        if r.status_code == 201:
            obj.mch_id = r.headers["Location"].split("/")[-1]
        else:
            for f in cloud.get_files(directory)["files"]:
                if f["name"] == str(obj.pk):
                    obj.mch_id = f["id"]
                    break
        obj.save()
    return obj.mch_id


def process_mch_uploads(
    directory_pk, upload_key, directory_content_type, file_content_type
):
    files_added = 0
    directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
    metafiles = get_temporary_files(upload_key)
    cloud = MyCloudHome.load()
    directory_model = ContentType.objects.get_for_id(
        directory_content_type
    ).model_class()
    file_model = ContentType.objects.get_for_id(file_content_type).model_class()
    if not metafiles:
        shutil.rmtree(directory)
        return files_added
    try:
        directory_object = directory_model.objects.get(pk=directory_pk)
    except directory_model.DoesNotExist:
        shutil.rmtree(directory)
        return files_added
    directory_id = get_mch_directory_id(
        getattr(cloud, directory_object.DIRECTORY_ID_FIELD), directory_object
    )
    for meta in metafiles:
        file_path = os.path.join(directory, meta["name"])
        if not os.path.exists(file_path):
            continue
        r = cloud.create_file(meta["name"], open(file_path, "rb").read(), directory_id)
        if r.status_code == 409 or r.status_code != 201:
            continue
        mch_id = r.headers["Location"].split("/")[-1]
        file_model.objects.create(
            **{
                file_model.PARENT_FIELD: directory_object,
                "file_name": meta["name"],
                "file_size": meta["size"],
                "mime_type": meta["type"],
                "mch_id": mch_id,
            }
        )
        files_added += 1
    shutil.rmtree(directory)
    directory_object.upload = False
    directory_object.save()
    return files_added


def check_and_enqueue_file_upload(upload_key, directory_object, file_model):
    if temporary_files_exist(upload_key):
        directory_object.upload = True
        directory_object.save()
        temporary_directory = os.path.join(
            settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key
        )
        with open(os.path.join(temporary_directory, "lock"), "w") as lockfile:
            lockfile.write("")
        django_rq.enqueue(
            process_mch_uploads,
            directory_object.pk,
            upload_key,
            ContentType.objects.get_for_model(directory_object._meta.model).pk,
            ContentType.objects.get_for_model(file_model).pk,
        )
        return True
