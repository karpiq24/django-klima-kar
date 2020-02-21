import enum

from ariadne import QueryType

from KlimaKar.graphql.utils import get_paginated_results
from apps.invoicing.models import Contractor

query = QueryType()


@query.field("contractors")
def resolve_contractors(_, info, pagination=None, filters=None):
    qs = Contractor.objects.all()
    if not pagination:
        pagination = {}
    if filters:
        for key, value in filters.items():
            if issubclass(type(value), enum.Enum):
                filters[key] = value.value
        qs = qs.filter(**filters)
    return get_paginated_results(qs, **pagination)
