import os

from ariadne import load_schema_from_path
from django.conf import settings

from apps.warehouse.graphql.types import query, invoice, ware, supplier

from apps.warehouse.graphql.queries import *  # noqa
from apps.warehouse.graphql.mutations import *  # noqa


WarehouseTypeDefs = load_schema_from_path(
    os.path.join(settings.BASE_DIR, "apps/warehouse/graphql/")
)
WarehouseTypes = [query, invoice, ware, supplier]
