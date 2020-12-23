from KlimaKar.graphql.utils import get_paginated_results
from apps.annotations.models import Annotation
from apps.annotations.graphql import query


@query.field("annotations")
def resolve_annotations(_, info, pagination=None, filters=None):
    return get_paginated_results(Annotation.objects.all(), pagination, filters)
