from KlimaKar.registry import ModelRegistry
from apps.annotations.handlers import delete_annotations_handler


class AnnotationsRegistry(ModelRegistry):
    def get_pre_delete_handler(self):
        return delete_annotations_handler


annotations = AnnotationsRegistry()
