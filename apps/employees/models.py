from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse

from KlimaKar.templatetags.slugify import slugify
from apps.annotations.models import Annotation
from apps.invoicing.models import Contractor


class Employee(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="Użytkownik",
        null=True,
        blank=True,
    )
    first_name = models.CharField("Imię", max_length=150)
    last_name = models.CharField("Nazwisko", max_length=150)
    email = models.EmailField("Adres email", blank=True)
    phone = models.CharField(max_length=16, verbose_name="Numer telefonu", blank=True)
    annotations = GenericRelation(Annotation, related_query_name="employee")

    class Meta:
        verbose_name = "Pracownik"
        verbose_name_plural = "Pracownicy"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def formatted_phone(self):
        return Contractor.format_phone_number(self.phone)

    def get_absolute_url(self):
        return reverse(
            "employees:employee_detail", kwargs={"pk": self.pk, "slug": slugify(self)},
        )


class WorkAbsence(models.Model):
    SICK_LEAVE = "S"
    VACATION = "V"
    OTHER = "O"

    REASON_CHOICES = [
        (SICK_LEAVE, "Zwolnienie lekarskie"),
        (VACATION, "Urlop"),
        (OTHER, "Inny"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, verbose_name="Pracownik"
    )
    date_from = models.DateField(verbose_name="Data od")
    date_to = models.DateField(verbose_name="Data do")
    comment = models.TextField(verbose_name="Uwagi", blank=True)
    reason = models.CharField(
        max_length=1, choices=REASON_CHOICES, verbose_name="Powód nieobecności"
    )

    class Meta:
        verbose_name = "Nieobecność"
        verbose_name_plural = "Nieobecności"
        ordering = ["date_from", "date_to"]

    def __str__(self):
        return f"{self.employee}: {self.date_from} - {self.date_to}"

    def get_absolute_url(self):
        return reverse(
            "employees:employee_detail",
            kwargs={"pk": self.employee.pk, "slug": slugify(self.employee)},
        )
