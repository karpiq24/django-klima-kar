import datetime

from weasyprint import HTML, CSS

from django.db import models
from django.template.loader import get_template
from django.dispatch import receiver

from apps.settings.models import MyCloudHome
from apps.invoicing.models import Contractor, SaleInvoice
from apps.warehouse.models import Ware


class Vehicle(models.Model):
    registration_plate = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Numer rejestracyjny')
    vin = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='Numer VIN')
    brand = models.CharField(
        max_length=64,
        verbose_name='Marka')
    model = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Model')
    engine_volume = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Pojemność silnika (cm3)')
    engine_power = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Moc silnika (kW)')
    production_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Rok produkcji')

    def __str__(self):
        return '{}{}{}{}'.format(
            self.brand,
            ' {}'.format(self.model) if self.model else '',
            ' {}'.format(self.registration_plate) if self.registration_plate else '',
            ' ({})'.format(self.production_year) if self.production_year else '')


class Component(models.Model):
    COMPRESSOR = 'CO'
    HEATER = 'HE'
    OTHER = 'OT'
    TYPE_CHOICES = [
        (COMPRESSOR, 'Sprężarka'),
        (HEATER, 'Ogrzewanie postojowe'),
        (OTHER, 'Inny'),
    ]

    component_type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        verbose_name='Rodzaj')
    model = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Model')
    serial_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Numer seryjny')
    catalog_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Numer katalogowy')

    def __str__(self):
        return '{}{}{}{}'.format(
            self.get_component_type_display() if self.component_type != self.OTHER else '',
            ' {}'.format(self.model) if self.model else '',
            ' {}'.format(self.serial_number) if self.serial_number else '',
            ' {}'.format(self.catalog_number) if self.catalog_number else '')


class Commission(models.Model):
    OPEN = 'OP'
    READY = 'RE'
    DONE = 'DO'
    CANCELLED = 'CA'
    STATUS_CHOICES = [
        (OPEN, 'Otwarte'),
        (READY, 'Gotowe'),
        (DONE, 'Zamknięte'),
        (CANCELLED, 'Anulowane')
    ]
    VEHICLE = 'VH'
    COMPONENT = 'CO'
    COMMISSION_TYPES = [
        (VEHICLE, 'Pojazd'),
        (COMPONENT, 'Podzespół')
    ]

    commission_type = models.CharField(
        max_length=2,
        choices=COMMISSION_TYPES,
        default=VEHICLE,
        verbose_name='Rodzaj zlecenia')
    vc_name = models.CharField(
        max_length=128,
        verbose_name='Nazwa pojazdu/podzespołu')
    vehicle = models.ForeignKey(
        Vehicle,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Pojazd')
    component = models.ForeignKey(
        Component,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Podzespół')
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Kontrahent')
    sale_invoices = models.ManyToManyField(
        SaleInvoice,
        blank=True,
        verbose_name='Faktury sprzedażowe')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Opis')
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=OPEN,
        verbose_name='Status')
    start_date = models.DateField(
        verbose_name='Data przyjęcia',
        default=datetime.date.today)
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data zamknięcia')
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Wartość')
    upload = models.BooleanField(
        verbose_name='Pliki są wgrywane',
        default=False)
    mch_id = models.CharField(
        max_length=128,
        blank=True,
        null=True)

    def __str__(self):
        return self.vc_name

    def save(self, *args, **kwargs):
        if self.status in [self.DONE, self.CANCELLED] and not self.end_date:
            self.end_date = datetime.date.today()
        super().save(*args, **kwargs)

    @property
    def number(self):
        return self.pk

    def generate_pdf(self):
        template = get_template('commission/pdf_commission.html')
        rendered_tpl = template.render({'commission': self}).encode()
        documents = []
        documents.append(
            HTML(string=rendered_tpl).render(stylesheets=[CSS(filename='KlimaKar/static/css/invoice.css')]))
        all_pages = []
        for doc in documents:
            for p in doc.pages:
                all_pages.append(p)
        return documents[0].copy(all_pages).write_pdf()


class CommissionItem(models.Model):
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        verbose_name='Zlecenie')
    name = models.CharField(
        max_length=255,
        verbose_name='Nazwa usługi/towaru')
    description = models.CharField(
        max_length=255,
        verbose_name='Opis usługi/towaru',
        blank=True,
        null=True)
    quantity = models.IntegerField(
        default=1,
        verbose_name='Ilość')
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='Cena')
    ware = models.ForeignKey(
        Ware,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Towar')

    def __str__(self):
        return "{} - {}".format(self.commission.id, self.name)

    @property
    def total(self):
        return self.price * self.quantity


class CommissionFile(models.Model):
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        verbose_name='Zlecenie')
    file_name = models.CharField(
        max_length=256,
        verbose_name='Nazwa pliku')
    file_size = models.PositiveIntegerField(
        verbose_name='Rozmiar pliku')
    mime_type = models.CharField(
        max_length=64,
        verbose_name='Typ pliku')
    mch_id = models.CharField(
        max_length=128,
        blank=True,
        null=True)

    def __str__(self):
        return self.file_name

    @property
    def file_contents(self):
        if not self.mch_id:
            return None
        cloud = MyCloudHome.load()
        return cloud.download_file(self.mch_id)


@receiver(models.signals.pre_delete, sender=CommissionFile)
def file_pre_delete(sender, instance, **kwargs):
    if instance.mch_id:
        cloud = MyCloudHome.load()
        return cloud.delete_file(instance.mch_id)
