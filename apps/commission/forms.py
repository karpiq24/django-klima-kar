import datetime

from dal import autocomplete
from extra_views import InlineFormSet

from django import forms
from django.utils.crypto import get_random_string

from KlimaKar.forms import ToggleInput
from KlimaKar.widgets import PrettySelect
from apps.commission.models import Vehicle, Component, Commission, CommissionItem
from apps.invoicing.models import Contractor
from apps.warehouse.models import Ware


class VehicleModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["brand"].widget.attrs.update({"placeholder": "Podaj markę"})
        self.fields["model"].widget.attrs.update({"placeholder": "Podaj model"})
        self.fields["registration_plate"].widget.attrs.update(
            {"placeholder": "Podaj numer rejestracyjny"}
        )
        self.fields["vin"].widget.attrs.update({"placeholder": "Podaj numer VIN"})
        self.fields["registration_date"].widget.attrs.update(
            {"class": "date-input", "placeholder": "Wybierz datę"}
        )

    def clean_registration_plate(self):
        data = self.cleaned_data["registration_plate"]
        if data:
            data = data.replace(" ", "").upper()
        return data

    def clean_vin(self):
        data = self.cleaned_data["vin"]
        if data:
            data = data.upper()
        return data

    class Meta:
        model = Vehicle
        fields = [
            "registration_plate",
            "brand",
            "model",
            "vin",
            "engine_volume",
            "engine_power",
            "production_year",
            "fuel_type",
            "registration_date",
        ]


class ComponentModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["model"].widget.attrs.update({"placeholder": "Podaj model"})
        self.fields["serial_number"].widget.attrs.update(
            {"placeholder": "Podaj numer seryjny"}
        )
        self.fields["catalog_number"].widget.attrs.update(
            {"placeholder": "Podaj numer katalogowy"}
        )

    class Meta:
        model = Component
        fields = ["component_type", "model", "serial_number", "catalog_number"]


class CommissionModelForm(forms.ModelForm):
    contractor = forms.ModelChoiceField(
        label="Kontrahent",
        queryset=Contractor.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="invoicing:contractor_autocomplete_create",
            attrs={"data-placeholder": "Podaj nazwę, NIP albo numer telefonu"},
        ),
        required=False,
    )
    vehicle = forms.ModelChoiceField(
        label="Pojazd",
        queryset=Vehicle.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="commission:vehicle_autocomplete_create",
            attrs={"data-placeholder": "Podaj numer rejestracyjny"},
        ),
        required=False,
    )
    component = forms.ModelChoiceField(
        label="Podzespół",
        queryset=Component.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="commission:component_autocomplete_create",
            attrs={"data-placeholder": "Podaj model, numer seryjny albo katalogowy"},
        ),
        required=False,
    )

    upload_key = forms.CharField(
        label="Klucz wysyłania plików", widget=forms.HiddenInput(), required=False
    )
    generate_pdf = forms.BooleanField(
        label="Wydruk po zapisie", widget=forms.HiddenInput(), required=False
    )

    def __init__(self, *args, **kwargs):
        self.commission_type = kwargs.pop("commission_type", None)
        super().__init__(*args, **kwargs)
        if not self.commission_type and kwargs.get("data"):
            self.commission_type = kwargs["data"].get("commission_type")
        if not self.commission_type and self.instance and self.instance.commission_type:
            self.commission_type = self.instance.commission_type
        self.fields["vc_name"].widget.attrs.update({"placeholder": "Podaj nazwę"})
        self.fields["start_date"].widget.attrs.update(
            {"class": "date-input", "placeholder": "Wybierz datę"}
        )
        self.fields["end_date"].widget.attrs.update(
            {"class": "date-input", "placeholder": "Wybierz datę", "disabled": True}
        )
        if self.commission_type == Commission.VEHICLE:
            self.fields.pop("component")
            self.fields["vc_name"].label = "Nazwa pojazdu"
        elif self.commission_type == Commission.COMPONENT:
            self.fields.pop("vehicle")
            self.fields["vc_name"].label = "Nazwa podzespołu"
        else:
            self.fields.pop("vehicle")
            self.fields.pop("component")
            self.fields["vc_name"].label = "Nazwa"
        self.fields["upload_key"].initial = get_random_string(length=32)

    def clean(self):
        status = self.cleaned_data["status"]
        end_date = self.cleaned_data["end_date"]
        if status in [Commission.DONE, Commission.CANCELLED] and not end_date:
            self.cleaned_data["end_date"] = datetime.date.today()
        vc = self.cleaned_data.get("vehicle", self.cleaned_data.get("component"))
        if vc:
            self.cleaned_data["vc_name"] = str(vc)
        return self.cleaned_data

    class Meta:
        model = Commission
        fields = [
            "vc_name",
            "vehicle",
            "component",
            "contractor",
            "description",
            "status",
            "start_date",
            "end_date",
            "commission_type",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "commission_type": forms.HiddenInput(),
            "status": PrettySelect(),
        }


class CommissionFastModelForm(forms.ModelForm):
    value = forms.DecimalField(
        label="Cena", max_digits=7, decimal_places=2, localize=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vc_name"].widget.attrs.update({"placeholder": "Podaj nazwę"})
        self.fields["description"].required = True

    class Meta:
        model = Commission
        fields = [
            "commission_type",
            "vc_name",
            "description",
            "status",
            "start_date",
            "end_date",
            "value",
        ]
        widgets = {
            "description": forms.TextInput(attrs={"placeholder": "Podaj krótki opis"}),
            "status": forms.HiddenInput(),
            "start_date": forms.HiddenInput(),
            "end_date": forms.HiddenInput(),
            "commission_type": PrettySelect(),
        }


class CommissionItemModelForm(forms.ModelForm):
    ware = forms.ModelChoiceField(
        label="Towar",
        queryset=Ware.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url="warehouse:ware_autocomplete"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"placeholder": "Podaj nazwę", "class": "item-name"}
        )
        self.fields["description"].widget.attrs.update(
            {"placeholder": "Podaj opis", "class": "item-description"}
        )
        self.fields["quantity"].widget.attrs.update(
            {"placeholder": "Ilość", "class": "item-quantity"}
        )
        self.fields["price"].widget.attrs.update(
            {"placeholder": "Cena", "class": "item-price"}
        )
        self.fields["ware"].widget.attrs.update(
            {"data-placeholder": "Wybierz towar", "class": "item-ware"}
        )

    class Meta:
        model = CommissionItem
        fields = ["name", "description", "quantity", "price", "ware"]
        localized_fields = ["price", "quantity"]


class CommissionItemInline(InlineFormSet):
    model = CommissionItem
    form_class = CommissionItemModelForm
    factory_kwargs = {"extra": 20}


class CommissionEmailForm(forms.Form):
    recipient = forms.EmailField(label="Do")
    subject = forms.CharField(label="Temat")
    message = forms.CharField(widget=forms.Textarea, label="Treść")
    commission = forms.ModelChoiceField(
        queryset=Commission.objects.none(), widget=forms.HiddenInput()
    )
    include_description = forms.BooleanField(
        label="Opis zlecenia w pliku", widget=ToggleInput, initial=True, required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commission"].queryset = Commission.objects.filter(
            pk=self.initial["commission"].pk
        )
