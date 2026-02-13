import json
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import boto3
import psycopg2
from botocore.config import Config as BotoConfig
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from google.cloud import storage as gcs_storage
from urllib.parse import urlencode

from django.conf import settings
from django.utils.translation import gettext_lazy, override
from openhexa.toolbox.dhis2 import DHIS2
from openhexa.toolbox.iaso import IASO

from hexa.core.utils import get_email_attachments, send_mail
from hexa.user_management.models import User

from ..analytics.api import track
from .models import Connection, ConnectionType, Workspace, WorkspaceInvitation

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 10


def send_workspace_add_user_email(
    invited_by: User, workspace: Workspace, invitee: User, role: str
):
    title = gettext_lazy(
        f"You've been added to the workspace {workspace.name} on OpenHEXA"
    )
    action_url = f"{settings.NEW_FRONTEND_DOMAIN}/workspaces/{workspace.slug}"

    with override(invitee.language):
        send_mail(
            title=title,
            template_name="workspaces/mails/add_existing_user",
            template_variables={
                "workspace": workspace.name,
                "owner": invited_by.display_name,
                "owner_email": invited_by.email,
                "invitee": invitee.display_name,
                "url": action_url,
            },
            recipient_list=[invitee.email],
            attachments=get_email_attachments(),
        )

        track(
            request=None,
            event="emails.workspace_invite_sent",
            properties={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "workspace": workspace.slug,
                "invitee_email": invitee.email,
                "invitee_role": role,
            },
        )


def send_workspace_invite_new_user_email(invitation: WorkspaceInvitation):
    title = gettext_lazy(
        f"You've been invited to join the workspace {invitation.workspace.name} on OpenHEXA"
    )
    token = invitation.generate_token()
    action_url = f"{settings.NEW_FRONTEND_DOMAIN}/register?{urlencode({'email': invitation.email, 'token': token})}"
    invited_by = invitation.invited_by

    with override(invited_by.language):
        send_mail(
            title=title,
            template_name="workspaces/mails/invite_new_user",
            template_variables={
                "workspace": invitation.workspace.name,
                "owner": invited_by.display_name,
                "owner_email": invited_by.email,
                "url": action_url,
            },
            recipient_list=[invitation.email],
            attachments=get_email_attachments(),
        )

        track(
            request=None,
            event="emails.invite_sent",
            properties={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "workspace": invitation.workspace.slug,
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
    IASO_FORMS = "IASO_FORMS"
    IASO_ORG_UNITS = "IASO_ORG_UNITS"
    IASO_PROJECTS = "IASO_PROJECTS"


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
        IASOMetadataQueryType.IASO_PROJECTS: iaso_client.get_projects,
        IASOMetadataQueryType.IASO_FORMS: iaso_client.get_forms,
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
            url=connection_values.get("url"),
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


def test_connection(connection_type: str, fields: dict[str, str]) -> tuple[bool, str | None]:
    testers = {
        ConnectionType.DHIS2: _test_dhis2,
        ConnectionType.IASO: _test_iaso,
        ConnectionType.POSTGRESQL: _test_postgresql,
        ConnectionType.S3: _test_s3,
        ConnectionType.GCS: _test_gcs,
    }
    tester = testers.get(connection_type)
    if not tester:
        return False, f"Testing is not supported for {connection_type} connections"

    try:
        return tester(fields)
    except Exception as e:
        logger.exception("Connection test failed for %s", connection_type)
        return False, str(e)


def _test_dhis2(fields: dict) -> tuple[bool, str | None]:
    client = DHIS2(
        url=fields["url"],
        username=fields["username"],
        password=fields["password"],
    )
    if not client.ping():
        return False, "DHIS2 instance is not reachable"
    client.me()
    return True, None


def _test_iaso(fields: dict) -> tuple[bool, str | None]:
    client = IASO(
        url=fields["url"],
        username=fields["username"],
        password=fields["password"],
    )
    response = client.api_client.get("api/profiles/me/")
    client.api_client.raise_if_error(response)
    return True, None


def _test_postgresql(fields: dict) -> tuple[bool, str | None]:
    conn = psycopg2.connect(
        host=fields["host"],
        port=int(fields.get("port", 5432)),
        user=fields["username"],
        password=fields["password"],
        dbname=fields["db_name"],
        connect_timeout=CONNECT_TIMEOUT,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
    finally:
        conn.close()
    return True, None


def _test_s3(fields: dict) -> tuple[bool, str | None]:
    client = boto3.client(
        "s3",
        aws_access_key_id=fields.get("access_key_id") or None,
        aws_secret_access_key=fields.get("access_key_secret") or None,
        config=BotoConfig(
            connect_timeout=CONNECT_TIMEOUT,
            read_timeout=CONNECT_TIMEOUT,
            retries={"total_max_attempts": 1},
        ),
    )
    client.head_bucket(Bucket=fields["bucket_name"])
    return True, None


def _test_gcs(fields: dict) -> tuple[bool, str | None]:
    creds = json.loads(fields["service_account_key"])
    client = gcs_storage.Client.from_service_account_info(creds)
    bucket = client.bucket(fields["bucket_name"])
    list(bucket.list_blobs(max_results=1))
    return True, None
