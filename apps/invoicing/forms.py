from dal import autocomplete
from extra_views import InlineFormSet

from django import forms
from django.urls import reverse
from django.forms.models import model_to_dict
from django.db.models import Q

from KlimaKar.widgets import PrettySelect
from KlimaKar.forms import ToggleInput

from apps.invoicing.models import (
    Contractor,
    SaleInvoice,
    SaleInvoiceItem,
    ServiceTemplate,
    RefrigerantWeights,
    CorrectiveSaleInvoice,
)
from apps.warehouse.models import Ware
from apps.commission.models import CommissionItem


class EnableDisableDateInput(forms.DateInput):
    template_name = "invoicing/sale_invoice/date_field.html"


class SaleInvoiceModelForm(forms.ModelForm):
    contractor = forms.ModelChoiceField(
        label="Kontrahent",
        queryset=Contractor.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="invoicing:contractor_autocomplete_create"
        ),
    )
    generate_pdf = forms.BooleanField(
        label="Wydruk po zapisie", widget=forms.HiddenInput(), required=False
    )
    contractor_modified = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number"].widget.attrs.update(
            {"placeholder": "Podaj numer faktury"}
        )
        self.fields["contractor"].widget.attrs.update(
            {"data-placeholder": "Podaj nazwę, NIP albo numer telefonu"}
        )
        self.fields["issue_date"].widget.attrs.update({"placeholder": "Wybierz datę"})
        self.fields["issue_date"].widget.attrs.update({"class": "date-input"})
        self.fields["completion_date"].widget.attrs.update(
            {"placeholder": "Wybierz datę"}
        )
        self.fields["completion_date"].widget.attrs.update({"class": "date-input"})
        self.fields["payment_date"].widget.attrs.update({"placeholder": "Wybierz datę"})
        self.fields["payment_date"].widget.attrs.update({"class": "date-input"})
        self.fields["payment_type_other"].widget.attrs.update(
            {"placeholder": "Podaj formę płatności"}
        )

        contractor = self.initial.get("contractor")
        if contractor:
            self.fields["contractor"].initial = contractor

    def clean(self):
        cleaned_data = super().clean()
        number = cleaned_data["number"]
        if self.instance and self.instance.number == number:
            return cleaned_data
        else:
            invoice_type = cleaned_data["invoice_type"]
            invoices = SaleInvoice.objects.filter(invoice_type=invoice_type)
            if invoice_type == SaleInvoice.TYPE_VAT:
                invoices = (
                    invoices
                    | SaleInvoice.objects.filter(invoice_type=SaleInvoice.TYPE_WDT)
                ).distinct()
            elif invoice_type == SaleInvoice.TYPE_WDT:
                invoices = (
                    invoices
                    | SaleInvoice.objects.filter(invoice_type=SaleInvoice.TYPE_VAT)
                ).distinct()
            elif invoice_type == SaleInvoice.TYPE_PRO_FORMA:
                invoices = (
                    invoices
                    | SaleInvoice.objects.filter(
                        invoice_type=SaleInvoice.TYPE_WDT_PRO_FORMA
                    )
                ).distinct()
            elif invoice_type == SaleInvoice.TYPE_WDT_PRO_FORMA:
                invoices = (
                    invoices
                    | SaleInvoice.objects.filter(
                        invoice_type=SaleInvoice.TYPE_PRO_FORMA
                    )
                ).distinct()
            if invoices.filter(number=number).exists():
                self.add_error("number", "Faktura o tym numerze już istnieje.")
        return cleaned_data

    class Meta:
        model = SaleInvoice
        fields = [
            "issue_date",
            "completion_date",
            "invoice_type",
            "number",
            "contractor",
            "payment_type",
            "payment_date",
            "payment_type_other",
            "comment",
            "tax_percent",
        ]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 2}),
            "payment_date": EnableDisableDateInput(),
            "invoice_type": forms.HiddenInput(),
            "tax_percent": forms.HiddenInput(),
            "payment_type": PrettySelect(),
        }


class CorrectiveSaleInvoiceModelForm(SaleInvoiceModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contractor"].disabled = True
        self.fields["completion_date"].disabled = True

    class Meta:
        model = CorrectiveSaleInvoice
        fields = [
            "issue_date",
            "completion_date",
            "invoice_type",
            "number",
            "contractor",
            "payment_type",
            "payment_date",
            "payment_type_other",
            "comment",
            "tax_percent",
            "original_invoice",
            "reason",
        ]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 2}),
            "reason": forms.Textarea(attrs={"rows": 2}),
            "payment_date": EnableDisableDateInput(),
            "invoice_type": forms.HiddenInput(),
            "original_invoice": forms.HiddenInput(),
            "tax_percent": forms.HiddenInput(),
            "payment_type": PrettySelect(),
        }


