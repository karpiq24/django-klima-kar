from django.db import models


class ReceiptPTU(models.Model):
    date = models.DateField(
        verbose_name=('Data'),
        unique=True)
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=('Łączna wartość PTU'))

    def __str__(self):
        return "{} - {} zł".format(self.date, self.value)
