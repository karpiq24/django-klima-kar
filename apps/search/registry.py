from KlimaKar.registry import ModelRegistry
from apps.search.utils import (
    pre_delete_handler,
    post_save_handler,
    update_parent_handler,
)


class SearchRegistry(ModelRegistry):
    def get_pre_delete_handler(self):
        return pre_delete_handler

    def get_post_save_handler(self):
        return post_save_handler


class SearchChildRegistry(ModelRegistry):
    def get_pre_delete_handler(self):
        return update_parent_handler

    def get_post_save_handler(self):
        return update_parent_handler


search = SearchRegistry()
search_child = SearchChildRegistry()
