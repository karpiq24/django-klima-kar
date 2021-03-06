import datetime

from django.contrib.contenttypes.fields import GenericRelation
from weasyprint import HTML, CSS

from django.db import models
from django.template.loader import get_template
from django.dispatch import receiver
from django.urls import reverse

from KlimaKar.templatetags.slugify import slugify
from KlimaKar.models import TotalValueQuerySet
from apps.annotations.models import Annotation
from apps.audit.functions import get_audit_logs
from apps.invoicing.models import Contractor, SaleInvoice
from apps.mycloudhome.models import MyCloudHomeFile, MyCloudHomeDirectoryModel
from apps.search.models import SearchDocument
from apps.warehouse.models import Ware


class Vehicle(models.Model):
    RELATED_MODELS = [("commission.Commission", "vehicle")]
    MODEL_COLOR = "#F09300"
    MODEL_ICON = "fas fa-car"

    PETROL = "P"
    DIESEL = "D"
    MIXED = "M"
    LPG = "LPG"
    CNG = "CNG"
    HYDROGEN = "H"
    LNG = "LNG"
    BIODIESEL = "BD"
    ETHANOL = "E85"
    ELECTRIC = "EE"
    PETROL_ELECTRIC = "P EE"
    OTHER = "999"

    FUEL_CHOICES = [
        (PETROL, "benzyna"),
        (DIESEL, "olej napędowy"),
        (MIXED, "mieszanka (paliwo-olej)"),
        (LPG, "gaz płynny (propan-butan)"),
        (CNG, "gaz ziemny sprężony (metan)"),
        (HYDROGEN, "wodór"),
        (LNG, "gaz ziemny skroplony (metan)"),
        (BIODIESEL, "biodiesel"),
        (ETHANOL, "etanol"),
        (ELECTRIC, "energia elektryczna"),
        (PETROL_ELECTRIC, "benzyna, energia elektryczna"),
        (OTHER, "inne"),
    ]

    registration_plate = models.CharField(
        max_length=32, unique=True, verbose_name="Numer rejestracyjny"
    )
    vin = models.CharField(
        max_length=32, blank=True, null=True, unique=True, verbose_name="Numer VIN"
    )
    brand = models.CharField(max_length=64, verbose_name="Marka")
    model = models.CharField(max_length=64, blank=True, null=True, verbose_name="Model")
    engine_volume = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Pojemność silnika (cm3)"
    )
    engine_power = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Moc silnika (kW)"
    )
    production_year = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Rok produkcji"
    )
    fuel_type = models.CharField(
        max_length=4,
        choices=FUEL_CHOICES,
        verbose_name="Rodzaj paliwa",
        null=True,
        blank=True,
    )
    registration_date = models.DateField(
        verbose_name="Data pierwszej rejestracji", null=True, blank=True
    )

    annotations = GenericRelation(Annotation, related_query_name="vehicle")
    search = GenericRelation(SearchDocument, related_query_name="vehicle")

    class Meta:
        verbose_name = "Pojazd"
        verbose_name_plural = "Pojazdy"
        ordering = ["brand", "model", "id"]

    def __str__(self):
        return "{}{}{}{}".format(
            self.brand,
            " {}".format(self.model) if self.model else "",
            " {}".format(self.registration_plate) if self.registration_plate else "",
            " ({})".format(self.production_year) if self.production_year else "",
        )

    def get_absolute_url(self):
        return reverse(
            "commission:vehicle_detail", kwargs={"pk": self.pk, "slug": slugify(self)}
        )

    def get_logs(self):
        return get_audit_logs(self)


@receiver(models.signals.post_save, sender=Vehicle)
def change_vehicle_commissions_name(sender, instance, **kwargs):
    instance.commission_set.update(vc_name=str(instance))


class Component(models.Model):
    RELATED_MODELS = [("commission.Commission", "component")]
    MODEL_COLOR = "#13BB72"
    MODEL_ICON = "fas fa-microchip"
    COMPRESSOR = "CO"
    HEATER = "HE"
    OTHER = "OT"
    TYPE_CHOICES = [
        (COMPRESSOR, "Sprężarka"),
        (HEATER, "Ogrzewanie postojowe"),
        (OTHER, "Inny"),
    ]

    component_type = models.CharField(
        max_length=2, choices=TYPE_CHOICES, verbose_name="Rodzaj"
    )
    model = models.CharField(max_length=64, blank=True, null=True, verbose_name="Model")
    serial_number = models.CharField(
        max_length=64, blank=True, null=True, verbose_name="Numer seryjny"
    )
    catalog_number = models.CharField(
        max_length=64, blank=True, null=True, verbose_name="Numer katalogowy"
    )

    annotations = GenericRelation(Annotation, related_query_name="component")
    search = GenericRelation(SearchDocument, related_query_name="component")

    class Meta:
        verbose_name = "Podzespół"
        verbose_name_plural = "Podzespoły"
        ordering = ["component_type"]

    def __str__(self):
        return "{}{}{}{}".format(
            self.get_component_type_display()
            if self.component_type != self.OTHER
            else "",
            " {}".format(self.model) if self.model else "",
            " {}".format(self.serial_number) if self.serial_number else "",
            " {}".format(self.catalog_number) if self.catalog_number else "",
        )

    def get_absolute_url(self):
        return reverse(
            "commission:component_detail", kwargs={"pk": self.pk, "slug": slugify(self)}
        )

    def get_logs(self):
        return get_audit_logs(self)


