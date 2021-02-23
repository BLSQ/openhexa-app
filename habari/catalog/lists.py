from django.core.paginator import Paginator
from django.utils.translation import ugettext_lazy as _


def build_summary_list_params(
    queryset,
    *,
    title,
    per_page=5,
    columns,
    paginated_list_url,
    item_name,
    item_template
):
    """Build the template params required for the summary list partials"""

    paginator = Paginator(queryset, per_page)
    page = paginator.page(1)

    return {
        "title": title,
        "current_page": page,
        "current_page_count": len(page),
        "total_count": page.paginator.count,
        "columns": columns,
        "paginated_list_url": paginated_list_url,
        "item_name": item_name,
        "item_template": item_template,
    }


def build_paginated_list_params(
    queryset, *, title, per_page=10, page_number, columns, item_name, item_template
):
    """Build the template params required for the paginated list partials"""

    paginator = Paginator(queryset, per_page)
    page = paginator.page(page_number)

    return {
        "title": title,  # TODO: translate
        "label": _("%(start_index)d to %(end_index)d out of %(total)d")
        % {
            "start_index": page.start_index(),
            "end_index": page.end_index(),
            "total": paginator.count,
        },
        "current_page": page,
        "current_page_count": len(page),
        "current_page_number": page_number,
        "total_count": page.paginator.count,
        "range": list(set(paginator.page_range[:3]) | set(paginator.page_range[-3:])),
        "columns": columns,
        "item_name": item_name,
        "item_template": item_template,
    }
