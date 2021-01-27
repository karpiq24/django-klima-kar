from django.db.models import Q

from KlimaKar.graphql.utils import get_paginated_results
from apps.warehouse.models import Ware, Supplier, Invoice
from apps.warehouse.graphql.types import query, invoice, supplier, ware


@query.field("wares")
def resolve_wares(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        return qs.filter(
            Q(index__icontains=search)
            | Q(index_slug__icontains=search)
            | Q(barcode=search)
        )

    return get_paginated_results(
        Ware.objects.all(), pagination, filters, custom_filter=search_filter
    )


@query.field("suppliers")
def resolve_suppliers(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        return qs.filter(name__icontains=search)

    return get_paginated_results(
        Supplier.objects.all(), pagination, filters, custom_filter=search_filter
    )


@query.field("purchaseInvoices")
def resolve_invoices(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        return qs.filter(
            Q(number__icontains=search) | Q(supplier__name__icontains=search)
        )

    return get_paginated_results(
        Invoice.objects.all(), pagination, filters, custom_filter=search_filter
    )


@invoice.field("items")
def resolve_items(obj, info):
    return obj.invoiceitem_set.all()


@supplier.field("purchaseInvoices")
def resolve_supplier_invoices(obj, info):
    return obj.invoice_set.all()


@ware.field("purchaseInvoices")
def resolve_ware_invoices(obj, info):
    return Invoice.objects.filter(invoiceitem__ware=obj)
