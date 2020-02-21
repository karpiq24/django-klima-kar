from ariadne import QueryType

from KlimaKar.graphql.utils import get_paginated_results
from apps.invoicing.models import Contractor

query = QueryType()


@query.field("contractors")
def resolve_contractors(_, info, pagination=None, filters=None):
    return get_paginated_results(
        Contractor.objects.all(),
        pagination,
        filters)
