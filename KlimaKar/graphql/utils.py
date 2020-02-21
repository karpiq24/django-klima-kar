from ariadne import convert_kwargs_to_snake_case
from django.core.paginator import Paginator


@convert_kwargs_to_snake_case
def get_paginated_results(qs, page=1, page_size=10):
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)
    return {
        'pageInfo': {
            'hasNextPage': page_obj.has_next(),
            'hasPreviousPage': page_obj.has_previous(),
            'count': paginator.count,
            'num_pages': paginator.num_pages
        },
        'objects': page_obj
    }
