import base64
import hashlib
import json
import typing

from django.contrib.contenttypes.models import ContentType

from hexa.core.credentials import HexaCredentials
from hexa.notebooks.credentials import NotebooksCredentials
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.plugins.connector_s3.api import (
    _get_app_s3_credentials,
    generate_sts_user_s3_credentials,
)
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import PermissionMode


def _generate_credentials(
    credentials: HexaCredentials,
    role_identifier: str,
    read_only_buckets: typing.Optional[typing.Sequence[Bucket]] = None,
    read_write_buckets: typing.Optional[typing.Sequence[Bucket]] = None,
):
    # We only need to generate s3 credentials if the user has access to one or more buckets
    if not (read_only_buckets or read_write_buckets):
        return

    principal_s3_credentials = _get_app_s3_credentials()

    session_identifier = str(credentials.reference_id)

    sts_credentials, fresh_role = generate_sts_user_s3_credentials(
        read_only_buckets=read_only_buckets,
        read_write_buckets=read_write_buckets,
        role_identifier=role_identifier,
        session_identifier=session_identifier,
    )

    json_config = {
        "AWS_ENDPOINT": principal_s3_credentials["endpoint_url"],
        "AWS_ACCESS_KEY_ID": sts_credentials["AccessKeyId"],
        "AWS_SECRET_ACCESS_KEY": sts_credentials["SecretAccessKey"],
        "AWS_SESSION_TOKEN": sts_credentials["SessionToken"],
        "AWS_DEFAULT_REGION": principal_s3_credentials["default_region"],
        "buckets": [
            {"name": b.name, "region": str(b.region), "mode": "RO"}
            for b in read_only_buckets
        ]
        + [
            {"name": b.name, "region": str(b.region), "mode": "RW"}
            for b in read_write_buckets
        ],
    }

    credentials.update_env(
        {
            "AWS_S3_BUCKET_NAMES": ",".join(
                b.name for b in list(read_only_buckets) + list(read_write_buckets)
            ),
            "AWS_S3_FUSE_CONFIG": base64.b64encode(
                json.dumps(json_config).encode()
            ).decode(),
            # Not used by FUSE, but usefull for others
            "AWS_ACCESS_KEY_ID": sts_credentials["AccessKeyId"],
            "AWS_SECRET_ACCESS_KEY": sts_credentials["SecretAccessKey"],
            "AWS_SESSION_TOKEN": sts_credentials["SessionToken"],
            "AWS_FRESH_ROLE": "TRUE" if fresh_role else "FALSE",
        }
    )
    if principal_s3_credentials["default_region"] != "":
        credentials.update_env(
            {
                "AWS_DEFAULT_REGION": principal_s3_credentials["default_region"],
            }
        )


def notebooks_credentials(credentials: NotebooksCredentials):
    """Provides the notebooks credentials data that allows users to access S3 buckets in the notebooks component."""
    read_only_buckets = Bucket.objects.filter_for_user(
        credentials.user, mode=PermissionMode.VIEWER
    )
    read_write_buckets = Bucket.objects.filter_for_user(
        credentials.user, mode__in=[PermissionMode.EDITOR, PermissionMode.OWNER]
    )

    if credentials.user.is_superuser:
        role_identifier = "superuser"
    else:
        team_ids = ",".join(
            [str(t.id) for t in credentials.user.team_set.order_by("id")]
        )
        role_identifier = hashlib.blake2s(
            team_ids.encode("utf-8"), digest_size=16
        ).hexdigest()

    return _generate_credentials(
        credentials, role_identifier, read_only_buckets, read_write_buckets
    )


def pipelines_credentials(credentials: PipelinesCredentials):
    """
    Provides the pipelines credentials data that allows users to access S3 buckets
    in the pipelines component.
    """
    if hasattr(credentials.pipeline, "authorized_datasources"):
        authorized_buckets = credentials.pipeline.authorized_datasources.filter(
            datasource_type=ContentType.objects.get_for_model(Bucket)
        )
        buckets = []
        for authorized_bucket in authorized_buckets:
            buckets.append(authorized_bucket.datasource)
            if authorized_bucket.slug:
                label = authorized_bucket.slug.replace("-", "_").upper()
                credentials.update_env(
                    {f"AWS_BUCKET_{label}_NAME": authorized_bucket.datasource.name}
                )
        role_identifier = f"p-{credentials.reference_id}"
    else:
        # Pipelines V2
        buckets = Bucket.objects.filter_for_user(credentials.pipeline.user)
        role_identifier = "superuser"

    return _generate_credentials(credentials, role_identifier, [], buckets)
