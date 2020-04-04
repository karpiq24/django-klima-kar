from KlimaKar.graphql.utils import get_paginated_results
from apps.commission.models import Commission, Vehicle, Component
from apps.commission.graphql import query, commission, vehicle, component


@query.field("commissions")
def resolve_commissions(_, info, pagination=None, filters=None):
    return get_paginated_results(Commission.objects.all(), pagination, filters)


@query.field("vehicles")
def resolve_vehicles(_, info, pagination=None, filters=None):
    return get_paginated_results(Vehicle.objects.all(), pagination, filters)


@query.field("components")
def resolve_components(_, info, pagination=None, filters=None):
    return get_paginated_results(Component.objects.all(), pagination, filters)


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


@vehicle.field("get_fuel_type_display")
def resolve_get_fuel_type_display(obj, info):
    return obj.get_fuel_type_display()
