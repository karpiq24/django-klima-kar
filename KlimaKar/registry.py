from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_delete


class ModelRegistry(object):
    def __init__(self):
        self._registry = set()

    def register(self, model):
        self._registry.add(model)
        self._connect_signals(model)

    def unregister(self, model):
        self._registry.remove(model)
        self._disconnect_signals(model)

    def contains(self, model):
        return model in self._registry

    def registered_models(self):
        return list(self._registry)

    def content_type_choices(self):
        return [
            (ContentType.objects.get_for_model(model).pk, self._names[model])
            for model in self.registered_models()
        ]

    def get_pre_delete_handler(self):
        return None

    def get_post_save_handler(self):
        return None

    def _connect_signals(self, model):
        if self.get_post_save_handler():
            post_save.connect(self.get_post_save_handler(), sender=model)
        if self.get_pre_delete_handler():
            pre_delete.connect(self.get_pre_delete_handler(), sender=model)

    def _disconnect_signals(self, model):
        if self.get_post_save_handler():
            post_save.disconnect(self.get_post_save_handler(), sender=model)
        if self.get_pre_delete_handler():
            pre_delete.disconnect(self.get_pre_delete_handler(), sender=model)
