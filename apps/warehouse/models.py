from django.db import models
from django.db.models import Sum, F
from django.db.models.fields import FloatField
from django.conf import settings


class Ware(models.Model):
    index = models.CharField(
        max_length=63,
        unique=True,
        verbose_name='Indeks')
    index_slug = models.CharField(
        max_length=63,
        verbose_name='Slug indeks')
    name = models.CharField(
        max_length=255,
        verbose_name='Nazwa')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Opis')
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Stan')
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data dodania')

    @property
    def last_price(self):
        last_invoice = InvoiceItem.objects.filter(ware=self).order_by('-invoice__date')
        if last_invoice:
            return last_invoice[0].price
        else:
            return None

    @staticmethod
    def slugify(value):
        return ''.join(e for e in value if e.isalnum()).lower()

    def __str__(self):
        return self.index

    def save(self, *args, **kwargs):
        self.index_slug = self.slugify(self.index)
        super(Ware, self).save(*args, **kwargs)


class Supplier(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nazwa')
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data dodania')

    def __str__(self):
        return self.name

    @property
    def all_invoices_value(self):
        total = InvoiceItem.objects.filter(invoice__supplier=self).aggregate(
            total=Sum(F('price') * F('quantity'),
                      output_field=FloatField()))['total']
        return total


class Invoice(models.Model):
    date = models.DateField(
        verbose_name='Data')
    number = models.CharField(
        max_length=127,
        verbose_name='Numer faktury')
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        verbose_name='Dostawca')
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data dodania')

    def __str__(self):
        return '{}: {}'.format(str(self.supplier), self.number)

    @property
    def total_value(self):
        total = InvoiceItem.objects.filter(invoice=self).aggregate(
            total=Sum(F('price') * F('quantity'),
                      output_field=FloatField()))['total']
        return total

    def check_ware_price_changes(self):
        for item in self.invoiceitem_set.all():
            last_invoice = Invoice.objects.filter(
                supplier=self.supplier,
                invoiceitem__ware=item.ware).exclude(
                pk=self.pk).order_by('-date').first()
            if not last_invoice:
                continue
            last_price = last_invoice.invoiceitem_set.filter(
                ware=item.ware).first().price
            if last_price <= 0 or item.price <= 0:
                continue
            percent_change = ((item.price - last_price) / last_price) * 100
            if percent_change >= settings.PRICE_CHHANGE_PERCENTAGE or \
                    percent_change <= -settings.PRICE_CHHANGE_PERCENTAGE:
                WarePriceChange.objects.create(
                    invoice=self,
                    ware=item.ware,
                    last_price=last_price,
                    new_price=item.price)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        verbose_name='Faktura')
    ware = models.ForeignKey(
        Ware,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Towar')
    quantity = models.DecimalField(
        default=1,
        max_digits=8,
        decimal_places=3,
        verbose_name='Ilość')
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='Cena netto')

    def __str__(self):
        return self.ware.index


class WarePriceChange(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        verbose_name='Faktura')
    ware = models.ForeignKey(
        Ware,
        on_delete=models.CASCADE,
        verbose_name='Towar')
    last_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='Ostatnia cena')
    new_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='Nowa cena')
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data dodania')

    def __str__(self):
        return "{} {} -> {}".format(self.ware, self.last_price, self.new_price)

    @property
    def is_discount(self):
        return self.new_price < self.last_price

    def percent_change(self, absolute=False):
        change = ((self.new_price - self.last_price) / self.last_price) * 100
        if absolute:
            change = abs(change)
        return change
