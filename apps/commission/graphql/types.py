import enum

from ariadne import ObjectType, EnumType, QueryType, MutationType

from KlimaKar.graphql.utils import get_paginated_results
from apps.commission.models import Commission, Vehicle, Component


commission = ObjectType("Commission")
vehicle = ObjectType("Vehicle")
component = ObjectType("Component")
query = QueryType()
mutation = MutationType()


class CommissionStatus(enum.Enum):
    OPEN = Commission.OPEN
    READY = Commission.READY
    DONE = Commission.DONE
    CANCELLED = Commission.CANCELLED
    ON_HOLD = Commission.ON_HOLD


class CommissionType(enum.Enum):
    VEHICLE = Commission.VEHICLE
    COMPONENT = Commission.COMPONENT


commission_status = EnumType("CommissionStatus", CommissionStatus)
commission_type = EnumType("CommissionType", CommissionType)


@query.field("commissions")
def resolve_commissions(_, info, pagination=None, filters=None):
    return get_paginated_results(Commission.objects.all(), pagination, filters)


@query.field("vehicles")
def resolve_vehicles(_, info, pagination=None, filters=None):
    return get_paginated_results(Vehicle.objects.all(), pagination, filters)


@query.field("components")
def resolve_components(_, info, pagination=None, filters=None):
    return get_paginated_results(Component.objects.all(), pagination, filters)


@mutation.field("updateStatus")
def resolve_update_status(_, info, id, status):
    c = Commission.objects.get(id=id)
    c.status = status.value
    c.save()
    return c


@commission.field("saleInvoices")
def resolve_contractors(obj, info):
    return obj.sale_invoices.all()


@commission.field("items")
def resolve_items(obj, info):
    return obj.commissionitem_set.all()


@vehicle.field("commissions")
@component.field("commissions")
def resolve_vc_commissions(obj, info):
    return obj.commission_set.all()


@component.field("get_component_type_display")
def resolve_get_component_type_display(obj, info):
    return obj.get_component_type_display()
