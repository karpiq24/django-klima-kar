from ariadne import load_schema_from_path
from apps.invoicing.graphql.types import query


InvoicingTypeDefs = load_schema_from_path('apps/invoicing/graphql/')
InvoicingTypes = [query]
