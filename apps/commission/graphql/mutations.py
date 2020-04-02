from KlimaKar.graphql.resolvers import BaseModelFormResolver
from apps.commission.models import Commission
from apps.commission.forms import (
    CommissionModelForm,
    CommissionItemModelForm,
    ComponentModelForm,
    VehicleModelForm,
)

from apps.commission.graphql.types import mutation


@mutation.field("updateStatus")
def resolve_update_status(_, info, id, status):
    c = Commission.objects.get(id=id)
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
