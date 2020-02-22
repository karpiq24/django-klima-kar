from ariadne import load_schema_from_path
from apps.invoicing.graphql.types import query, sale_invoice_types, payment_types, invoice


InvoicingTypeDefs = load_schema_from_path('apps/invoicing/graphql/')
InvoicingTypes = [query, sale_invoice_types, payment_types, invoice]
