from tqdm import tqdm

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.search.models import SearchDocument
from apps.search.registry import search


class Command(BaseCommand):
    help = "Rebuild search index"

    def handle(self, *args, **options):
        SearchDocument.objects.all().delete()
        for model in search.registered_models():
            print(f"Indexing {model._meta.verbose_name_plural}")
            self.create_documents(model.objects.all())

    @transaction.atomic
    def create_documents(self, objects):
        for obj in tqdm(objects):
            SearchDocument.reindex(obj)
