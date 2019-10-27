from django.db import models

from KlimaKar.models import SingletonModel


class SiteSettings(SingletonModel):
    EMAIL_HOST = models.CharField(
        max_length=255,
        verbose_name='Serwer poczty',
        blank=True,
        null=True)
    EMAIL_HOST_USER = models.CharField(
        max_length=255,
        verbose_name='Użytkownik',
        blank=True,
        null=True)
    EMAIL_HOST_PASSWORD = models.CharField(
        max_length=255,
        verbose_name='Hasło',
        blank=True,
        null=True)
    EMAIL_PORT = models.PositiveIntegerField(
        default=0,
        verbose_name='Port',
        blank=True,
        null=True)
    EMAIL_USE_TLS = models.BooleanField(
        verbose_name='Wymagane połączenie TLS',
        default=False)
    EMAIL_USE_SSL = models.BooleanField(
        verbose_name='Wymagane połączenie SSL',
        default=False)
    DEFAULT_FROM_EMAIL = models.CharField(
        max_length=255, verbose_name='Wyświetlany nadawca',
        blank=True,
        null=True)
    SALE_INVOICE_EMAIL_TITLE = models.CharField(
        max_length=255,
        verbose_name='Tytuł wiadomości z fakturą sprzedażową',
        blank=True,
        null=True)
    SALE_INVOICE_EMAIL_BODY = models.TextField(
        verbose_name='Treść wiadomości z fakturą sprzedażową',
        blank=True,
        null=True)
    SALE_INVOICE_TAX_PERCENT = models.FloatField(
        verbose_name="Procent podatku VAT", default=23,
        blank=True,
        null=True)
    SALE_INVOICE_TAX_PERCENT_WDT = models.FloatField(
        verbose_name="Procent podatku VAT dla faktur WDT", default=0,
        blank=True,
        null=True)
    COMMISSION_EMAIL_TITLE = models.CharField(
        max_length=255, verbose_name='Tytuł wiadomości ze zleceniem',
        blank=True,
        null=True)
    COMMISSION_EMAIL_BODY = models.TextField(
        verbose_name='Treść wiadomości ze zleceniem',
        blank=True,
        null=True)
    COMMISSION_TAX_PERCENT = models.FloatField(
        verbose_name="Procent podatku VAT w zleceniu", default=23,
        blank=True,
        null=True)
    COMMISSION_SMS_BODY = models.TextField(
        verbose_name='Treść powiadomienia SMS',
        blank=True,
        null=True)
