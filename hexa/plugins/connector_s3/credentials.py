import base64
import hashlib
import json

import boto3
from django.contrib.contenttypes.models import ContentType

from hexa.notebooks.credentials import NotebooksCredentials
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.plugins.connector_s3.api import (
    _build_iam_client,
    _get_credentials,
    attach_policy,
    generate_s3_policy,
    generate_sts_user_s3_credentials,
    get_or_create_role,
    parse_arn,
)
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import PermissionMode


def notebooks_credentials(credentials: NotebooksCredentials):
    """Provides the notebooks credentials data that allows users to access S3 buckets in the notebooks component."""

    read_only_buckets = Bucket.objects.filter_for_user(
        credentials.user, mode=PermissionMode.VIEWER
    )
    read_write_buckets = Bucket.objects.filter_for_user(
        credentials.user, mode__in=[PermissionMode.EDITOR, PermissionMode.OWNER]
    )

    # We only need to generate s3 credentials if the user has access to one or more buckets
    if read_only_buckets or read_write_buckets:
        principal_s3_credentials = _get_credentials()

        session_identifier = str(credentials.user.id)
        if credentials.user.is_superuser:
            role_identifier = "superuser"
        else:
            team_ids = ",".join(
                [str(t.id) for t in credentials.user.team_set.order_by("id")]
            )
            role_identifier = hashlib.blake2s(
                team_ids.encode("utf-8"), digest_size=16
            ).hexdigest()

        sts_credentials = generate_sts_user_s3_credentials(
            principal_credentials=principal_s3_credentials,
            read_only_buckets=read_only_buckets,
            read_write_buckets=read_write_buckets,
            role_identifier=role_identifier,
            session_identifier=session_identifier,
            duration=60 * 60 * 12,
        )

        json_config = {
            "AWS_ACCESS_KEY_ID": sts_credentials["AccessKeyId"],
            "AWS_SECRET_ACCESS_KEY": sts_credentials["SecretAccessKey"],
            "AWS_SESSION_TOKEN": sts_credentials["SessionToken"],
            "AWS_DEFAULT_REGION": principal_s3_credentials.default_region,
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
            }
        )
        if principal_s3_credentials.default_region != "":
            credentials.update_env(
                {
                    "AWS_DEFAULT_REGION": principal_s3_credentials.default_region,
                }
            )


def pipelines_credentials(credentials: PipelinesCredentials):
    """
    Provides the notebooks credentials data that allows users to access S3 buckets
    in the pipelines component.
    """
    env = {}

    authorized_datasources = credentials.pipeline.authorized_datasources.filter(
        datasource_type=ContentType.objects.get_for_model(Bucket)
    )
    buckets = [x.datasource for x in authorized_datasources]

    if not buckets:
        return

    # Set up the role dedicated to the pipeline
    principal_s3_credentials = _get_credentials()
    iam_client = _build_iam_client(principal_credentials=principal_s3_credentials)

    principal_role_path = parse_arn(principal_s3_credentials.app_role_arn)["resource"]
    pipeline_app = credentials.pipeline._meta.app_label
    pipeline_role_path = f"/{principal_role_path}/pipelines/{pipeline_app}/"

    role_data = get_or_create_role(
        principal_credentials=principal_s3_credentials,
        role_path=pipeline_role_path,
        role_name=f"{principal_s3_credentials.username}-p-{str(credentials.pipeline.id)}",
        description=f'Role used to run the pipeline "{credentials.pipeline}" ({credentials.pipeline._meta.verbose_name})',
    )

    attach_policy(
        iam_client=iam_client,
        role_name=role_data["Role"]["RoleName"],
        policy_name="s3-access",
        document=generate_s3_policy(
            read_write_bucket_names=[b.name for b in buckets], read_only_bucket_names=[]
        ),
    )

    # Ask new temporary credentials
    sts_client = boto3.client(
        "sts",
        aws_access_key_id=principal_s3_credentials.access_key_id,
        aws_secret_access_key=principal_s3_credentials.secret_access_key,
    )

    sts_response = sts_client.assume_role(
        RoleArn=role_data["Role"]["Arn"],
        RoleSessionName="dag-run",
        DurationSeconds=12 * 60 * 60,
    )

    sts_credentials = sts_response["Credentials"]

    env["AWS_ACCESS_KEY_ID"] = sts_credentials["AccessKeyId"]
    env["AWS_SECRET_ACCESS_KEY"] = sts_credentials["SecretAccessKey"]
    env["AWS_SESSION_TOKEN"] = sts_credentials["SessionToken"]

    # Set some environment variables to help the user
    if principal_s3_credentials.default_region != "":
        env["AWS_DEFAULT_REGION"] = principal_s3_credentials.default_region

    env["AWS_S3_BUCKET_NAMES"] = ",".join(b.name for b in buckets)

    for authorized_bucket in authorized_datasources:
        if authorized_bucket.slug:
            label = authorized_bucket.slug.replace("-", "_").upper()
            env[f"AWS_BUCKET_{label}_NAME"] = authorized_bucket.datasource.name

    credentials.env.update(env)