class NipInput(forms.TextInput):
    template_name = "invoicing/contractor/nip_field.html"

    class Media:
        js = ("js/invoicing/contractor-gus.js",)

    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop("prefix")
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs, *args, **kwargs):
        context = super().get_context(name, value, attrs)
        context["url"] = reverse("invoicing:contractor_gus")
        context["prefix"] = self.prefix
        return context


class ContractorModelForm(forms.ModelForm):
    ignore_duplicated_phone = forms.CharField(
        required=False, widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.is_locked:
            self.fields["nip"].disabled = True
            self.fields[
                "nip"
            ].help_text = "Ten kontrahent ma przypisaną fakturę, zamiast edytować numer NIP, dodaj nowego kontrahenta."

        self.fields["name"].widget.attrs.update({"placeholder": "Podaj nazwę"})
        if self.instance and self.instance.nip_prefix:
            nip_prefix = self.instance.nip_prefix
        else:
            nip_prefix = ""
        self.fields["nip"].widget = NipInput(prefix=nip_prefix)
        self.fields["nip"].widget.attrs.update({"placeholder": "Podaj NIP"})
        self.fields["address_1"].widget.attrs.update({"placeholder": "Podaj adres"})
        self.fields["address_2"].widget.attrs.update({"placeholder": "Podaj adres"})
        self.fields["city"].widget.attrs.update({"placeholder": "Podaj miasto"})
        self.fields["postal_code"].widget.attrs.update(
            {"placeholder": "Podaj kod pocztowy"}
        )
        self.fields["email"].widget.attrs.update({"placeholder": "Podaj adres e-mail"})
        self.fields["phone_1"].widget.attrs.update(
            {"placeholder": "Podaj numer telefonu"}
        )
        self.fields["phone_2"].widget.attrs.update(
            {"placeholder": "Podaj numer telefonu"}
        )
        self.fields["bdo_number"].widget.attrs.update(
            {"placeholder": "Podaj numer BDO"}
        )

    class Meta:
        model = Contractor
        fields = [
            "nip_prefix",
            "nip",
            "name",
            "city",
            "postal_code",
            "address_1",
            "address_2",
            "email",
            "phone_1",
            "phone_2",
            "bdo_number",
            "ignore_duplicated_phone",
        ]
        widgets = {"nip_prefix": forms.HiddenInput()}

    class Media:
        js = ("js/invoicing/contractor-form.js",)

    def clean_nip(self):
        nip = self.cleaned_data["nip"]
        if self.instance and self.instance.is_locked:
            return self.instance.nip
        return nip

    def clean_nip_prefix(self):
        nip_prefix = self.cleaned_data["nip_prefix"]
        if self.instance and self.instance.is_locked:
            return self.instance.nip_prefix
        return nip_prefix

    def clean_phone_1(self):
        data = self.cleaned_data["phone_1"]
        if data:
            data = data.replace(" ", "")
            if not bool(self.data.get("ignore_duplicated_phone", "False")):
                self._check_duplicate_phones(data)
        return data

    def clean_phone_2(self):
        data = self.cleaned_data["phone_2"]
        if data:
            data = data.replace(" ", "")
            if not bool(self.data.get("ignore_duplicated_phone", "False")):
                self._check_duplicate_phones(data)
        return data

    def _check_duplicate_phones(self, number):
        queryset = Contractor.objects.filter(Q(phone_1=number) | Q(phone_2=number))
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError(
                "Podany numer jest już przypisany do innego kontrahenta.",
                code="duplicated_phone",
                params=[queryset.first().as_json()],
            )


class SaleInvoiceItemModelForm(forms.ModelForm):
    ware = forms.ModelChoiceField(
        label="Towar",
        queryset=Ware.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url="warehouse:ware_autocomplete"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"placeholder": "Podaj nazwę"})
        self.fields["name"].widget.attrs.update({"class": "item-name"})
        self.fields["description"].widget.attrs.update({"placeholder": "Podaj opis"})
        self.fields["description"].widget.attrs.update({"class": "item-description"})
        self.fields["quantity"].widget.attrs.update({"placeholder": "Ilość"})
        self.fields["quantity"].widget.attrs.update({"class": "item-quantity"})
        self.fields["price_netto"].widget.attrs.update({"placeholder": "Netto"})
        self.fields["price_netto"].widget.attrs.update({"class": "item-netto"})
        self.fields["price_brutto"].widget.attrs.update({"placeholder": "Brutto"})
        self.fields["price_brutto"].widget.attrs.update({"class": "item-brutto"})
        self.fields["ware"].widget.attrs.update({"data-placeholder": "Wybierz towar"})
        self.fields["ware"].widget.attrs.update({"class": "item-ware"})

    class Meta:
        model = SaleInvoiceItem
        fields = [
            "name",
            "description",
            "quantity",
            "price_netto",
            "price_brutto",
            "ware",
        ]
        localized_fields = ["price_netto", "price_brutto", "quantity"]


