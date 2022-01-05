from __future__ import annotations

import json
import typing
from logging import getLogger
from time import sleep

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

import hexa.plugins.connector_s3.models

logger = getLogger(__name__)


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


def generate_sts_user_s3_credentials(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    role_identifier: str,
    session_identifier: str,
    read_only_buckets: typing.Sequence[hexa.plugins.connector_s3.models.Bucket],
    read_write_buckets: typing.Sequence[hexa.plugins.connector_s3.models.Bucket],
    duration: int = 60 * 60,
) -> typing.Dict[str, str]:
    """Generate temporary S3 credentials for a specific team and for specific buckets.

    The process can be summarized like this:

        1. We first check if we already have a IAM role for the team
        2. If we don't, create the role
        3. Ensure that the app IAM user can assume the team role
        4. Generates a fresh S3 policy for the team role and sets it on the role (replacing the existing one)
        5. Assume the team role
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

    # Get or create the team role with the proper assume role policy. role_name max length 64 chars.
    role_name = f"{principal_credentials.username}-s3-{role_identifier}"
    assume_role_policy_doc = json.dumps(
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
    )
    try:
        role_data = iam_client.get_role(RoleName=role_name)
    except iam_client.exceptions.NoSuchEntityException:
        role_data = iam_client.create_role(
            RoleName=role_name,
            MaxSessionDuration=12 * 60 * 60,
            AssumeRolePolicyDocument=assume_role_policy_doc,
        )
        # Very unfortunate, but the assume role policy effect is not immediate
        sleep(10)

    policy_doc = json.dumps(
        generate_s3_policy(
            [b.name for b in read_write_buckets], [b.name for b in read_only_buckets]
        )
    )
    if len(policy_doc) > 10240:
        raise S3ApiError(
            f"Role policies cannot exceed 10240 characters (generated policy is {len(policy_doc)} long)"
        )

    # Build a fresh version of the s3 policy and set it as an inline policy on the role (forced update)
    iam_client.put_role_policy(
        RoleName=role_data["Role"]["RoleName"],
        PolicyName="s3-access",
        PolicyDocument=policy_doc,
    )

    # We can then assume the team role
    sts_client = boto3.client(
        "sts",
        aws_access_key_id=principal_credentials.access_key_id,
        aws_secret_access_key=principal_credentials.secret_access_key,
    )

    role_session_name = (
        f"sts-{principal_credentials.username[:22]}-{session_identifier}"
    )

    response = sts_client.assume_role(
        RoleArn=role_data["Role"]["Arn"],
        RoleSessionName=role_session_name,
        DurationSeconds=duration,
    )

    response_status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if response_status_code != 200:
        raise S3ApiError(
            f'Error when generating STS credentials using principal "{principal_credentials.username}" '
            f"(Status: {response_status_code})"
        )

    return response["Credentials"]


def generate_s3_policy(
    read_write_bucket_names: typing.Sequence[str] = None,
    read_only_bucket_names: typing.Optional[typing.Sequence[str]] = None,
) -> typing.Dict:
    statements = []

    if read_only_bucket_names:
        statements.append(
            {
                "Sid": "S3RO",
                "Effect": "Allow",
                "Action": ["s3:ListBucket", "s3:GetObject*"],
                "Resource": [
                    *[
                        f"arn:aws:s3:::{bucket_name}"
                        for bucket_name in read_only_bucket_names
                    ],
                    *[
                        f"arn:aws:s3:::{bucket_name}/*"
                        for bucket_name in read_only_bucket_names
                    ],
                ],
            }
        )
        statements.append(
            {
                "Sid": "S3RWK",
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/.s3keep"
                    for bucket_name in read_only_bucket_names
                ],
            }
        )
    if read_write_bucket_names:
        statements.append(
            {
                "Sid": "S3AllActions",
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": [
                    *[
                        f"arn:aws:s3:::{bucket_name}"
                        for bucket_name in read_write_bucket_names
                    ],
                    *[
                        f"arn:aws:s3:::{bucket_name}/*"
                        for bucket_name in read_write_bucket_names
                    ],
                ],
            }
        )

    return {
        "Version": "2012-10-17",
        "Statement": statements,
    }


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


def get_object_metadata(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    bucket: hexa.plugins.connector_s3.models.Bucket,
    object_key: str,
):
    client = _build_app_s3_client(principal_credentials=principal_credentials)
    metadata = client.head_object(Bucket=bucket.name, Key=object_key)

    return {
        "Key": object_key,
        "LastModified": metadata["LastModified"],
        "Size": metadata["ContentLength"],
        "ETag": metadata["ETag"].strip('"'),
        "StorageClass": metadata.get("StorageClass", "STANDARD"),
        "Type": "directory" if _is_dir(metadata) else "file",
    }


def list_objects_metadata(
    *,
    principal_credentials: hexa.plugins.connector_s3.models.Credentials,
    bucket: hexa.plugins.connector_s3.models.Bucket,
):
    client = _build_app_s3_client(principal_credentials=principal_credentials)
    kwargs, objects = {"Bucket": bucket.name}, []

    while True:
        page = client.list_objects_v2(**kwargs)
        if "Contents" not in page:
            assert page["IsTruncated"] is False
            break
        objects.extend(page["Contents"])
        if page["IsTruncated"]:
            kwargs["ContinuationToken"] = page["NextContinuationToken"]
        else:
            break

    # Add "Type" property and add missing pseudo-directories (list_objects_v2 will only return directories that have
    # been explicitly created as objects of size 0 with a key that ends with "/"

    directory_names = set()
    pseudo_directory_names = set()
    pseudo_directory_last_modified = {}
    for metadata in objects:
        metadata["ETag"] = metadata["ETag"].strip('"')
        if _is_dir(metadata):
            metadata["Type"] = "directory"
            directory_names.add(metadata["Key"])
        else:
            metadata["Type"] = "file"

        path = metadata["Key"].strip("/").split("/")

        if len(path) > 1:
            for depth in range(1, len(path)):
                dirname = "/".join(path[:-depth]) + "/"
                pseudo_directory_names.add(dirname)
                if (
                    dirname not in pseudo_directory_last_modified
                    or pseudo_directory_last_modified[dirname]
                    < metadata["LastModified"]
                ):
                    pseudo_directory_last_modified[dirname] = metadata["LastModified"]

    pseudo_directories = [
        {
            "Key": name,
            "LastModified": pseudo_directory_last_modified[name],
            "Size": 0,
            "ETag": "",
            "StorageClass": "STANDARD",
            "Type": "directory",
        }
        for name in pseudo_directory_names
        if name not in directory_names
    ]

    # remove file that are directories (legacy of s3contentmngr)
    # TODO: discuss - should not be necessary anymore
    # objects = [object for object in objects if object["Key"] not in directory_set]

    # merge objects and return
    return objects + pseudo_directories


def _is_dir(object_data: typing.Mapping[str, typing.Any]):
    return object_data.get(
        "Size", object_data.get("ContentLength")
    ) == 0 and object_data["Key"].endswith("/")
