import json
import datetime

from weasyprint import HTML, CSS

from django.db import models
from django.core.validators import RegexValidator
from django.template.loader import get_template
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder

from KlimaKar.templatetags.slugify import slugify
from KlimaKar.models import TotalValueQuerySet
from apps.warehouse.models import Ware


class Contractor(models.Model):
    RELATED_MODELS = [
        ("invoicing.SaleInvoice", "contractor"),
        ("commission.Commission", "contractor"),
    ]
    MODEL_COLOR = "#00A0DF"
    MODEL_ICON = "fas fa-users"

    name = models.CharField(max_length=512, verbose_name="Nazwa")
    nip = models.CharField(max_length=32, verbose_name="NIP", blank=True, null=True)
    nip_prefix = models.CharField(
        max_length=2, verbose_name="Prefiks NIP", blank=True, null=True
    )
    address_1 = models.CharField(
        max_length=128, verbose_name="Adres", blank=True, null=True
    )
    address_2 = models.CharField(
        max_length=128, verbose_name="Adres 2", blank=True, null=True
    )
    city = models.CharField(
        max_length=128, verbose_name="Miasto", blank=True, null=True
    )
    postal_code = models.CharField(
        max_length=16, verbose_name="Kod pocztowy", blank=True, null=True
    )
    email = models.EmailField(verbose_name="Adres e-mail", blank=True, null=True)
    bdo_number = models.CharField(
        max_length=16, verbose_name="Numer BDO", blank=True, null=True
    )
    phone_1 = models.CharField(
        max_length=16, verbose_name="Numer telefonu", blank=True, null=True
    )
    phone_2 = models.CharField(
        max_length=16, verbose_name="Numer telefonu 2", blank=True, null=True
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")

    class Meta:
        verbose_name = "Kontrahent"
        verbose_name_plural = "Kontrahenci"
        ordering = ["name"]

    @property
    def phone_1_formatted(self):
        return Contractor.format_phone_number(self.phone_1) if self.phone_1 else None

    @property
    def phone_2_formatted(self):
        return Contractor.format_phone_number(self.phone_2) if self.phone_2 else None

    @property
    def phones(self):
        phones = []
        if self.phone_1:
            phones.append(self.phone_1)
        if self.phone_2:
            phones.append(self.phone_2)
        return phones

    @property
    def formatted_phones(self):
        phones = []
        if self.phone_1:
            phones.append(self.phone_1_formatted)
        if self.phone_2:
            phones.append(self.phone_2_formatted)
        return phones

    @staticmethod
    def format_phone_number(number):
        if not number:
            return number
        if len(number) == 7:
            return " ".join([number[:3], number[3:5], number[5:7]])
        if number.startswith("00"):
            return " ".join(
                [number[:4], *[number[i : i + 3] for i in range(4, len(number), 3)]]
            )
        if len(number) == 10 and number.startswith("0"):
            return " ".join([number[:3], number[3:6], number[6:8], number[8:10]])
        return " ".join([number[i : i + 3] for i in range(0, len(number), 3)])

    def as_json(self, ignore=["created_date"]):
        data = {}
        for field in Contractor._meta.get_fields():
            try:
                if field.attname in ignore:
                    continue
                if getattr(self, field.attname):
                    data[field.attname] = {
                        "label": field.verbose_name,
                        "value": getattr(self, field.attname),
                    }
            except AttributeError:
                continue
        return json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "invoicing:contractor_detail", kwargs={"pk": self.pk, "slug": slugify(self)}
        )


