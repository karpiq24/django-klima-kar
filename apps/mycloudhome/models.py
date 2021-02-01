from django.conf import settings
from django.db import models
from django.core.cache import cache


class MyCloudHomeDirectoryModel(models.Model):
    DIRECTORY_ID_FIELD = None

    upload = models.BooleanField(verbose_name="Pliki są wgrywane", default=False)
    scanning = models.BooleanField(verbose_name="Trwa skanowanie", default=False)
    mch_id = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        abstract = True

    def get_files(self):
        raise NotImplementedError


class MyCloudHomeFile(models.Model):
    PARENT_FIELD = None

    file_name = models.CharField(max_length=256, verbose_name="Nazwa pliku")
    file_size = models.PositiveIntegerField(verbose_name="Rozmiar pliku")
    mime_type = models.CharField(max_length=64, verbose_name="Typ pliku")
    mch_id = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.file_name

    @property
    def file_contents(self):
        from apps.settings.models import MyCloudHome

        if not self.mch_id:
            return None

        cached = cache.get(f"file_{self.mch_id}")
        if cached:
            return cached
        cloud = MyCloudHome.load()
        data = cloud.download_file(self.mch_id)
        if data:
            cache.set(f"file_{self.mch_id}", data, timeout=settings.CACHE_FILE_TIMEOUT)
        return data

    @property
    def is_image(self):
        return self.mime_type in [
            "image/apng",
            "image/bmp",
            "image/gif",
            "image/x-icon",
            "image/jpeg",
            "image/png",
            "image/svg+xml",
            "image/tiff",
            "image/webp",
        ]
