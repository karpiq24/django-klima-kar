import re
from django.db.models import Q
from django.template import Template, Context

from KlimaKar.functions import strip_accents
from KlimaKar.graphql.utils import get_paginated_results
from apps.commission.functions import decode_mpojazd, decode_aztec_code
from apps.commission.models import Commission, Vehicle, Component
from apps.commission.graphql import query, commission, vehicle, component
from apps.settings.models import SiteSettings


@query.field("commissions")
def resolve_commissions(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        try:
            return qs.filter(pk=search)
        except ValueError:
            return qs.filter(vc_name__icontains=search)

    return get_paginated_results(
        Commission.objects.all(), pagination, filters, custom_filter=search_filter
    )


@query.field("vehicles")
def resolve_vehicles(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        q = re.sub(r"[\W_]+", "", search)
        return qs.filter(
            Q(brand__icontains=search)
            | Q(model__icontains=search)
            | Q(vin__icontains=q)
            | Q(registration_plate__icontains=q)
        )

    return get_paginated_results(
        Vehicle.objects.all(), pagination, filters, custom_filter=search_filter
    )


@query.field("components")
def resolve_components(_, info, pagination=None, filters=None, search=None):
    def search_filter(qs):
        if not search:
            return qs
        return qs.filter(
            Q(model__icontains=search)
            | Q(serial_number__icontains=search)
            | Q(catalog_number__icontains=search)
        )

    return get_paginated_results(
        Component.objects.all(), pagination, filters, custom_filter=search_filter
    )


@query.field("decode")
def resolve_decode_scanned_code(_, info, code, create):
    code = code.strip()
    if ";" in code:
        return decode_mpojazd(code, create)
    return decode_aztec_code(code, create)


@commission.field("saleInvoices")
def resolve_contractors(obj, info):
    return obj.sale_invoices.all()


@commission.field("items")
def resolve_items(obj, info):
    return obj.commissionitem_set.all()


@commission.field("smsBody")
def resolve_sms_body(obj, info):
    site_settings = SiteSettings.load()
    if site_settings.COMMISSION_SMS_BODY:
        message = Template(site_settings.COMMISSION_SMS_BODY).render(
            Context({"commission": obj})
        )
        return strip_accents(message)
    return None


@vehicle.field("commissions")
@component.field("commissions")
def resolve_vc_commissions(obj, info):
    return obj.commission_set.all()


@component.field("get_component_type_display")
def resolve_get_component_type_display(obj, info):
    return obj.get_component_type_display()


@vehicle.field("get_fuel_type_display")
def resolve_get_fuel_type_display(obj, info):
    return obj.get_fuel_type_display()


@commission.field("get_absolute_url")
@component.field("get_absolute_url")
@vehicle.field("get_absolute_url")
def resolve_get_absolute_url(obj, info):
    return obj.get_absolute_url()


@component.field("last_commission")
@vehicle.field("last_commission")
def resolve_last_commission(obj, info):
    return obj.commission_set.first()