class SaleInvoiceItemsInline(InlineFormSet):
    model = SaleInvoiceItem
    form_class = SaleInvoiceItemModelForm
    factory_kwargs = {"extra": 20}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commission = self.kwargs.get("commission", None)
        self.value_type = self.kwargs.get("value_type", None)
        self.original_invoice = self.kwargs.get("original_invoice", None)

    def get_initial(self):
        if not self.object and self.original_invoice:
            items = SaleInvoiceItem.objects.filter(sale_invoice=self.original_invoice)
            initial = [model_to_dict(item) for item in items]
            return initial
        if not self.object and self.commission:
            items = CommissionItem.objects.filter(commission=self.commission)
            initial = [self._commission_item_to_dict(item) for item in items]
            return initial
        return self.initial[:]

    def _commission_item_to_dict(self, item):
        d = model_to_dict(item, exclude=["id", "commission"])
        if self.value_type == "netto":
            d["price_netto"] = d.pop("price")
        else:
            d["price_brutto"] = d.pop("price")
        return d


class AlwaysChangedModelForm(forms.ModelForm):
    """
    Force saving RefrigerantWeightsInline formset with default values
    """

    def has_changed(self):
        return True


class RefrigerantWeightsInline(InlineFormSet):
    model = RefrigerantWeights
    factory_kwargs = {"max_num": 1, "min_num": 1, "extra": 0, "can_delete": False}
    form_class = AlwaysChangedModelForm
    fields = "__all__"


class ServiceTemplateModelForm(forms.ModelForm):
    ware = forms.ModelChoiceField(
        label="Towar",
        queryset=Ware.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url="warehouse:ware_autocomplete"),
    )
    services = forms.ModelMultipleChoiceField(
        label="Usługi",
        queryset=ServiceTemplate.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url="invoicing:service_template_autocomplete"
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"placeholder": "Podaj nazwę"})
        self.fields["ware_filter"].widget.attrs.update(
            {"placeholder": "Podaj nazwę towaru"}
        )
        self.fields["button_name"].widget.attrs.update(
            {"placeholder": "Podaj nazwę przycisku"}
        )
        self.fields["name"].widget.attrs.update({"class": "item-name"})
        self.fields["description"].widget.attrs.update({"placeholder": "Podaj opis"})
        self.fields["description"].widget.attrs.update({"class": "item-description"})
        self.fields["quantity"].widget.attrs.update({"placeholder": "Podaj ilość"})
        self.fields["quantity"].widget.attrs.update({"class": "item-quantity"})
        self.fields["price_netto"].widget.attrs.update(
            {"placeholder": "Podaj cenę netto"}
        )
        self.fields["price_netto"].widget.attrs.update({"class": "item-netto"})
        self.fields["price_brutto"].widget.attrs.update(
            {"placeholder": "Podaj cenę brutto"}
        )
        self.fields["price_brutto"].widget.attrs.update({"class": "item-brutto"})
        self.fields["ware"].widget.attrs.update({"data-placeholder": "Wybierz towar"})
        self.fields["ware"].widget.attrs.update({"class": "item-ware"})
        self.fields["services"].widget.attrs.update(
            {"data-placeholder": "Wybierz usługi"}
        )

    class Meta:
        model = ServiceTemplate
        fields = [
            "name",
            "description",
            "quantity",
            "price_netto",
            "price_brutto",
            "ware",
            "button_color",
            "display_as_button",
            "button_name",
            "is_ware_service",
            "ware_filter",
            "is_group",
            "services",
        ]
        widgets = {
            "display_as_button": ToggleInput,
            "is_ware_service": ToggleInput,
            "is_group": ToggleInput,
        }
        localized_fields = ["price_netto", "price_brutto", "quantity"]


class EmailForm(forms.Form):
    recipient = forms.EmailField(label="Do")
    subject = forms.CharField(label="Temat")
    message = forms.CharField(widget=forms.Textarea, label="Treść")
    sale_invoice = forms.ModelChoiceField(
        queryset=SaleInvoice.objects.none(), widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sale_invoice"].queryset = SaleInvoice.objects.filter(
            pk=self.initial["sale_invoice"].pk
        )
