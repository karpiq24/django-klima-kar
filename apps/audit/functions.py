import json

from django.db.utils import ProgrammingError
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import fields

from apps.audit.models import AuditLog


def get_object_diffrence(old_obj, new_obj):
    if old_obj._meta.model != new_obj._meta.model:
        raise ProgrammingError('Objects model mismatch.')
    diff = {}
    for field in old_obj._meta.get_fields():
        try:
            old_val = getattr(old_obj, field.attname)
            new_val = getattr(new_obj, field.attname)
        except AttributeError:
            continue
        if old_val != new_val:
            diff[field.name] = [old_val, new_val]
    return json.dumps(diff, cls=DjangoJSONEncoder) if diff else None


def get_object_json(obj):
    data = {}
    for field in obj._meta.get_fields():
        try:
            if type(field) is fields.related.ManyToManyField:
                val = [f.pk for f in getattr(obj, field.attname).all()]
            else:
                val = getattr(obj, field.attname)
        except AttributeError:
            continue
        data[field.name] = val
    return json.dumps(data, cls=DjangoJSONEncoder) if data else None


def pre_save_handler(sender, instance, **kwargs):
    model = instance._meta.model
    try:
        old_instance = model.objects.get(pk=instance.pk)
    except model.DoesNotExist:
        return
    diff = get_object_diffrence(old_instance, instance)
    if not diff:
        return
    AuditLog.objects.log_action(
        content_type=ContentType.objects.get_for_model(model),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action_type=AuditLog.CHANGE,
        diffrence=diff)


def post_save_handler(sender, instance, created, **kwargs):
    if not created:
        return
    model = instance._meta.model
    AuditLog.objects.log_action(
        content_type=ContentType.objects.get_for_model(model),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action_type=AuditLog.ADDITION)


def pre_delete_handler(sender, instance, **kwargs):
    model = instance._meta.model
    AuditLog.objects.log_action(
        content_type=ContentType.objects.get_for_model(model),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action_type=AuditLog.DELETION,
        diffrence=get_object_json(instance))
