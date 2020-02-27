import os

from ariadne import load_schema_from_path
from django.conf import settings

from apps.commission.graphql.types import commission, commission_type, commission_status, query, mutation, vehicle, \
    component


CommissionTypeDefs = load_schema_from_path(
    os.path.join(settings.BASE_DIR, 'apps/commission/graphql/'))
CommissionTypes = [commission, commission_type, commission_status, query, mutation, vehicle, component]
