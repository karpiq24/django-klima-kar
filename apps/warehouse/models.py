# -*- coding: utf-8 -*-
from django.db import models


class Ware(models.Model):
    index = models.CharField(max_length=63, unique=True, verbose_name=('Indeks'))
    name = models.CharField(max_length=255, verbose_name=('Nazwa'))
    description = models.TextField(blank=True, null=True, verbose_name=('Opis'))
    stock = models.PositiveIntegerField(default=0, verbose_name=('Stan'))

    def __str__(self):
        return self.index


class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=('Nazwa'))

    def __str__(self):
        return self.name


class Invoice(models.Model):
    date = models.DateField(verbose_name=('Data'))
    number = models.CharField(max_length=127, verbose_name=('Numer faktury'))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name=('Dostawca'))
    total_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=('Łączna wartość'))
    items = models.ManyToManyField(Ware, through='InvoiceItem')

    def __str__(self):
        return self.number


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name=('Faktura'))
    ware = models.ForeignKey(Ware, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=('Towar'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=('Ilość'))
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name=('Cena netto'))

    def __str__(self):
        return self.ware.index
