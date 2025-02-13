from enum import StrEnum
from typing import Optional
from urllib.parse import urlencode

from django.conf import settings
from django.utils.translation import gettext_lazy, override
from openhexa.toolbox.dhis2 import DHIS2

from hexa.core.utils import send_mail
from hexa.user_management.models import User

from .models import Connection, WorkspaceInvitation


def send_workspace_invitation_email(
    invitation: WorkspaceInvitation, user: Optional[User] = None
):
    token = invitation.generate_invitation_token()

    with override(user.language if user else invitation.invited_by.language):
        if user:
            title = gettext_lazy(
                f"You've been added to the workspace {invitation.workspace.name}"
            )
            action_url = f"{settings.NEW_FRONTEND_DOMAIN}/user/account"
        else:
            title = gettext_lazy(
                f"You've been invited to join the workspace {invitation.workspace.name} on OpenHEXA"
            )
            action_url = f"{settings.NEW_FRONTEND_DOMAIN}/register?{urlencode({'email': invitation.email, 'token': token})}"

        send_mail(
            title=title,
            template_name="workspaces/mails/invite_user",
            template_variables={
                "workspace": invitation.workspace.name,
                "owner": invitation.invited_by.display_name,
                "user": user,
                "url": action_url,
            },
            recipient_list=[invitation.email],
        )


class DHIS2MetadataQueryType(StrEnum):
    ORGANISATION_UNITS = "ORGANISATION_UNITS"
    ORGANISATION_UNIT_GROUPS = "ORGANISATION_UNIT_GROUPS"
    ORGANISATION_UNIT_LEVELS = "ORGANISATION_UNIT_LEVELS"
    DATASETS = "DATASETS"
    DATA_ELEMENTS = "DATA_ELEMENTS"
    DATA_ELEMENT_GROUPS = "DATA_ELEMENT_GROUPS"
    INDICATORS = "INDICATORS"
    INDICATOR_GROUPS = "INDICATOR_GROUPS"


def query_dhis2_metadata(
    dhis2: DHIS2, query_type: DHIS2MetadataQueryType, **kwargs
) -> dict:
    """
    Gets metadata from DHIS2
    """
    metadata_methods = {
        DHIS2MetadataQueryType.ORGANISATION_UNITS: dhis2.meta.organisation_units,
        DHIS2MetadataQueryType.ORGANISATION_UNIT_GROUPS: dhis2.meta.organisation_unit_groups,
        DHIS2MetadataQueryType.ORGANISATION_UNIT_LEVELS: dhis2.meta.organisation_unit_levels,
        DHIS2MetadataQueryType.DATASETS: dhis2.meta.datasets,
        DHIS2MetadataQueryType.DATA_ELEMENTS: dhis2.meta.data_elements,
        DHIS2MetadataQueryType.DATA_ELEMENT_GROUPS: dhis2.meta.data_element_groups,
        DHIS2MetadataQueryType.INDICATORS: dhis2.meta.indicators,
        DHIS2MetadataQueryType.INDICATOR_GROUPS: dhis2.meta.indicator_groups,
    }
    return metadata_methods[query_type](**kwargs)


def dhis2_client_from_connection(connection: Connection) -> DHIS2 | None:
    """
    Gets DHIS2 toolbox client from workspace connection
    """
    fields = connection.fields.all()
    dhis_connection_dict = {field.code: field.value for field in fields}

    return DHIS2(
        url=dhis_connection_dict.get("url"),
        username=dhis_connection_dict.get("username"),
        password=dhis_connection_dict.get("password"),
    )


def generate_search_filter(kwargs):
    filters = []
    search_query = kwargs.get("search")
    if search_query and search_query.strip():
        filters.append(f"name:token:{search_query.strip()}")

    if kwargs.get("filter"):
        for item in kwargs["filter"]:
            filters.append(f"{item['field']}:in[{','.join(map(str, item['value']))}]")

    return filters


def process_metadata_response(metadata_response, page):
    if isinstance(metadata_response, dict):
        metadata_items = metadata_response.get("items", [])
        pager = metadata_response.get("pager", {})
        total_items = pager.get("total", len(metadata_items))
        total_pages = pager.get("pageCount", 1)
        page_number = pager.get("page", page)

    elif isinstance(metadata_response, list):
        metadata_items = metadata_response
        total_items = len(metadata_items)
        total_pages = 1
        page_number = page

    else:
        raise ValueError("Unexpected response format from DHIS2")

    return metadata_items, total_items, total_pages, page_number


def error_response(page, error_type):
    return {
        "items": [],
        "total_items": 0,
        "total_pages": 0,
        "page_number": page,
        "success": False,
        "error": error_type,
    }
