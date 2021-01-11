from django.apps import AppConfig


class AnnotationsConfig(AppConfig):
    name = "apps.annotations"

    def ready(self):
        from apps.audit.registry import audit
        from apps.annotations.models import Annotation

        audit.register(Annotation)
