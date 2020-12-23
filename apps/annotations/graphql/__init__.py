import os

from ariadne import load_schema_from_path
from django.conf import settings

from apps.annotations.graphql.types import (
    annotation,
    query,
    mutation,
)

from apps.annotations.graphql.queries import *  # noqa
from apps.annotations.graphql.mutations import *  # noqa


AnnotationTypeDefs = load_schema_from_path(
    os.path.join(settings.BASE_DIR, "apps/annotations/graphql/")
)
AnnotationTypes = [
    query,
    annotation,
    mutation,
]
