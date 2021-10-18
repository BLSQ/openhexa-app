from __future__ import annotations

import json
import typing

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.utils.text import slugify

import hexa.plugins.connector_s3.models


class S3ApiError(Exception):
    pass


def generate_sts_app_s3_credentials(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    bucket: typing.Optional[hexa.plugins.connector_s3.models.Bucket] = None,
    duration: int = 60 * 60,
) -> typing.Dict[str, str]:
    """Generate temporary S3 credentials for app operations, using the app role.

    This app role should be provisioned beforehand and should have a policy that allows the app to access all the
    environment buckets.
    """

    if principal_credentials.app_role_arn == "":
        raise S3ApiError(
            f'Credentials "{principal_credentials.display_name}" have no app role ARN'
        )

    sts_client = boto3.client(
        "sts",
        aws_access_key_id=principal_credentials.access_key_id,
        aws_secret_access_key=principal_credentials.secret_access_key,
    )

    assume_role_extra_kwargs = (
        {}
        if bucket is None
        else {"Policy": json.dumps(generate_s3_policy([bucket.name]))}
    )

    response = sts_client.assume_role(
        RoleArn=principal_credentials.app_role_arn,
        RoleSessionName=f"sts-{principal_credentials.username}-system",
        DurationSeconds=duration,
        **assume_role_extra_kwargs,
    )

    response_status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if response_status_code != 200:
        raise S3ApiError(
            f'Error when generating STS credentials using principal "{principal_credentials.username}" '
            f"(Status: {response_status_code})"
        )

    return response["Credentials"]


def generate_sts_team_s3_credentials(
    *,
    user: hexa.user_management.models.User,
    team: hexa.user_management.models.Team,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    buckets: typing.Sequence[hexa.plugins.connector_s3.models.Bucket],
    duration: int = 60 * 60,
) -> typing.Dict[str, str]:
    """Generate temporary S3 credentials for a specific team and for specific buckets.

    The process can be summarized like this:

        1. We first check if we already have a IAM role for the team
        2. If we don't, create the role
        3. Ensure that the app IAM user can assume the team role
        4. Generates a fresh S3 policy for the team role and sets it on the role (replacing the existing one)
    """

    if principal_credentials.user_arn == "":
        raise S3ApiError(
            f'Credentials "{principal_credentials.display_name}" have no user ARN'
        )

    iam_client = boto3.client(
        "iam",
        aws_access_key_id=principal_credentials.access_key_id,
        aws_secret_access_key=principal_credentials.secret_access_key,
    )

    # Get or create the team role
    team_role_name = f"{principal_credentials.username}-{slugify(team.name)}"
    try:
        role_data = iam_client.get_role(RoleName=team_role_name)
    except iam_client.exceptions.NoSuchEntityException:
        role_data = iam_client.create_role(
            RoleName=team_role_name, MaxSessionDuration=12 * 60 * 60
        )

    # Make sure that the IAM app user can assume the team role
    iam_client.update_assume_role_policy(
        RoleName=team_role_name,
        PolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"AWS": principal_credentials.user_arn},
                    },
                ],
            }
        ),
    )

    # Build a fresh version of the s3 policy and set it as an inline policy on the role (forced update)
    iam_client.put_role_policy(
        RoleName=role_data["Role"]["RoleName"],
        PolicyName="s3-access",
        PolicyDocument=json.dumps(generate_s3_policy([b.name for b in buckets])),
    )

    # We can then assume the team role
    sts_client = boto3.client(
        "sts",
        aws_access_key_id=principal_credentials.access_key_id,
        aws_secret_access_key=principal_credentials.secret_access_key,
    )

    response = sts_client.assume_role(
        RoleArn=role_data["Role"]["Arn"],
        RoleSessionName=f"sts-{principal_credentials.username}-{user.email}",
        DurationSeconds=duration,
    )

    response_status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if response_status_code != 200:
        raise S3ApiError(
            f'Error when generating STS credentials using principal "{principal_credentials.username}" '
            f"(Status: {response_status_code})"
        )

    return response["Credentials"]


def generate_s3_policy(bucket_names: typing.Sequence[str]) -> typing.Dict:
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "s3-all-actions",
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": [
                    *[f"arn:aws:s3:::{bucket_name}" for bucket_name in bucket_names],
                    *[f"arn:aws:s3:::{bucket_name}/*" for bucket_name in bucket_names],
                ],
            }
        ],
    }

    return policy


def _build_app_s3_client(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
):
    sts_credentials = generate_sts_app_s3_credentials(
        principal_credentials=principal_credentials,
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
    s3_client = _build_app_s3_client(principal_credentials=principal_credentials)

    try:
        return s3_client.head_bucket(Bucket=bucket.name)
    except ClientError as e:
        raise S3ApiError(e)


def generate_download_url(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    bucket: hexa.plugins.connector_s3.models.Bucket,
    target_object: hexa.plugins.connector_s3.models.Object,
):
    s3_client = _build_app_s3_client(principal_credentials=principal_credentials)

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
    s3_client = _build_app_s3_client(principal_credentials=principal_credentials)

    return s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket.name, "Key": target_key},
        ExpiresIn=60 * 60,
    )
