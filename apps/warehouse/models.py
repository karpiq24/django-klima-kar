import datetime

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.conf import settings
from django.urls import reverse

from KlimaKar.templatetags.slugify import slugify
from KlimaKar.models import TotalValueQuerySet
from apps.annotations.models import Annotation
from apps.audit.functions import get_audit_logs
from apps.search.models import SearchDocument


class Ware(models.Model):
    RELATED_MODELS = [("warehouse.Invoice", "invoiceitem__ware")]
    MODEL_COLOR = "#FF3516"
    MODEL_ICON = "fas fa-tags"

    index = models.CharField(max_length=63, unique=True, verbose_name="Indeks")
    index_slug = models.CharField(max_length=63, verbose_name="Slug indeks")
    name = models.CharField(max_length=255, verbose_name="Nazwa")
    description = models.TextField(blank=True, null=True, verbose_name="Opis")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stan")
    retail_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Cena detaliczna",
    )
    barcode = models.CharField(max_length=32, blank=True, verbose_name="Kod kreskowy")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")
    annotations = GenericRelation(Annotation, related_query_name="ware")

    class Meta:
        verbose_name = "Towar"
        verbose_name_plural = "Towary"
        ordering = ["index"]

    @property
    def last_price(self):
        last_invoice = InvoiceItem.objects.filter(ware=self).order_by("-invoice__date")
        if last_invoice:
            return last_invoice[0].price
        else:
            return None

    @staticmethod
    def slugify(value):
        return "".join(e for e in value if e.isalnum()).lower()

    def __str__(self):
        return self.index

    def get_absolute_url(self):
        return reverse(
            "warehouse:ware_detail", kwargs={"pk": self.pk, "slug": slugify(self)}
        )

    def save(self, *args, **kwargs):
        self.index_slug = self.slugify(self.index)
        super(Ware, self).save(*args, **kwargs)

    def get_logs(self):
        return get_audit_logs(self)


class Supplier(models.Model):
    RELATED_MODELS = [("warehouse.Invoice", "supplier")]
    MODEL_COLOR = "#C1456E"
    MODEL_ICON = "fas fa-truck"

    name = models.CharField(max_length=255, unique=True, verbose_name="Nazwa")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")

    annotations = GenericRelation(Annotation, related_query_name="supplier")
    search = GenericRelation(SearchDocument, related_query_name="supplier")

    class Meta:
        verbose_name = "Dostawca"
        verbose_name_plural = "Dostawcy"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "warehouse:supplier_detail", kwargs={"pk": self.pk, "slug": slugify(self)}
        )

    @property
    def all_invoices_value(self):
        return self.invoice_set.total()

    def get_logs(self):
        return get_audit_logs(self)


class Invoice(models.Model):
    PRICE_FIELD = "invoiceitem__price"
    QUANTITY_FIELD = "invoiceitem__quantity"
    MODEL_COLOR = "#8355C5"
    MODEL_ICON = "fas fa-file-alt"

    objects = TotalValueQuerySet.as_manager()

    date = models.DateField(verbose_name="Data")
    number = models.CharField(max_length=127, verbose_name="Numer faktury")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, verbose_name="Dostawca"
    )
    remote_id = models.CharField(
        max_length=256, verbose_name="ID u dostawcy", blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")

    annotations = GenericRelation(Annotation, related_query_name="invoice")
    search = GenericRelation(SearchDocument, related_query_name="invoice")

    class Meta:
        verbose_name = "Faktura zakupowa"
        verbose_name_plural = "Faktury zakupowe"
        ordering = ["-date"]
        unique_together = ["supplier", "number"]

    def __str__(self):
        return "{}: {}".format(str(self.supplier), self.number)

    def get_absolute_url(self):
        return reverse(
            "warehouse:invoice_detail", kwargs={"pk": self.pk, "slug": slugify(self)}
        )

    @property
    def is_editable(self):
        return self.created_date.date() == datetime.date.today()

    @property
    def total_value(self):
        return self._meta.model.objects.filter(pk=self.pk).total()

    def check_ware_price_changes(self):
        for item in self.invoiceitem_set.all():
            last_invoice = (
                Invoice.objects.filter(
                    supplier=self.supplier, invoiceitem__ware=item.ware
                )
                .exclude(pk=self.pk)
                .order_by("-date")
                .first()
            )
            if not last_invoice:
                continue
            last_price = (
                last_invoice.invoiceitem_set.filter(ware=item.ware).first().price
            )
            if last_price <= 0 or item.price <= 0:
                continue
            percent_change = ((item.price - last_price) / last_price) * 100
            if (
                percent_change >= settings.PRICE_CHHANGE_PERCENTAGE
                or percent_change <= -settings.PRICE_CHHANGE_PERCENTAGE
            ):
                WarePriceChange.objects.create(
                    invoice=self,
                    ware=item.ware,
                    last_price=last_price,
                    new_price=item.price,
                )

    def get_logs(self):
        return get_audit_logs(
            self,
            m2one=[
                {
                    "key": "invoice",
                    "objects": self.invoiceitem_set.all(),
                    "model": InvoiceItem,
                },
            ],
        )


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, verbose_name="Faktura"
    )
    ware = models.ForeignKey(Ware, on_delete=models.PROTECT, verbose_name="Towar")
    quantity = models.DecimalField(
        default=1, max_digits=8, decimal_places=3, verbose_name="Ilość"
    )
    price = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name="Cena netto"
    )

    class Meta:
        verbose_name = "Pozycja faktury zakupowej"
        verbose_name_plural = "Pozycje faktur zakupowych"
        ordering = ["invoice", "pk"]

    def __str__(self):
        return f"{self.invoice}: {self.ware.index if self.ware else '-'}"

    def get_absolute_url(self):
        return reverse(
            "warehouse:invoice_detail",
            kwargs={"pk": self.invoice.pk, "slug": slugify(self.invoice)},
        )


class WarePriceChange(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, verbose_name="Faktura"
    )
    ware = models.ForeignKey(Ware, on_delete=models.CASCADE, verbose_name="Towar")
    last_price = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name="Ostatnia cena"
    )
    new_price = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name="Nowa cena"
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")

    class Meta:
        verbose_name = "Zmiana ceny towaru"
        verbose_name_plural = "Zmiany cen towarów"
        ordering = ["-created_date"]

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
