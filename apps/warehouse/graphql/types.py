from ariadne import QueryType, ObjectType

from KlimaKar.graphql.utils import get_paginated_results
from apps.warehouse.models import Ware, Supplier, Invoice

query = QueryType()
invoice = ObjectType('PurchaseInvoice')
ware = ObjectType('Ware')
supplier = ObjectType('Supplier')


@query.field("wares")
def resolve_wares(_, info, pagination=None, filters=None):
    return get_paginated_results(
        Ware.objects.all(),
        pagination,
        filters)


@query.field("suppliers")
def resolve_suppliers(_, info, pagination=None, filters=None):
    return get_paginated_results(
        Supplier.objects.all(),
        pagination,
        filters)


@query.field("purchaseInvoices")
def resolve_invoices(_, info, pagination=None, filters=None):
    return get_paginated_results(
        Invoice.objects.all(),
        pagination,
        filters)


@invoice.field("items")
def resolve_items(obj, info):
    return obj.invoiceitem_set.all()


@supplier.field("purchaseInvoices")
def resolve_supplier_invoices(obj, info):
    return obj.invoice_set.all()


@ware.field("purchaseInvoices")
def resolve_ware_invoices(obj, info):
    return Invoice.objects.filter(invoiceitem__ware=obj)
