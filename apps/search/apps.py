from django.apps import AppConfig
from django.db.models.signals import pre_delete, post_save


class SearchConfig(AppConfig):
    name = "apps.search"

    def ready(self):
        from apps.search.utils import (
            pre_delete_handler,
            post_save_handler,
            update_parent_handler,
        )

        from apps.search.models import SearchDocument

        for model in SearchDocument.indexed_models:
            post_save.connect(post_save_handler, sender=model)
            pre_delete.connect(pre_delete_handler, sender=model)

        for model in SearchDocument.child_models:
            post_save.connect(update_parent_handler, sender=model)
            pre_delete.connect(update_parent_handler, sender=model)
