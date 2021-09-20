from django.conf import settings
from django.core.paginator import Paginator

from .forms import (  # noqa: F401
    EmptyValue,
    GraphQLChoiceField,
    GraphQLForm,
    GraphQLMultipleChoiceField,
)
from .models import (  # noqa: F401
    GraphQLModelChoiceField,
    GraphQLModelForm,
    GraphQLModelMultipleChoiceField,
)


def result_page(queryset, page, per_page=None):
    if per_page is None:
        per_page = settings.GRAPHQL_DEFAULT_PAGE_SIZE
    if per_page > settings.GRAPHQL_MAX_PAGE_SIZE:
        per_page = settings.GRAPHQL_MAX_PAGE_SIZE

    paginator = Paginator(queryset, per_page)

    return {
        "page_number": page,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,
        "items": paginator.page(page),
    }
