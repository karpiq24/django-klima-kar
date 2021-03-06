import os

from ariadne import load_schema_from_path
from django.conf import settings

from apps.commission.graphql.types import (
    commission,
    query,
    mutation,
    vehicle,
    component,
)

from apps.commission.graphql.queries import *  # noqa
from apps.commission.graphql.mutations import *  # noqa


CommissionTypeDefs = load_schema_from_path(
    os.path.join(settings.BASE_DIR, "apps/commission/graphql/")
)
CommissionTypes = [
    commission,
    query,
    mutation,
    vehicle,
    component,
]
