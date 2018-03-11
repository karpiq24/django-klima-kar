# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Sum


class Ware(models.Model):
    index = models.CharField(max_length=63, unique=True, verbose_name=('Indeks'))
    index_slug = models.CharField(max_length=63, verbose_name=('Slug indeks'))
    name = models.CharField(max_length=255, verbose_name=('Nazwa'))
    description = models.TextField(blank=True, null=True, verbose_name=('Opis'))
    stock = models.PositiveIntegerField(default=0, verbose_name=('Stan'))

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
    name = models.CharField(max_length=255, unique=True, verbose_name=('Nazwa'))

    def __str__(self):
        return self.name

    @property
    def all_invoices_value(self):
        return Invoice.objects.filter(supplier=self).aggregate(Sum('total_value'))['total_value__sum']


class Invoice(models.Model):
    date = models.DateField(verbose_name=('Data'))
    number = models.CharField(max_length=127, verbose_name=('Numer faktury'))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name=('Dostawca'))
    total_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=('Łączna wartość'),
                                      null=True, blank=True)

    def __str__(self):
        return self.number

    def calculate_total_value(self):
        total = 0
        for item in self.invoiceitem_set.all():
            total += item.quantity * item.price
        self.total_value = total
        self.save()


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name=('Faktura'))
    ware = models.ForeignKey(Ware, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=('Towar'))
    quantity = models.IntegerField(default=1, verbose_name=('Ilość'))
    price = models.DecimalField(max_digits=7, decimal_places=2, default='0.00', verbose_name=('Cena netto'))

    def __str__(self):
        return self.ware.index
