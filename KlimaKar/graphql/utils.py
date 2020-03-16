import enum

from django.core.paginator import Paginator


def get_paginated_results(qs, pagination, filters):
    page_size = 10
    page = 1
    if pagination:
        page_size = pagination.get("pageSize", page_size)
        page = pagination.get("page", page)
    if filters:
        for key, value in filters.items():
            if issubclass(type(value), enum.Enum):
                filters[key] = value.value
        qs = qs.filter(**filters)
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
