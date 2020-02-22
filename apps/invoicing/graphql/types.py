import enum

from ariadne import QueryType, ObjectType, EnumType

from KlimaKar.graphql.utils import get_paginated_results
from apps.invoicing.models import Contractor, SaleInvoice

query = QueryType()
invoice = ObjectType("SaleInvoice")


class SaleInvoiceType(enum.Enum):
    TYPE_VAT = SaleInvoice.TYPE_VAT
    TYPE_PRO_FORMA = SaleInvoice.TYPE_PRO_FORMA
    TYPE_CORRECTIVE = SaleInvoice.TYPE_CORRECTIVE
    TYPE_WDT = SaleInvoice.TYPE_WDT
    TYPE_WDT_PRO_FORMA = SaleInvoice.TYPE_WDT_PRO_FORMA


class PaymentType(enum.Enum):
    CASH = SaleInvoice.CASH
    CARD = SaleInvoice.CARD
    TRANSFER = SaleInvoice.TRANSFER
    OTHER = SaleInvoice.OTHER


sale_invoice_types = EnumType(
    'SaleInvoiceType', SaleInvoiceType)
payment_types = EnumType(
    'PaymentType', PaymentType)


@query.field("contractors")
def resolve_contractors(_, info, pagination=None, filters=None):
    return get_paginated_results(
        Contractor.objects.all(),
        pagination,
        filters)


@query.field("saleInvoices")
def resolve_invoices(_, info, pagination=None, filters=None):
    return get_paginated_results(
        SaleInvoice.objects.all(),
        pagination,
        filters)


@invoice.field("items")
def resolve_items(obj, info):
    return obj.saleinvoiceitem_set.all()


@invoice.field("commissions")
def resolve_vc_commissions(obj, info):
    return obj.commission.all()
