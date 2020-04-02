from KlimaKar.graphql.utils import get_paginated_results
from apps.invoicing.models import Contractor, SaleInvoice, ServiceTemplate
from apps.invoicing.graphql import query, invoice


@query.field("contractors")
def resolve_contractors(_, info, pagination=None, filters=None):
    return get_paginated_results(Contractor.objects.all(), pagination, filters)


@query.field("saleInvoices")
def resolve_invoices(_, info, pagination=None, filters=None):
    return get_paginated_results(SaleInvoice.objects.all(), pagination, filters)


@query.field("services")
def resolve_services(_, info, pagination=None, filters=None):
    return get_paginated_results(ServiceTemplate.objects.all(), pagination, filters)


@invoice.field("items")
def resolve_items(obj, info):
    return obj.saleinvoiceitem_set.all()


@invoice.field("commissions")
def resolve_vc_commissions(obj, info):
    return obj.commission.all()
