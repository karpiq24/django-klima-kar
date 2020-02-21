import enum

from ariadne import ObjectType, EnumType, QueryType, MutationType

from KlimaKar.graphql.utils import get_paginated_results
from apps.commission.models import Commission


commission = ObjectType('Commission')
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


commission_status = EnumType(
    'CommissionStatus', CommissionStatus)
commission_type = EnumType(
    'CommissionType', CommissionType)


@query.field("commissions")
def resolve_commissions(_, info, pagination=None, filters=None):
    return get_paginated_results(
        Commission.objects.all(),
        pagination,
        filters)


@mutation.field("updateStatus")
def resolve_update_status(_, info, id, status):
    c = Commission.objects.get(id=id)
    c.status = status.value
    c.save()
    return c


@commission.field("sale_invoices")
def resolve_contractors(obj, info):
    return obj.sale_invoices.all()
