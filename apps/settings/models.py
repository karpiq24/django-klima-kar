import os
import requests

from django.db import models
from django.conf import settings

from KlimaKar.models import SingletonModel
from KlimaKar.functions import encode_media_related
from apps.commission.models import Commission, CommissionFile

from apps.warehouse.models import Supplier
from apps.wiki.models import Article, ArticleFile


class SiteSettings(SingletonModel):
    EMAIL_HOST = models.CharField(
        max_length=255, verbose_name="Serwer poczty", blank=True, null=True
    )
    EMAIL_HOST_USER = models.CharField(
        max_length=255, verbose_name="Użytkownik", blank=True, null=True
    )
    EMAIL_HOST_PASSWORD = models.CharField(
        max_length=255, verbose_name="Hasło", blank=True, null=True
    )
    EMAIL_PORT = models.PositiveIntegerField(
        default=0, verbose_name="Port", blank=True, null=True
    )
    EMAIL_USE_TLS = models.BooleanField(
        verbose_name="Wymagane połączenie TLS", default=False
    )
    EMAIL_USE_SSL = models.BooleanField(
        verbose_name="Wymagane połączenie SSL", default=False
    )
    DEFAULT_FROM_EMAIL = models.CharField(
        max_length=255, verbose_name="Wyświetlany nadawca", blank=True, null=True
    )
    SALE_INVOICE_EMAIL_TITLE = models.CharField(
        max_length=255,
        verbose_name="Tytuł wiadomości z fakturą sprzedażową",
        blank=True,
        null=True,
    )
    SALE_INVOICE_EMAIL_BODY = models.TextField(
        verbose_name="Treść wiadomości z fakturą sprzedażową", blank=True, null=True
    )
    SALE_INVOICE_TAX_PERCENT = models.FloatField(
        verbose_name="Procent podatku VAT", default=23, blank=True, null=True
    )
    SALE_INVOICE_TAX_PERCENT_WDT = models.FloatField(
        verbose_name="Procent podatku VAT dla faktur WDT",
        default=0,
        blank=True,
        null=True,
    )
    SEND_SALE_INVOICE = models.BooleanField(
        verbose_name="Wysyłaj faktury co miesiąc", default=False
    )
    SEND_SALE_INVOICE_EMAILS = models.TextField(
        verbose_name="Adresy email do comiesięcznej wysyłki faktur", blank=True,
    )
    SEND_SALE_INVOICE_TITLE = models.CharField(
        max_length=255, verbose_name="Tytuł comiesięcznej wiadomości", blank=True,
    )
    SEND_SALE_INVOICE_BODY = models.TextField(
        verbose_name="Treść comiesięcznej wiadomości", blank=True,
    )
    COMMISSION_EMAIL_TITLE = models.CharField(
        max_length=255,
        verbose_name="Tytuł wiadomości ze zleceniem",
        blank=True,
        null=True,
    )
    COMMISSION_EMAIL_BODY = models.TextField(
        verbose_name="Treść wiadomości ze zleceniem", blank=True, null=True
    )
    COMMISSION_SMS_BODY = models.TextField(
        verbose_name="Treść powiadomienia SMS", blank=True, null=True
    )

    class Meta:
        verbose_name = "Ustawienia strony"
        verbose_name_plural = "Ustawienia strony"

    def __str__(self):
        return "Ustawienia strony"


