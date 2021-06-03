from __future__ import annotations

import boto3
import json
import typing

import stringcase

import hexa.user_management.models
import hexa.plugins.connector_s3.models


class S3ApiError(Exception):
    pass


def generate_sts_buckets_credentials(
    *,
    user: hexa.user_management.models.User,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    buckets: typing.Sequence[hexa.plugins.connector_s3.models.Bucket],
    duration: int = 60 * 60,
) -> typing.Dict[str, str]:
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
                    stringcase.snakecase(f"{bucket.s3_name}-all-actions")
                ),
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket.s3_name}",
                    f"arn:aws:s3:::{bucket.s3_name}/*",
                ],
            }
            for bucket in buckets
        ],
    }
    response = client.assume_role(
        Policy=json.dumps(policy),
        RoleArn=principal_credentials.role_arn,
        RoleSessionName=f"sts-{principal_credentials.username}-{user.username}",
        DurationSeconds=duration,
    )

    response_status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if response_status_code != 200:
        raise S3ApiError(
            f'Error when generating STS credentials using principal "{principal_credentials.username}" '
            f"(Status: {response_status_code})"
        )

    return response["Credentials"]
