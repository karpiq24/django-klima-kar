import enum

from ariadne import QueryType, ObjectType, EnumType

from apps.invoicing.models import SaleInvoice

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


sale_invoice_types = EnumType("SaleInvoiceType", SaleInvoiceType)
payment_types = EnumType("PaymentType", PaymentType)