class InvoiceDownloadSettings(SingletonModel):
    DOWNLOAD_INTER_CARS = models.BooleanField(
        verbose_name="Pobieraj faktury Inter Cars", default=False
    )
    INTER_CARS_SUPPLIER = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        verbose_name="Dostawca Inter Cars",
        related_name="intercars",
        blank=True,
        null=True,
    )
    INTER_CARS_CLIENT_NUMBER = models.CharField(
        verbose_name="Numer klienta Inter Cars", max_length=255, blank=True, null=True
    )
    INTER_CARS_TOKEN = models.CharField(
        verbose_name="Token Inter Cars", max_length=255, blank=True, null=True
    )
    DOWNLOAD_DEKO = models.BooleanField(
        verbose_name="Pobieraj faktury Deko", default=False
    )
    DEKO_SUPPLIER = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        verbose_name="Dostawca Deko",
        related_name="deko",
        blank=True,
        null=True,
    )
    DEKO_LOGIN = models.CharField(
        verbose_name="Login Deko", max_length=255, blank=True, null=True
    )
    DEKO_PASSWORD = models.CharField(
        verbose_name="Hasło Deko", max_length=255, blank=True, null=True
    )
    DOWNLOAD_PROFIAUTO = models.BooleanField(
        verbose_name="Pobieraj faktury ProfiAuto", default=False
    )
    PROFIAUTO_SUPPLIER = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        verbose_name="Dostawca ProfiAuto",
        related_name="profiauto",
        blank=True,
        null=True,
    )
    PROFIAUTO_LOGIN = models.CharField(
        verbose_name="Login ProfiAuto", max_length=255, blank=True, null=True
    )
    PROFIAUTO_PASSWORD = models.CharField(
        verbose_name="Hasło ProfiAuto", max_length=255, blank=True, null=True
    )
    DOWNLOAD_GORDON = models.BooleanField(
        verbose_name="Pobieraj faktury Gordon", default=False
    )
    GORDON_SUPPLIER = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        verbose_name="Dostawca Gordon",
        related_name="gordon",
        blank=True,
        null=True,
    )
    GORDON_LOGIN = models.CharField(
        verbose_name="Login Gordon", max_length=255, blank=True, null=True
    )
    GORDON_PASSWORD = models.CharField(
        verbose_name="Hasło Gordon", max_length=255, blank=True, null=True
    )
    DOWNLOAD_ZATOKA = models.BooleanField(
        verbose_name="Pobieraj faktury Zatoka", default=False
    )
    ZATOKA_SUPPLIER = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        verbose_name="Dostawca Zatoka",
        related_name="zatoka",
        blank=True,
        null=True,
    )
    ZATOKA_LOGIN = models.CharField(
        verbose_name="Login Zatoka", max_length=255, blank=True, null=True
    )
    ZATOKA_PASSWORD = models.CharField(
        verbose_name="Hasło Zatoka", max_length=255, blank=True, null=True
    )

    class Meta:
        verbose_name = "Ustawienia pobierania faktur"
        verbose_name_plural = "Ustawienia pobierania faktur"

    def __str__(self):
        return "Ustawienia pobierania faktur"


