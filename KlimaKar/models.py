from django.db import models
from django.db.models import Sum, F
from django.db.models.fields import FloatField
from django.db.models.functions import Coalesce


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class TotalValueQuerySet(models.QuerySet):
    def total(self, price_type=None):
        price_field = self.model.PRICE_FIELD
        if price_type:
            price_field = "{}_{}".format(price_field, price_type)
        return self.aggregate(
            total=Coalesce(
                Sum(
                    F(price_field) * F(self.model.QUANTITY_FIELD),
                    output_field=FloatField(),
                ),
                0,
            )
        )["total"]

    def order_by_total(self, is_descending=True, price_type=None):
        price_field = self.model.PRICE_FIELD
        if price_type:
            price_field = "{}_{}".format(price_field, price_type)
        return self.annotate(
            total=Coalesce(
                Sum(
                    F(price_field) * F(self.model.QUANTITY_FIELD),
                    output_field=FloatField(),
                ),
                0,
            )
        ).order_by("{}total".format("-" if is_descending else ""))
