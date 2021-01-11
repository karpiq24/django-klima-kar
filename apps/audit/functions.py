import inspect
import json

from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Q
from django.db.utils import ProgrammingError
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.related import ManyToManyField

from apps.annotations.models import Annotation
from apps.audit.models import AuditLog


def get_object_difference(old_obj, new_obj):
    if old_obj._meta.model != new_obj._meta.model:
        raise ProgrammingError("Objects model mismatch.")
    ignore_fields = getattr(old_obj._meta.model, "AUDIT_IGNORE", [])
    diff = {}
    for field in old_obj._meta.get_fields():
        try:
            if field.attname in ignore_fields:
                continue
            old_val = getattr(old_obj, field.attname)
            new_val = getattr(new_obj, field.attname)
        except AttributeError:
            continue
        if old_val != new_val:
            diff[field.name] = [old_val, new_val]
    return json.loads(json.dumps(diff, cls=DjangoJSONEncoder)) if diff else None


def get_object_json(obj):
    data = {}
    for field in obj._meta.get_fields():
        try:
            if type(field) is GenericRelation:
                continue
            if type(field) is ManyToManyField:
                val = [f.pk for f in getattr(obj, field.attname).all()]
            else:
                val = getattr(obj, field.attname)
        except AttributeError:
            continue
        data[field.name] = val
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder)) if data else None


def inspect_user():
    frame = inspect.currentframe()
    while frame:
        try:
            return frame.f_locals["request"].user
        except KeyError:
            frame = frame.f_back
    return None


def pre_save_handler(sender, instance, **kwargs):
    model = instance._meta.model
    try:
        old_instance = model.objects.get(pk=instance.pk)
    except model.DoesNotExist:
        return
    diff = get_object_difference(old_instance, instance)
    if not diff:
        return
    AuditLog.objects.log_action(
        content_type=ContentType.objects.get_for_model(model),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action_type=AuditLog.CHANGE,
        difference=diff,
    )


def post_save_handler(sender, instance, created, **kwargs):
    if not created:
        return
    model = instance._meta.model
    AuditLog.objects.log_action(
        content_type=ContentType.objects.get_for_model(model),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action_type=AuditLog.ADDITION,
    )


def pre_delete_handler(sender, instance, **kwargs):
    model = instance._meta.model
    AuditLog.objects.log_action(
        content_type=ContentType.objects.get_for_model(model),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action_type=AuditLog.DELETION,
        difference=get_object_json(instance),
    )


def m2m_changed_handler(sender, instance, action, pk_set, **kwargs):
    if action not in ["pre_add", "pre_remove"]:
        return

    model = instance._meta.model
    diff = {}
    the_field = None
    for field in model._meta.get_fields():
        if (
            type(field) is ManyToManyField
            and getattr(model, field.attname).through is sender
        ):
            the_field = field
            old_pk_set = [f.pk for f in getattr(instance, the_field.attname).all()]
    if action == "pre_add":
        new_pk_set = old_pk_set + list(pk_set)
    elif action == "pre_remove":
        new_pk_set = [pk for pk in old_pk_set if pk not in pk_set]
    if old_pk_set == new_pk_set:
        return

    diff[the_field.name] = [old_pk_set, new_pk_set]
    AuditLog.objects.log_action(
        content_type=ContentType.objects.get_for_model(model),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action_type=AuditLog.CHANGE,
        difference=diff,
    )


def get_audit_logs(obj, has_annotations=True, m2one=[], extra=AuditLog.objects.none()):
    logs = AuditLog.objects.filter(
        content_type=ContentType.objects.get_for_model(obj._meta.model),
        object_id=obj.pk,
    )
    if has_annotations:
        logs = logs | AuditLog.objects.filter(
            content_type=ContentType.objects.get_for_model(Annotation),
            object_id__in=map(str, obj.annotations.all().values_list("pk", flat=True)),
        )
    for rel in m2one:
        logs = logs | AuditLog.objects.filter(
            Q(**{f"difference__{rel['key']}": obj.pk})
            | Q(object_id__in=map(str, rel["objects"].values_list("pk", flat=True))),
            content_type=ContentType.objects.get_for_model(rel["model"]),
        )
    return (logs | extra).distinct().order_by("-action_time")
