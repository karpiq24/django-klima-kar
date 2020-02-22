from ariadne import load_schema_from_path
from apps.warehouse.graphql.types import query, invoice, ware, supplier


WarehouseTypeDefs = load_schema_from_path('apps/warehouse/graphql/')
WarehouseTypes = [query, invoice, ware, supplier]
