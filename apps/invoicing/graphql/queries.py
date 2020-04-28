from django.db.models import Q

from KlimaKar.graphql.utils import get_paginated_results
from apps.invoicing.models import Contractor, SaleInvoice, ServiceTemplate
from apps.invoicing.graphql import query, invoice
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
