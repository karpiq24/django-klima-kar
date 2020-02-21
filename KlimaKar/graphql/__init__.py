from ariadne import make_executable_schema, load_schema_from_path

from apps.commission.graphql import CommissionTypeDefs, CommissionTypes
from apps.invoicing.graphql import InvoicingTypeDefs, InvoicingTypes

QuerySchema = load_schema_from_path('KlimaKar/graphql')

schema = make_executable_schema(
    [QuerySchema, CommissionTypeDefs, InvoicingTypeDefs],
    [*CommissionTypes, *InvoicingTypes])
