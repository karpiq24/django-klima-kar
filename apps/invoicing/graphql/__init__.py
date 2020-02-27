import os

from ariadne import load_schema_from_path
from django.conf import settings

from apps.invoicing.graphql.types import query, sale_invoice_types, payment_types, invoice


InvoicingTypeDefs = load_schema_from_path(
    os.path.join(settings.BASE_DIR, 'apps/invoicing/graphql/'))
InvoicingTypes = [query, sale_invoice_types, payment_types, invoice]
