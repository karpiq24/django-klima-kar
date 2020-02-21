from ariadne import load_schema_from_path
from apps.commission.graphql.types import commission, commission_type, commission_status, query, mutation


CommissionTypeDefs = load_schema_from_path('apps/commission/graphql/')
CommissionTypes = [commission, commission_type, commission_status, query, mutation]
