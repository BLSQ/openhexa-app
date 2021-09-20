from __future__ import annotations

import json
import typing

import boto3
import stringcase
from botocore.config import Config

import hexa.plugins.connector_s3.models
import hexa.user_management.models


class S3ApiError(Exception):
    pass


def generate_sts_buckets_credentials(
    *,
    user: hexa.user_management.models.User | None = None,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    buckets: typing.Sequence[hexa.plugins.connector_s3.models.Bucket],
    duration: int = 60 * 60,
) -> dict[str, str]:
    """Generate temporary credentials for the provided buckets using the provided principal credentials"""

    if principal_credentials.role_arn == "":
        raise S3ApiError(
            f'Credentials "{principal_credentials.display_name}" have not role ARN'
        )

    client = boto3.client(
        "sts",
        aws_access_key_id=principal_credentials.access_key_id,
        aws_secret_access_key=principal_credentials.secret_access_key,
    )
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": stringcase.pascalcase(
                    stringcase.snakecase(f"{bucket.name}-all-actions")
                ),
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket.name}",
                    f"arn:aws:s3:::{bucket.name}/*",
                ],
            }
            for bucket in buckets
        ],
    }
    if user is not None:
        session_name = f"sts-{principal_credentials.username}-{user.username}"
    else:
        session_name = f"sts-{principal_credentials.username}-system"

    response = client.assume_role(
        Policy=json.dumps(policy),
        RoleArn=principal_credentials.role_arn,
        RoleSessionName=session_name,
        DurationSeconds=duration,
    )

    response_status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if response_status_code != 200:
        raise S3ApiError(
            f'Error when generating STS credentials using principal "{principal_credentials.username}" '
            f"(Status: {response_status_code})"
        )

    return response["Credentials"]


def _build_s3_client(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    bucket: hexa.plugins.connector_s3.models.Bucket,
    user: hexa.user_management.models.User | None = None,
):
    sts_credentials = generate_sts_buckets_credentials(
        user=user,
        principal_credentials=principal_credentials,
        buckets=[bucket],
        duration=900,
    )
    return boto3.client(
        "s3",
        principal_credentials.default_region,
        aws_access_key_id=sts_credentials["AccessKeyId"],
        aws_secret_access_key=sts_credentials["SecretAccessKey"],
        aws_session_token=sts_credentials["SessionToken"],
        config=Config(signature_version="s3v4"),
    )


def head_bucket(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    bucket: hexa.plugins.connector_s3.models.Bucket,
):
    s3_client = _build_s3_client(
        principal_credentials=principal_credentials, bucket=bucket
    )

    return s3_client.head_bucket(bucket.name)


def generate_download_url(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    bucket: hexa.plugins.connector_s3.models.Bucket,
    target_object: hexa.plugins.connector_s3.models.Object,
):
    s3_client = _build_s3_client(
        principal_credentials=principal_credentials, bucket=bucket
    )

    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket.name, "Key": target_object.key},
        ExpiresIn=60 * 10,
    )


def generate_upload_url(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    bucket: hexa.plugins.connector_s3.models.Bucket,
    target_key: str,
):
    s3_client = _build_s3_client(
        principal_credentials=principal_credentials, bucket=bucket
    )

    return s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket.name, "Key": target_key},
        ExpiresIn=60 * 60,
    )