class SaleInvoice(models.Model):
    AUDIT_IGNORE = ["number_year", "number_value"]
    MODEL_COLOR = "#89D23A"
    MODEL_ICON = "fas fa-book"

    CASH = "1"
    CARD = "2"
    TRANSFER = "3"
    OTHER = "4"
    PAYMENT_TYPES = [
        (CASH, "gotówka"),
        (CARD, "karta"),
        (TRANSFER, "przelew"),
        (OTHER, "inna"),
    ]

    TYPE_VAT = "1"
    TYPE_PRO_FORMA = "2"
    TYPE_CORRECTIVE = "3"
    TYPE_WDT = "4"
    TYPE_WDT_PRO_FORMA = "5"
    INVOICE_TYPES = [
        (TYPE_VAT, "Faktura VAT"),
        (TYPE_PRO_FORMA, "Pro forma"),
        (TYPE_CORRECTIVE, "Korekta"),
        (TYPE_WDT, "Faktura VAT WDT"),
        (TYPE_WDT_PRO_FORMA, "Pro forma WDT"),
    ]

    issue_date = models.DateField(
        verbose_name="Data wystawienia", default=datetime.date.today
    )
    completion_date = models.DateField(
        verbose_name="Data wykonania", default=datetime.date.today
    )
    invoice_type = models.CharField(
        max_length=1, verbose_name="Rodzaj faktury", choices=INVOICE_TYPES
    )
    number = models.CharField(
        max_length=16,
        validators=[RegexValidator(r"^\d+\/\d{4}$")],
        verbose_name="Numer faktury",
    )
    number_year = models.PositiveSmallIntegerField()
    number_value = models.PositiveSmallIntegerField()
    contractor = models.ForeignKey(
        Contractor, on_delete=models.PROTECT, verbose_name="Kontrahent"
    )
    payment_type = models.CharField(
        max_length=1, verbose_name="Forma płatności", choices=PAYMENT_TYPES
    )
    payment_date = models.DateField(
        verbose_name="Termin płatności", null=True, blank=True
    )
    payment_type_other = models.CharField(
        max_length=128, verbose_name="Inna forma płatności", null=True, blank=True
    )
    payed = models.BooleanField(verbose_name="Zapłacono", default=True)
    tax_percent = models.FloatField(verbose_name="Procent podatku VAT", default=23)
    comment = models.TextField(verbose_name="Uwagi", blank=True)
    legacy = models.BooleanField(default=False, verbose_name="Faktura archiwalna")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")

    objects = TotalValueQuerySet.as_manager()
    PRICE_FIELD = "saleinvoiceitem__price"
    QUANTITY_FIELD = "saleinvoiceitem__quantity"

    class Meta:
        verbose_name = "Faktura sprzedażowa"
        verbose_name_plural = "Faktury sprzedażowe"
        ordering = ["-number_year", "-number_value"]

    def __str__(self):
        return "{} {}".format(self.get_invoice_type_display(), self.number)

    def get_absolute_url(self):
        return reverse(
            "invoicing:sale_invoice_detail",
            kwargs={"pk": self.pk, "slug": slugify(self)},
        )

    @property
    def total_value_netto(self):
        return self._meta.model.objects.filter(pk=self.pk).total(price_type="netto")

    @property
    def total_value_brutto(self):
        return self._meta.model.objects.filter(pk=self.pk).total(price_type="brutto")

    @property
    def total_value_tax(self):
        return self.total_value_brutto - self.total_value_netto

    @property
    def corrected_invoice(self):
        return CorrectiveSaleInvoice.objects.get(original_invoice=self)

    def save(self, *args, **kwargs):
        invoice_type = self.invoice_type
        invoices = SaleInvoice.objects.filter(invoice_type=invoice_type)
        if invoice_type == SaleInvoice.TYPE_VAT:
            invoices = (
                invoices | SaleInvoice.objects.filter(invoice_type=SaleInvoice.TYPE_WDT)
            ).distinct()
        elif invoice_type == SaleInvoice.TYPE_WDT:
            invoices = (
                invoices | SaleInvoice.objects.filter(invoice_type=SaleInvoice.TYPE_VAT)
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
                | SaleInvoice.objects.filter(invoice_type=SaleInvoice.TYPE_PRO_FORMA)
            ).distinct()
        if self.pk:
            invoices = invoices.exclude(pk=self.pk)
        if invoices.filter(number=self.number).exists():
            raise ValueError("number", "Faktura o tym numerze już istnieje.")

        number_data = self.number.split("/")
        self.number_value = int(number_data[0])
        self.number_year = int(number_data[1])
        if not self.pk and self.payment_date:
            self.payed = False
        super().save(*args, **kwargs)

    def generate_pdf(self, print_version=False):
        if self.invoice_type == self.TYPE_CORRECTIVE:
            template = get_template("invoicing/corrective_invoice.html")
        else:
            template = get_template("invoicing/invoice.html")
        rendered_tpl = template.render({"invoice": self}).encode()
        documents = []
        documents.append(
            HTML(string=rendered_tpl).render(
                stylesheets=[CSS(filename="KlimaKar/static/css/invoice.css")]
            )
        )
        if print_version:
            documents.append(
                HTML(string=rendered_tpl).render(
                    stylesheets=[CSS(filename="KlimaKar/static/css/invoice.css")]
                )
            )
        all_pages = []
        for doc in documents:
            for p in doc.pages:
                all_pages.append(p)
        return documents[0].copy(all_pages).write_pdf()


