import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from urllib.parse import urlencode

from django.conf import settings
from django.utils.translation import gettext_lazy, override
from openhexa.toolbox.dhis2 import DHIS2
from openhexa.toolbox.iaso import IASO

from hexa.core.utils import send_mail as send_mail
from hexa.user_management.models import User

from ..analytics.api import track
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

        attachments = [
            (
                "logo_with_text_white.png",
                open(
                    os.path.join(
                        settings.BASE_DIR,
                        "hexa/static/img/logo/logo_with_text_white.png",
                    ),
                    "rb",
                ).read(),
                "image/png",
            ),
            (
                "services_openhexa.png",
                open(
                    os.path.join(
                        settings.BASE_DIR,
                        "hexa/static/img/email/services_openhexa.png",
                    ),
                    "rb",
                ).read(),
                "image/png",
            ),
            (
                "flow_openhexa.png",
                open(
                    os.path.join(
                        settings.BASE_DIR,
                        "hexa/static/img/email/flow_openhexa.png",
                    ),
                    "rb",
                ).read(),
                "image/png",
            ),
        ]

        send_mail(
            title=title,
            template_name="workspaces/mails/invite_user",
            template_variables={
                "workspace": invitation.workspace.name,
                "owner": invitation.invited_by.display_name,
                "owner_email": invitation.invited_by.email,
                "user": user,
                "url": action_url,
            },
            recipient_list=[invitation.email],
            attachments=attachments,
        )

        track(
            request=None,
            event="emails.invite_sent",
            properties={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "workspace_id": str(invitation.workspace.id),
                "invitee_email": invitation.email,
                "invitee_role": invitation.role,
                "status": invitation.status,
            },
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


class IASOMetadataQueryType(StrEnum):
    FORMS = "FORMS"
    IASO_ORG_UNITS = "IASO_ORG_UNITS"
    PROJECTS = "PROJECTS"


@dataclass
class PagedMetadataResponse:
    items: list[dict]
    total_items: int
    total_pages: int
    page_number: int


def query_dhis2_metadata(
    dhis2_client: DHIS2, query_type: DHIS2MetadataQueryType, **kwargs
) -> PagedMetadataResponse:
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
    if query_type not in metadata_methods:
        raise ValueError(f"Unsupported query type: {query_type}")
    return normalize_metadata_response(metadata_methods[query_type](**kwargs))


def query_iaso_metadata(
    iaso_client: IASO, query_type: IASOMetadataQueryType, **kwargs
) -> PagedMetadataResponse:
    """
    Gets metadata from IASO
    """
    metadata_methods = {
        IASOMetadataQueryType.IASO_ORG_UNITS: iaso_client.get_org_units,
        IASOMetadataQueryType.PROJECTS: iaso_client.get_projects,
        IASOMetadataQueryType.FORMS: iaso_client.get_forms,
    }

    if query_type not in metadata_methods:
        raise ValueError(f"Unsupported query type: {query_type}")
    return normalize_metadata_response(metadata_methods[query_type](**kwargs))


def toolbox_client_from_connection(connection: Connection) -> DHIS2 | IASO | None:
    """
    Gets DHIS2, IASO toolbox client from workspace connection
    """
    supported_connection_types = [ConnectionType.DHIS2, ConnectionType.IASO]
    if connection.connection_type not in supported_connection_types:
        raise ValueError("Connection is not a DHIS2, IASO connection")

    fields = connection.fields.all()
    connection_values = {field.code: field.value for field in fields}

    if connection.connection_type == ConnectionType.IASO:
        return IASO(
            server_url=connection_values.get("url"),
            username=connection_values.get("username"),
            password=connection_values.get("password"),
        )
    if connection.connection_type == ConnectionType.DHIS2:
        return DHIS2(
            url=connection_values.get("url"),
            username=connection_values.get("username"),
            password=connection_values.get("password"),
        )


def normalize_metadata_response(response) -> PagedMetadataResponse:
    if isinstance(response, dict):
        pager = response.get("pager", {})
        return PagedMetadataResponse(
            items=response.get("items", []),
            total_items=pager.get("total", len(response.get("items", []))),
            total_pages=pager.get("pageCount", 1),
            page_number=pager.get("page", 1),
        )
    elif isinstance(response, list):
        return PagedMetadataResponse(
            items=response,
            total_items=len(response),
            total_pages=1,
            page_number=1,
        )
    else:
        raise ValueError("Unexpected response format")