@receiver(models.signals.post_save, sender=Component)
def change_component_commissions_name(sender, instance, **kwargs):
    instance.commission_set.update(vc_name=str(instance))


class Commission(MyCloudHomeDirectoryModel):
    AUDIT_IGNORE = ["upload", "mch_id", "scanning"]
    MODEL_COLOR = "#427BD2"
    MODEL_ICON = "fas fa-tasks"
    DIRECTORY_ID_FIELD = "COMMISSION_DIR_ID"

    OPEN = "OP"
    READY = "RE"
    DONE = "DO"
    CANCELLED = "CA"
    ON_HOLD = "HO"
    STATUS_CHOICES = [
        (OPEN, "Otwarte"),
        (READY, "Gotowe"),
        (DONE, "Zamknięte"),
        (ON_HOLD, "Wstrzymane"),
        (CANCELLED, "Anulowane"),
    ]
    VEHICLE = "VH"
    COMPONENT = "CO"
    COMMISSION_TYPES = [(VEHICLE, "Pojazd"), (COMPONENT, "Podzespół")]

    commission_type = models.CharField(
        max_length=2,
        choices=COMMISSION_TYPES,
        default=VEHICLE,
        verbose_name="Rodzaj zlecenia",
    )
    vc_name = models.CharField(max_length=128, verbose_name="Nazwa pojazdu/podzespołu")
    vehicle = models.ForeignKey(
        Vehicle, blank=True, null=True, on_delete=models.PROTECT, verbose_name="Pojazd"
    )
    component = models.ForeignKey(
        Component,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="Podzespół",
    )
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Kontrahent",
    )
    sale_invoices = models.ManyToManyField(
        SaleInvoice, blank=True, verbose_name="Faktury sprzedażowe"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Opis")
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default=OPEN, verbose_name="Status"
    )
    start_date = models.DateField(
        verbose_name="Data przyjęcia", default=datetime.date.today
    )
    end_date = models.DateField(blank=True, null=True, verbose_name="Data zamknięcia")
    sent_sms = models.BooleanField(
        verbose_name="Powiadomienie SMS zostało wysłane", default=False
    )

    annotations = GenericRelation(Annotation, related_query_name="commission")
    search = GenericRelation(SearchDocument, related_query_name="commission")

    objects = TotalValueQuerySet.as_manager()
    PRICE_FIELD = "commissionitem__price"
    QUANTITY_FIELD = "commissionitem__quantity"

    class Meta:
        verbose_name = "Zlecenie"
        verbose_name_plural = "Zlecenia"
        ordering = ["-pk"]

    def __str__(self):
        name = (
            str(self.vehicle)
            if self.vehicle
            else str(self.component)
            if self.component
            else self.vc_name
        )
        return "Zlecenie {}: {}".format(self.number, name)

    def get_absolute_url(self):
        return reverse(
            "commission:commission_detail",
            kwargs={"pk": self.pk, "slug": slugify(self)},
        )

    def save(self, *args, **kwargs):
        if self.status in [self.DONE, self.CANCELLED] and not self.end_date:
            self.end_date = datetime.date.today()
        super().save(*args, **kwargs)

    @property
    def number(self):
        return self.pk

    @property
    def value(self):
        return self._meta.model.objects.filter(pk=self.pk).total()

    @property
    def has_notes(self):
        return self.annotations.exists()

    @property
    def is_editable(self):
        return not (self.end_date and self.end_date < datetime.date.today())

    def generate_pdf(self, include_description=True):
        template = get_template("commission/pdf_commission.html")
        rendered_tpl = template.render(
            {"commission": self, "include_description": include_description}
        ).encode()
        documents = []
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

    def get_files(self):
        return self.commissionfile_set.all()

    def get_logs(self):
        return get_audit_logs(
            self,
            m2one=[
                {
                    "key": "commission",
                    "objects": self.commissionitem_set.all(),
                    "model": CommissionItem,
                },
                {
                    "key": "commission",
                    "objects": self.commissionfile_set.all(),
                    "model": CommissionFile,
                },
            ],
        )


class CommissionItem(models.Model):
    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, verbose_name="Zlecenie"
    )
    name = models.CharField(max_length=255, verbose_name="Nazwa usługi/towaru")
    description = models.CharField(
        max_length=255, verbose_name="Opis usługi/towaru", blank=True, null=True
    )
    quantity = models.DecimalField(
        default=1,
        max_digits=8,
        decimal_places=3,
        verbose_name="Ilość",
        blank=True,
        null=True,
    )
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Cena")
    ware = models.ForeignKey(
        Ware, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Towar"
    )

    class Meta:
        verbose_name = "Pozycja zlecenia"
        verbose_name_plural = "Pozycje zleceń"
        ordering = ["commission", "pk"]

    def __str__(self):
        return "{} - {}".format(self.commission.id, self.name)

    def get_absolute_url(self):
        return reverse(
            "commission:commission_detail",
            kwargs={"pk": self.commission.pk, "slug": slugify(self.commission)},
        )

    @property
    def total(self):
        return self.price * self.quantity


class CommissionFile(MyCloudHomeFile):
    PARENT_FIELD = "commission"

    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, verbose_name="Zlecenie"
    )

    class Meta:
        verbose_name = "Plik zlecenia"
        verbose_name_plural = "Pliki zleceń"
        ordering = ["commission", "pk"]

    def get_absolute_url(self):
        return reverse(
            "commission:commission_detail",
            kwargs={"pk": self.commission.pk, "slug": slugify(self.commission)},
        )
