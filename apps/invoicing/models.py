import datetime

from weasyprint import HTML, CSS

from django.db import models
from django.core.validators import RegexValidator
from django.template.loader import get_template

from apps.warehouse.models import Ware
from apps.invoicing.dictionaries import PAYMENT_TYPES, INVOICE_TYPES


class Contractor(models.Model):
    name = models.CharField(max_length=512, verbose_name=('Nazwa'))
    nip = models.CharField(max_length=32, verbose_name="NIP", blank=True, null=True)
    nip_prefix = models.CharField(max_length=2, verbose_name="Prefiks NIP", blank=True, null=True)
    address_1 = models.CharField(max_length=128, verbose_name="Adres", blank=True, null=True)
    address_2 = models.CharField(max_length=128, verbose_name="Adres 2", blank=True, null=True)
    city = models.CharField(max_length=128, verbose_name="Miasto", blank=True, null=True)
    postal_code = models.CharField(max_length=16, verbose_name="Kod pocztowy", blank=True, null=True)
    email = models.EmailField(verbose_name="Adres e-mail", blank=True, null=True)
    phone_1 = models.CharField(max_length=16, verbose_name="Numer telefonu", blank=True, null=True)
    phone_2 = models.CharField(max_length=16, verbose_name="Numer telefonu 2", blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=('Data dodania'))

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
    payed = models.BooleanField(verbose_name=('Zapłacono'), default=True)
    total_value_netto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=('Łączna wartość netto'))
    total_value_brutto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=('Łączna wartość brutto'))
    tax_percent = models.FloatField(verbose_name="Procent podatku VAT", default=23)
    comment = models.TextField(verbose_name=('Uwagi'), blank=True)
    legacy = models.BooleanField(default=False, verbose_name='Faktura archiwalna')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=('Data dodania'))

    def __str__(self):
        return self.number

    @property
    def total_value_tax(self):
        return self.total_value_brutto - self.total_value_netto

    @property
    def corrected_invoice(self):
        return CorrectiveSaleInvoice.objects.get(original_invoice=self)

    def save(self, *args, **kwargs):
        invoice_type = self.invoice_type
        invoices = SaleInvoice.objects.filter(invoice_type=invoice_type)
        if invoice_type == '1':
            invoices = (invoices | SaleInvoice.objects.filter(invoice_type='4')).distinct()
        elif invoice_type == '4':
            invoices = (invoices | SaleInvoice.objects.filter(invoice_type='1')).distinct()
        elif invoice_type == '2':
            invoices = (invoices | SaleInvoice.objects.filter(invoice_type='5')).distinct()
        elif invoice_type == '5':
            invoices = (invoices | SaleInvoice.objects.filter(invoice_type='2')).distinct()
        if self.pk:
            invoices = invoices.exclude(pk=self.pk)
        if invoices.filter(number=self.number).exists():
            raise ValueError('number', 'Faktura o tym numerze już istnieje.')

        number_data = self.number.split('/')
        self.number_value = number_data[0]
        self.number_year = number_data[1]
        if not self.pk and self.payment_date:
            self.payed = False
        super().save(*args, **kwargs)

    def generate_pdf(self, print_version=False):
        if self.invoice_type == '3':
            template = get_template('invoicing/corrective_invoice.html')
        else:
            template = get_template('invoicing/invoice.html')
        rendered_tpl = template.render({'invoice': self}).encode()
        documents = []
        documents.append(
            HTML(string=rendered_tpl).render(stylesheets=[CSS(filename='KlimaKar/static/css/invoice.css')]))
        if print_version:
            documents.append(
                HTML(string=rendered_tpl).render(stylesheets=[CSS(filename='KlimaKar/static/css/invoice.css')]))
        all_pages = []
        for doc in documents:
            for p in doc.pages:
                all_pages.append(p)
        return documents[0].copy(all_pages).write_pdf()


class RefrigerantWeights(models.Model):
    sale_invoice = models.OneToOneField(SaleInvoice, on_delete=models.CASCADE, verbose_name="Faktura sprzedażowa")
    r134a = models.PositiveIntegerField(verbose_name="Czynnik R134a", default=0)
    r1234yf = models.PositiveIntegerField(verbose_name="Czynnik R1234yf", default=0)
    r12 = models.PositiveIntegerField(verbose_name="Czynnik R12", default=0)
    r404 = models.PositiveIntegerField(verbose_name="Czynnik R404", default=0)

    def __str__(self):
        return "Waga czynników dla faktury {}".format(self.sale_invoice)


class ServiceTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nazwa usługi/towaru')
    description = models.CharField(max_length=255, verbose_name='Opis usługi/towaru', blank=True, null=True)
    quantity = models.IntegerField(verbose_name='Ilość', blank=True, null=True)
    price_netto = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Cena netto',
                                      blank=True, null=True)
    price_brutto = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Cena brutto',
                                       blank=True, null=True)
    ware = models.ForeignKey(Ware, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Towar')

    def __str__(self):
        return self.name


class SaleInvoiceItem(models.Model):
    sale_invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, verbose_name='Faktura sprzedażowa')
    name = models.CharField(max_length=255, verbose_name='Nazwa usługi/towaru')
    description = models.CharField(max_length=255, verbose_name='Opis usługi/towaru', blank=True, null=True)
    quantity = models.IntegerField(default=1, verbose_name='Ilość')
    price_netto = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Cena netto')
    price_brutto = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Cena brutto')
    ware = models.ForeignKey(Ware, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Towar')

    def __str__(self):
        return "{} - {}".format(self.sale_invoice.number, self.name)

    @property
    def total_netto(self):
        return self.price_netto * self.quantity

    @property
    def total_brutto(self):
        return self.price_brutto * self.quantity


class CorrectiveSaleInvoice(SaleInvoice):
    original_invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, verbose_name='Oryginalna faktura',
                                         related_name='%(class)s_original_invoice')
    reason = models.TextField(max_length=255, verbose_name='Powód wystawienia korekty')

    @property
    def diffrence_netto(self):
        return self.total_value_netto - self.original_invoice.total_value_netto

    @property
    def diffrence_brutto(self):
        return self.total_value_brutto - self.original_invoice.total_value_brutto

    @property
    def diffrence_tax(self):
        return self.total_value_tax - self.original_invoice.total_value_tax
