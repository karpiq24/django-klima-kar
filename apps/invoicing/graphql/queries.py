import requests
import datetime

from zeep import Client as ZeepClient

from django.db.models import Q
from django.conf import settings

from KlimaKar.graphql.utils import get_paginated_results
from apps.invoicing.models import Contractor, SaleInvoice, ServiceTemplate
from apps.invoicing.graphql import query, invoice, contractor, service
from apps.invoicing.gus import GUS


@query.field("contractors")
def resolve_contractors(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        q = search.replace(" ", "")
        return qs.filter(
            Q(name__icontains=search)
            | Q(nip__icontains=q)
            | Q(phone_1__icontains=q)
            | Q(phone_2__icontains=q)
        )

    return get_paginated_results(
        Contractor.objects.all(), pagination, filters, custom_filter=search_filter,
    )


@query.field("saleInvoices")
def resolve_invoices(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        queryset = qs.filter(number__iexact=search)
        if queryset.count() < 1:
            queryset = qs.filter(number__icontains=search)
        return queryset

    return get_paginated_results(
        SaleInvoice.objects.all(), pagination, filters, custom_filter=search_filter
    )


@query.field("services")
def resolve_services(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        return qs.filter(Q(name__icontains=search) | Q(description__icontains=search))

    return get_paginated_results(
        ServiceTemplate.objects.all(), pagination, filters, custom_filter=search_filter
    )


@query.field("gusAddress")
def resolve_gus_address(_, info, nip):
    if len(nip) != 10:
        return None
    return GUS.get_gus_address(nip)


@invoice.field("items")
def resolve_items(obj, info):
    return obj.saleinvoiceitem_set.all()


@invoice.field("commissions")
def resolve_vc_commissions(obj, info):
    return obj.commission.all()


@contractor.field("vatStatus")
def resolve_vat_status(obj, info):
    if not obj.nip:
        return None
    if obj.nip_prefix:
        client = ZeepClient(settings.UE_VALIDATE_VAT)
        vat = client.service.checkVat(obj.nip_prefix, obj.nip)
        return {
            "status": vat["valid"],
            "url": settings.UE_VIEW_VAT,
        }
    else:
        r = requests.get(
            settings.PL_VALIDATE_VAT.format(obj.nip, str(datetime.date.today()))
        )
        vat_subject = r.json().get("result", {}).get("subject", {})
        if vat_subject is None:
            vat_valid = False
        else:
            vat_valid = vat_subject.get("statusVat", False) == "Czynny"
        return {
            "status": vat_valid,
            "url": settings.PL_VIEW_VAT,
        }


@service.field("services")
def resolve_services(obj, info):
    return obj.services.all()
