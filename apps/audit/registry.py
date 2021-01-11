from KlimaKar.registry import ModelRegistry
from apps.audit.functions import (
    pre_delete_handler,
    pre_save_handler,
    post_save_handler,
    m2m_changed_handler,
)


class AuditRegistry(ModelRegistry):
    def get_pre_delete_handler(self):
        return pre_delete_handler

    def get_pre_save_handler(self):
        return pre_save_handler

    def get_post_save_handler(self):
        return post_save_handler

    def get_m2m_changed_handler(self):
        return m2m_changed_handler


audit = AuditRegistry()
