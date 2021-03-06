import os

from ariadne import load_schema_from_path

from apps.invoicing.graphql.types import query, invoice, contractor, service

from apps.invoicing.graphql.queries import *  # noqa
from apps.invoicing.graphql.mutations import *  # noqa

from django.conf import settings


InvoicingTypeDefs = load_schema_from_path(
    os.path.join(settings.BASE_DIR, "apps/invoicing/graphql/")
)
InvoicingTypes = [query, invoice, contractor, service]
