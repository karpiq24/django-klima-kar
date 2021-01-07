from django.template import Template, Context

from KlimaKar.functions import send_sms
from KlimaKar.graphql.resolvers import BaseModelFormResolver
from apps.commission.models import Commission, Component, Vehicle
from apps.commission.forms import (
    CommissionModelForm,
    CommissionItemModelForm,
    ComponentModelForm,
    VehicleModelForm,
)

from apps.commission.graphql.types import mutation
from apps.settings.models import SiteSettings


class CommissionFormResolver(BaseModelFormResolver):
    form_class = CommissionModelForm
    inlines = {"items": CommissionItemModelForm}
    inlines_parent = "commission"


@mutation.field("addCommission")
def resolve_add_commission(_, info, data):
    return CommissionFormResolver(data).process()


@mutation.field("updateCommission")
def resolve_update_commission(_, info, id, data):
    instance = Commission.objects.get(pk=id)
    if not (instance.is_editable or info.context.user.is_staff):
        return {
            "status": False,
            "errors": [{"message": "Brak dostępu do wybranego zasobu!"}],
        }
    return CommissionFormResolver(data, instance).process()


class ComponentFormResolver(BaseModelFormResolver):
    form_class = ComponentModelForm


@mutation.field("addComponent")
def resolve_add_component(_, info, data):
    return ComponentFormResolver(data).process()


@mutation.field("updateComponent")
def resolve_update_component(_, info, id, data):
    instance = Component.objects.get(pk=id)
    return ComponentFormResolver(data, instance).process()


class VehicleFormResolver(BaseModelFormResolver):
    form_class = VehicleModelForm


@mutation.field("addVehicle")
def resolve_add_vehicle(_, info, data):
    return VehicleFormResolver(data).process()


@mutation.field("updateVehicle")
def resolve_update_vehicle(_, info, id, data):
    instance = Vehicle.objects.get(pk=id)
    return VehicleFormResolver(data, instance).process()


@mutation.field("sendCommissionNotification")
def resolve_send_commission_notification(_, info, pk, phone):
    try:
        commission = Commission.objects.get(pk=pk)
    except Commission.DoesNotExist:
        return {"status": False, "message": "To zlecenie nie istnieje."}
    if commission.sent_sms:
        return {
            "status": False,
            "message": "Nie można ponownie wysłać tego powiadomienia.",
        }
    site_settings = SiteSettings.load()
    if site_settings.COMMISSION_SMS_BODY:
        message = Template(site_settings.COMMISSION_SMS_BODY).render(
            Context({"commission": commission})
        )
    else:
        return {"status": False, "message": "Treść wiadomości nie została ustawiona."}
    if send_sms(phone, message):
        commission.sent_sms = True
        commission.save()
        return {"status": True, "message": "Wiadomość została wysłana."}
    return {"status": False, "message": "Coś poszło nie tak. Spróbuj ponownie."}