class MyCloudHome(SingletonModel):
    APP_DIR_NAME = models.CharField(max_length=255, null=True)
    BACKUP_DIR_NAME = models.CharField(max_length=255, null=True)
    COMMISSION_DIR_NAME = models.CharField(max_length=255, null=True)
    ARTICLE_DIR_NAME = models.CharField(max_length=255, null=True)
    WD_CLIENT_ID = models.CharField(max_length=255, null=True)
    WD_CLIENT_SECRET = models.CharField(max_length=255, null=True)
    REFRESH_TOKEN = models.CharField(max_length=1024, blank=True, null=True)
    ACCESS_TOKEN = models.CharField(max_length=2048, blank=True, null=True)
    USER_ID = models.CharField(max_length=128, blank=True, null=True)
    DEVICE_ID = models.CharField(max_length=128, blank=True, null=True)
    DEVICE_NAME = models.CharField(max_length=256, blank=True, null=True)
    DEVICE_INTERNAL_URL = models.CharField(max_length=256, blank=True, null=True)
    DEVICE_EXTERNAL_URL = models.CharField(max_length=256, blank=True, null=True)
    APP_DIR_ID = models.CharField(max_length=128, blank=True, null=True)
    COMMISSION_DIR_ID = models.CharField(max_length=128, blank=True, null=True)
    ARTICLE_DIR_ID = models.CharField(max_length=128, blank=True, null=True)
    BACKUP_DIR_ID = models.CharField(max_length=128, blank=True, null=True)

    UPLOAD_MODELS = {
        "commission": {"model": Commission, "file_model": CommissionFile},
        "article": {"model": Article, "file_model": ArticleFile},
    }

    class Meta:
        verbose_name = "Ustawienia MyCluod Home"
        verbose_name_plural = "Ustawienia MyCluod Home"

    def __str__(self):
        return "Ustawienia MyCluod Home"

    def initialize(self):
        if not self.REFRESH_TOKEN:
            self.authorize_connection()
        if not self.ACCESS_TOKEN:
            self._refresh_token()
        if not self.USER_ID:
            user = self.get_user_info()
            self.USER_ID = user["sub"]
            self.save()
        if (
            not self.DEVICE_ID
            or not self.DEVICE_NAME
            or not self.DEVICE_INTERNAL_URL
            or not self.DEVICE_EXTERNAL_URL
        ):
            device = self.get_user_devices()["data"][0]
            self.DEVICE_ID = device["deviceId"]
            self.DEVICE_NAME = device["name"]
            self.DEVICE_INTERNAL_URL = device["network"]["internalURL"]
            self.DEVICE_EXTERNAL_URL = device["network"]["externalURI"]
            self.save()
        if not self.APP_DIR_ID:
            self._initialize_app_dir()
        if not self.COMMISSION_DIR_ID:
            self._initialize_commission_dir()
        if not self.ARTICLE_DIR_ID:
            self._initialize_article_dir()
        if not self.BACKUP_DIR_ID:
            self._initialize_backup_dir()

    def _initialize_app_dir(self):
        r = self.create_folder(self.APP_DIR_NAME)
        if r.status_code == 201:
            self.APP_DIR_ID = r.headers["Location"].split("/")[-1]
            self.save()
        else:
            files = self.get_files()["files"]
            for f in files:
                if f["name"] == self.APP_DIR_NAME:
                    self.APP_DIR_ID = f["id"]
                    self.save()
                    break

    def _initialize_commission_dir(self):
        r = self.create_folder(self.COMMISSION_DIR_NAME, self.APP_DIR_ID)
        if r.status_code == 201:
            self.COMMISSION_DIR_ID = r.headers["Location"].split("/")[-1]
            self.save()
        else:
            files = self.get_files(self.APP_DIR_ID)["files"]
            for f in files:
                if f["name"] == self.COMMISSION_DIR_NAME:
                    self.COMMISSION_DIR_ID = f["id"]
                    self.save()
                    break

    def _initialize_article_dir(self):
        r = self.create_folder(self.ARTICLE_DIR_NAME, self.APP_DIR_ID)
        if r.status_code == 201:
            self.ARTICLE_DIR_ID = r.headers["Location"].split("/")[-1]
            self.save()
        else:
            files = self.get_files(self.APP_DIR_ID)["files"]
            for f in files:
                if f["name"] == self.ARTICLE_DIR_NAME:
                    self.ARTICLE_DIR_ID = f["id"]
                    self.save()
                    break

    def _initialize_backup_dir(self):
        r = self.create_folder(self.BACKUP_DIR_NAME, self.APP_DIR_ID)
        if r.status_code == 201:
            self.BACKUP_DIR_ID = r.headers["Location"].split("/")[-1]
            self.save()
        else:
            files = self.get_files(self.APP_DIR_ID)["files"]
            for f in files:
                if f["name"] == self.BACKUP_DIR_NAME:
                    self.BACKUP_DIR_ID = f["id"]
                    self.save()
                    break

    def _get_endpoint(self, endpoint):
        url = "http://config.mycloud.com/config/v1/config"
        r = requests.get(url)
        return r.json()["data"]["componentMap"]["cloud.service.urls"][endpoint]

    def get_auth_url(self):
        url = os.path.join(self._get_endpoint("service.auth0.url"), "authorize")
        params = {
            "scope": "profile openid offline_access nas_read_write nas_read_only user_read device_read",
            "response_type": "code",
            "connection": "Username-Password-Authentication",
            "sso": "false",
            "audience": "mycloud.com",
            "protocol": "oauth2",
            "redirect_uri": settings.WD_REDIRECT_URL,
            "client_id": self.WD_CLIENT_ID,
        }
        pr = requests.models.PreparedRequest()
        pr.prepare(method="get", url=url, params=params)
        return pr.url

    def _get_access_and_refresh_token(self, code):
        url = os.path.join(self._get_endpoint("service.auth0.url"), "oauth", "token")
        data = {
            "code": code,
            "audience": "mycloud.com",
            "client_id": self.WD_CLIENT_ID,
            "client_secret": self.WD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": settings.WD_REDIRECT_URL,
        }
        r = requests.post(url, data=data)
        return r.json()

    def authorize_connection(self, code):
        data = self._get_access_and_refresh_token(code)
        if data.get("error"):
            return False
        self.ACCESS_TOKEN = data["access_token"]
        self.REFRESH_TOKEN = data["refresh_token"]
        self.save()
        self.initialize()
        return True

    def _refresh_token(self):
        url = os.path.join(self._get_endpoint("service.auth0.url"), "oauth", "token")
        data = {
            "audience": "mycloud.com",
            "client_id": self.WD_CLIENT_ID,
            "client_secret": self.WD_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": self.REFRESH_TOKEN,
        }
        r = requests.post(url, data=data)
        self.ACCESS_TOKEN = r.json()["access_token"]
        self.save()
        return r.json()

    def _get_auth_headers(self):
        return {"Authorization": "Bearer {}".format(self.ACCESS_TOKEN)}

    def get_user_info(self):
        url = os.path.join(self._get_endpoint("service.auth0.url"), "userinfo")
        r = requests.get(url, headers=self._get_auth_headers())
        if self._has_auth_errors(r, refresh=False):
            return None
        return r.json()

    def get_user_devices(self):
        url = os.path.join(
            self._get_endpoint("service.device.url"),
            "device",
            "v1",
            "user",
            self.USER_ID,
        )
        r = requests.get(url, headers=self._get_auth_headers())
        if self._has_auth_errors(r):
            return self.get_user_devices()
        return r.json()

    def create_folder(self, name, directory="root"):
        url = os.path.join(self.DEVICE_INTERNAL_URL, "sdk", "v2", "files")
        data = {"name": name, "mimeType": "application/x.wd.dir", "parentID": directory}
        body, content_type = encode_media_related(data)
        headers = self._get_auth_headers()
        headers["Content-Type"] = content_type
        r = requests.post(url, data=body, headers=headers)
        if self._has_auth_errors(r):
            return self.create_folder(name, directory)
        return r

    def create_file(self, name, contents, directory="root"):
        url = os.path.join(self.DEVICE_INTERNAL_URL, "sdk", "v2", "files")
        data = {"name": name, "parentID": directory}
        body, content_type = encode_media_related(data, contents)
        headers = self._get_auth_headers()
        headers["Content-Type"] = content_type
        r = requests.post(url, data=body, headers=headers)
        if self._has_auth_errors(r):
            return self.create_file(name, contents, directory)
        return r

    def get_files(self, directory="root"):
        url = os.path.join(
            self.DEVICE_INTERNAL_URL, "sdk", "v2", "filesSearch", "parents"
        )
        params = {"ids": directory}
        r = requests.get(url, params=params, headers=self._get_auth_headers())
        if self._has_auth_errors(r):
            return self.get_files(directory)
        return r.json()

    def delete_file(self, file_id):
        if not settings.WD_DELETE_FILES:
            return False
        if settings.DEBUG:
            raise Exception("Cannot delete WD files when in DEBUG mode.")
        if file_id == self.APP_DIR_ID:
            return False
        url = os.path.join(self.DEVICE_INTERNAL_URL, "sdk", "v2", "files", file_id)
        r = requests.delete(url, headers=self._get_auth_headers())
        if self._has_auth_errors(r):
            return self.delete_file(file_id)
        return r

    def download_file(self, file_id):
        if file_id == self.APP_DIR_ID:
            return None
        url = os.path.join(
            self.DEVICE_INTERNAL_URL, "sdk", "v2", "files", file_id, "content"
        )
        r = requests.get(url, headers=self._get_auth_headers())
        if self._has_auth_errors(r, check_text=False, check_json=False):
            return self.download_file(file_id)
        return r.content

    def _has_auth_errors(
        self, response, refresh=True, check_text=True, check_json=True
    ):
        has_error = False
        if response.status_code == 401:
            has_error = True
        elif check_text and response.text == "Unauthorized":
            has_error = True
        elif check_json:
            try:
                json_data = response.json()
                if json_data.get("key") == "unauthenticated":
                    has_error = True
                elif json_data.get("error", {}).get("label") == "UNAUTHORIZED":
                    has_error = True
                elif json_data.get("error") == "unauthorized":
                    has_error = True
            except ValueError:
                pass
        if has_error and refresh:
            self._refresh_token()
        return has_error
