from KlimaKar.graphql.resolvers import BaseModelFormResolver
from apps.commission.models import Commission, CommissionNote
from apps.commission.forms import (
    CommissionModelForm,
    CommissionItemModelForm,
    ComponentModelForm,
    VehicleModelForm,
)

from apps.commission.graphql.types import mutation


@mutation.field("updateStatus")
def resolve_update_status(_, info, pk, status):
    c = Commission.objects.get(id=pk)
    c.status = status.value
    c.save()
    return c


class AddCommissionResolver(BaseModelFormResolver):
    form_class = CommissionModelForm
    inlines = {"items": CommissionItemModelForm}
    inlines_parent = "commission"


@mutation.field("addComission")
def resolve_add_comission(_, info, data):
    return AddCommissionResolver(data).process()


class AddComponentResolver(BaseModelFormResolver):
    form_class = ComponentModelForm


@mutation.field("addComponent")
def resolve_add_component(_, info, data):
    return AddComponentResolver(data).process()


class AddVehicleResolver(BaseModelFormResolver):
    form_class = VehicleModelForm


@mutation.field("addVehicle")
def resolve_add_vehicle(_, info, data):
    return AddVehicleResolver(data).process()


@mutation.field("addCommissionNote")
def resolve_add_commission_note(_, info, commission, contents):
    try:
        commission_obj = Commission.objects.get(pk=commission)
    except Commission.DoesNotExist:
        return None
    note = CommissionNote.objects.create(commission=commission_obj, contents=contents)
    return note


@mutation.field("updateCommissionNote")
def resolve_update_commission_note(_, info, pk, contents, isActive):
    try:
        note = CommissionNote.objects.get(pk=pk)
    except CommissionNote.DoesNotExist:
        return None
    note.contents = contents
    note.is_active = isActive
    note.save()
    return note