class RefrigerantWeights(models.Model):
    sale_invoice = models.OneToOneField(
        SaleInvoice, on_delete=models.CASCADE, verbose_name="Faktura sprzedażowa"
    )
    r134a = models.PositiveIntegerField(verbose_name="Czynnik R134a", default=0)
    r1234yf = models.PositiveIntegerField(verbose_name="Czynnik R1234yf", default=0)
    r12 = models.PositiveIntegerField(verbose_name="Czynnik R12", default=0)
    r404 = models.PositiveIntegerField(verbose_name="Czynnik R404", default=0)

    class Meta:
        verbose_name = "Waga czynników"
        verbose_name_plural = "Wagi czynników"
        ordering = ["sale_invoice"]

    def __str__(self):
        return "Waga czynników dla faktury {}".format(self.sale_invoice)

    def get_absolute_url(self):
        return reverse(
            "invoicing:sale_invoice_detail",
            kwargs={"pk": self.sale_invoice.pk, "slug": slugify(self.sale_invoice)},
        )


class ServiceTemplate(models.Model):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"

    BUTTON_COLORS = [
        (PRIMARY, "Niebieski"),
        (SECONDARY, "Szary"),
        (SUCCESS, "Zielony"),
        (DANGER, "Czerwony"),
        (WARNING, "Żółty"),
        (INFO, "Cyjanowy"),
        (LIGHT, "Biały"),
        (DARK, "Czarny"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nazwa usługi/towaru")
    description = models.CharField(
        max_length=255, verbose_name="Opis usługi/towaru", blank=True, null=True
    )
    quantity = models.IntegerField(verbose_name="Ilość", blank=True, null=True)
    price_netto = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name="Cena netto", blank=True, null=True
    )
    price_brutto = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Cena brutto",
        blank=True,
        null=True,
    )
    ware = models.ForeignKey(
        Ware, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Towar"
    )
    display_as_button = models.BooleanField(
        default=False, verbose_name="Wyświetl jako przycisk"
    )
    button_name = models.CharField(
        max_length=255, verbose_name="Nazwa przycisku", blank=True, null=True
    )
    button_color = models.CharField(
        max_length=10,
        choices=BUTTON_COLORS,
        default=PRIMARY,
        verbose_name="Kolor przycisku",
    )
    is_ware_service = models.BooleanField(
        default=False, verbose_name="Usługa z filtrem towaru"
    )
    ware_filter = models.CharField(
        max_length=255, verbose_name="Filtr nazwy towaru", blank=True, null=True,
    )
    is_group = models.BooleanField(default=False, verbose_name="Grupa usług")
    services = models.ManyToManyField(
        "invoicing.ServiceTemplate", verbose_name="Usługi", blank=True
    )

    class Meta:
        verbose_name = "Szablon usługi"
        verbose_name_plural = "Szablony usług"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "invoicing:service_template_detail",
            kwargs={"pk": self.pk, "slug": slugify(self)},
        )


class SaleInvoiceItem(models.Model):
    sale_invoice = models.ForeignKey(
        SaleInvoice, on_delete=models.CASCADE, verbose_name="Faktura sprzedażowa"
    )
    name = models.CharField(max_length=255, verbose_name="Nazwa usługi/towaru")
    description = models.CharField(
        max_length=255, verbose_name="Opis usługi/towaru", blank=True, null=True
    )
    quantity = models.IntegerField(default=1, verbose_name="Ilość")
    price_netto = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name="Cena netto"
    )
    price_brutto = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name="Cena brutto"
    )
    ware = models.ForeignKey(
        Ware, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Towar"
    )

    class Meta:
        verbose_name = "Pozycja faktury sprzedażowej"
        verbose_name_plural = "Pozycje faktur sprzedażowych"
        ordering = ["sale_invoice"]

    def __str__(self):
        return "{} - {}".format(self.sale_invoice.number, self.name)

    def get_absolute_url(self):
        return reverse(
            "invoicing:sale_invoice_detail",
            kwargs={"pk": self.sale_invoice.pk, "slug": slugify(self.sale_invoice)},
        )

    @property
    def total_netto(self):
        return self.price_netto * self.quantity

    @property
    def total_brutto(self):
        return self.price_brutto * self.quantity


class CorrectiveSaleInvoice(SaleInvoice):
    original_invoice = models.ForeignKey(
        SaleInvoice,
        on_delete=models.CASCADE,
        verbose_name="Oryginalna faktura",
        related_name="%(class)s_original_invoice",
    )
    reason = models.TextField(max_length=255, verbose_name="Powód wystawienia korekty")

    class Meta:
        verbose_name = "Korekta faktury sprzedażowej"
        verbose_name_plural = "Korekty faktur sprzedażowych"
        ordering = ["-number"]

    def get_absolute_url(self):
        return reverse(
            "invoicing:sale_invoice_detail",
            kwargs={"pk": self.pk, "slug": slugify(self)},
        )

    @property
    def diffrence_netto(self):
        return self.total_value_netto - self.original_invoice.total_value_netto

    @property
    def diffrence_brutto(self):
        return self.total_value_brutto - self.original_invoice.total_value_brutto

    @property
    def diffrence_tax(self):
        return self.total_value_tax - self.original_invoice.total_value_tax
