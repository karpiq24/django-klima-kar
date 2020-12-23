import enum

from django.core.paginator import Paginator


def get_paginated_results(qs, pagination, filters, custom_filter=None):
    page_size = 10
    page = 1
    force_all = False
    if pagination:
        page_size = pagination.get("pageSize", page_size)
        page = pagination.get("page", page)
        force_all = pagination.get("forceAll", False)
    if filters:
        for key, value in filters.items():
            if issubclass(type(value), enum.Enum):
                filters[key] = value.value
        qs = qs.filter(**filters)
    if custom_filter:
        qs = custom_filter(qs)
    if force_all:
        return {
            "pageInfo": {
                "hasNextPage": False,
                "hasPreviousPage": False,
                "count": qs.count(),
                "numPages": 1,
                "pageNumber": 1,
            },
            "objects": qs,
        }
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)
    return {
        "pageInfo": {
            "hasNextPage": page_obj.has_next(),
            "hasPreviousPage": page_obj.has_previous(),
            "count": paginator.count,
            "numPages": paginator.num_pages,
            "pageNumber": page,
        },
        "objects": page_obj,
    }
