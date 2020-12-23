import os

from ariadne import make_executable_schema, load_schema_from_path
from django.conf import settings

from apps.commission.graphql import CommissionTypeDefs, CommissionTypes
from apps.invoicing.graphql import InvoicingTypeDefs, InvoicingTypes
from apps.warehouse.graphql import WarehouseTypeDefs, WarehouseTypes
from apps.annotations.graphql import AnnotationTypeDefs, AnnotationTypes

QuerySchema = load_schema_from_path(os.path.join(settings.BASE_DIR, "KlimaKar/graphql"))

schema = make_executable_schema(
    [
        QuerySchema,
        CommissionTypeDefs,
        InvoicingTypeDefs,
        WarehouseTypeDefs,
        AnnotationTypeDefs,
    ],
    [*CommissionTypes, *InvoicingTypes, *WarehouseTypes, *AnnotationTypes],
)
