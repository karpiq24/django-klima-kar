from django.apps import AppConfig
from django.db.models.signals import pre_delete


class MycloudhomeConfig(AppConfig):
    name = "apps.mycloudhome"

    def ready(self):
        from apps.commission.models import CommissionFile
        from apps.wiki.models import ArticleFile
        from apps.mycloudhome.utils import file_pre_delete_handler

        models = [CommissionFile, ArticleFile]

        for model in models:
            pre_delete.connect(file_pre_delete_handler, sender=model)
