from dataclasses import dataclass
from enum import StrEnum
from typing import Optional
from urllib.parse import urlencode

from django.conf import settings
from django.utils.translation import gettext_lazy, override
from openhexa.toolbox.dhis2 import DHIS2

from hexa.core.utils import send_mail
from hexa.user_management.models import User

from .models import Connection, ConnectionType, WorkspaceInvitation


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
    ORG_UNITS = "ORG_UNITS"
    ORG_UNIT_GROUPS = "ORG_UNIT_GROUPS"
    ORG_UNIT_LEVELS = "ORG_UNIT_LEVELS"
    DATASETS = "DATASETS"
    DATA_ELEMENTS = "DATA_ELEMENTS"
    DATA_ELEMENT_GROUPS = "DATA_ELEMENT_GROUPS"
    INDICATORS = "INDICATORS"
    INDICATOR_GROUPS = "INDICATOR_GROUPS"


@dataclass
class DHIS2MetadataResponse:
    items: list[dict]
    total_items: int
    total_pages: int
    page_number: int


def query_dhis2_metadata(
    dhis2_client: DHIS2, query_type: DHIS2MetadataQueryType, **kwargs
) -> DHIS2MetadataResponse:
    """
    Gets metadata from DHIS2
    """
    metadata_methods = {
        DHIS2MetadataQueryType.ORG_UNITS: dhis2_client.meta.organisation_units,
        DHIS2MetadataQueryType.ORG_UNIT_GROUPS: dhis2_client.meta.organisation_unit_groups,
        DHIS2MetadataQueryType.ORG_UNIT_LEVELS: dhis2_client.meta.organisation_unit_levels,
        DHIS2MetadataQueryType.DATASETS: dhis2_client.meta.datasets,
        DHIS2MetadataQueryType.DATA_ELEMENTS: dhis2_client.meta.data_elements,
        DHIS2MetadataQueryType.DATA_ELEMENT_GROUPS: dhis2_client.meta.data_element_groups,
        DHIS2MetadataQueryType.INDICATORS: dhis2_client.meta.indicators,
        DHIS2MetadataQueryType.INDICATOR_GROUPS: dhis2_client.meta.indicator_groups,
    }
    response = metadata_methods[query_type](**kwargs)

    if isinstance(response, dict):
        pager = response.get("pager", {})
        return DHIS2MetadataResponse(
            items=response.get("items", []),
            total_items=pager.get("total", len(response.get("items", []))),
            total_pages=pager.get("pageCount", 1),
            page_number=pager.get("page", 1),
        )

    elif isinstance(response, list):
        return DHIS2MetadataResponse(
            items=response,
            total_items=len(response),
            total_pages=1,
            page_number=1,
        )
    else:
        raise ValueError("Unexpected response format from DHIS2")


def dhis2_client_from_connection(connection: Connection) -> DHIS2 | None:
    """
    Gets DHIS2 toolbox client from workspace connection
    """
    if connection.connection_type != ConnectionType.DHIS2:
        raise ValueError("Connection is not a DHIS2 connection")

    fields = connection.fields.all()
    dhis_connection_dict = {field.code: field.value for field in fields}

    return DHIS2(
        url=dhis_connection_dict.get("url"),
        username=dhis_connection_dict.get("username"),
        password=dhis_connection_dict.get("password"),
    )
