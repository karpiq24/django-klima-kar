import datetime

from django.db import models
from django.core.validators import RegexValidator

from apps.warehouse.models import Ware
from apps.invoicing.dictionaries import PAYMENT_TYPES, INVOICE_TYPES


class Contractor(models.Model):
    name = models.CharField(max_length=512, verbose_name=('Nazwa'))
    nip = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')], verbose_name="NIP",
                           blank=True, null=True)
    nip_prefix = models.CharField(max_length=2, verbose_name="Prefiks NIP", blank=True, null=True)
    address_1 = models.CharField(max_length=128, verbose_name="Adres", blank=True, null=True)
    address_2 = models.CharField(max_length=128, verbose_name="Adres 2", blank=True, null=True)
    city = models.CharField(max_length=128, verbose_name="Miasto", blank=True, null=True)
    postal_code = models.CharField(max_length=16, verbose_name="Kod pocztowy", blank=True, null=True)

    def __str__(self):
        return self.name


class SaleInvoice(models.Model):
    issue_date = models.DateField(verbose_name=('Data wystawienia'), default=datetime.date.today)
    completion_date = models.DateField(verbose_name=('Data wykonania'), default=datetime.date.today)
    invoice_type = models.CharField(max_length=1, verbose_name=('Rodzaj faktury'), choices=INVOICE_TYPES)
    number = models.CharField(max_length=16, validators=[RegexValidator(r'^\d+\/\d{4}$')],
                              verbose_name=('Numer faktury'))
    number_year = models.PositiveSmallIntegerField()
    number_value = models.PositiveSmallIntegerField()
    contractor = models.ForeignKey(Contractor, on_delete=models.PROTECT, verbose_name=('Kontrahent'))
    payment_type = models.CharField(max_length=1, verbose_name=('Rodzaj płatności'), choices=PAYMENT_TYPES)
    payment_date = models.DateField(
        verbose_name=('Termin płatności'), null=True, blank=True)
    total_value_netto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=('Łączna wartość netto'))
    total_value_brutto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=('Łączna wartość brutto'))
    tax_percent = models.FloatField(verbose_name="Procent podatku VAT", default=23)
    comment = models.TextField(verbose_name=('Uwagi'), blank=True)

    def __str__(self):
        return self.number

    @property
    def total_value_tax(self):
        return self.total_value_brutto - self.total_value_netto


class RefrigerantWeights(models.Model):
    sale_invoice = models.OneToOneField(SaleInvoice, on_delete=models.CASCADE, verbose_name="Faktura sprzedażowa")
    r134a = models.PositiveIntegerField(verbose_name="Czynnik R134a", default=0, blank=True)
    r1234yf = models.PositiveIntegerField(verbose_name="Czynnik R1234yf", default=0, blank=True)
    r12 = models.PositiveIntegerField(verbose_name="Czynnik R12", default=0, blank=True)
    r404 = models.PositiveIntegerField(verbose_name="Czynnik R404", default=0, blank=True)

    def __str__(self):
        return "Waga czynników dla faktury {}".format(self.sale_invoice)


class SaleInvoiceItem(models.Model):
    sale_invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, verbose_name='Faktura sprzedażowa')
    name = models.CharField(max_length=255, verbose_name='Nazwa usługi/towaru')
    description = models.CharField(max_length=255, verbose_name='Opis usługi/towaru', blank=True, null=True)
    quantity = models.IntegerField(default=1, verbose_name='Ilość')
    price_netto = models.DecimalField(max_digits=7, decimal_places=2, default='0.00', verbose_name='Cena netto')
    price_brutto = models.DecimalField(max_digits=7, decimal_places=2, default='0.00', verbose_name='Cena brutto')
    ware = models.ForeignKey(Ware, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Towar')

    def __str__(self):
        return "{} - {}".format(self.sale_invoice.number, self.name)

    @property
    def total_netto(self):
        return self.price_netto * self.quantity

    @property
    def total_brutto(self):
        return self.price_brutto * self.quantity
