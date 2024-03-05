from __future__ import annotations

import json
import typing
from logging import getLogger
from time import monotonic, sleep

import boto3
import sentry_sdk
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings

import hexa.plugins.connector_s3.models as models

logger = getLogger(__name__)


class S3ApiError(Exception):
    pass


def _get_app_s3_credentials():
    return {
        "username": settings.AWS_USERNAME,
        "access_key_id": settings.AWS_ACCESS_KEY_ID,
        "secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
        "endpoint_url": settings.AWS_ENDPOINT_URL,
        "default_region": settings.AWS_DEFAULT_REGION,
        "user_arn": settings.AWS_USER_ARN,
        "app_role_arn": settings.AWS_APP_ROLE_ARN,
        "permissions_boundary_policy_arn": settings.AWS_PERMISSIONS_BOUNDARY_POLICY_ARN,
    }


def generate_sts_app_s3_credentials(
    *,
    bucket: models.Bucket | None = None,
    duration: int = 60 * 60,
) -> dict[str, str]:
    """Generate temporary S3 credentials for app operations, using the app role.

    This app role should be provisioned beforehand and should have a policy that allows the app to access all the
    environment buckets.
    """
    s3_credentials = _get_app_s3_credentials()
    if s3_credentials["app_role_arn"] == "":
        raise S3ApiError(
            f'Credentials "{s3_credentials["username"]}" have no app role ARN'
        )

    sts_client = boto3.client(
        "sts",
        region_name=s3_credentials["default_region"],
        endpoint_url=(
            None
            if not s3_credentials["endpoint_url"]
            else s3_credentials["endpoint_url"]
        ),
        aws_access_key_id=s3_credentials["access_key_id"],
        aws_secret_access_key=s3_credentials["secret_access_key"],
    )

    assume_role_extra_kwargs = (
        {} if bucket is None else {"Policy": json.dumps(generate_s3_policy([bucket]))}
    )

    response = sts_client.assume_role(
        RoleArn=s3_credentials["app_role_arn"],
        RoleSessionName=f"sts-{s3_credentials['username']}-system",
        DurationSeconds=duration,
        **assume_role_extra_kwargs,
    )

    response_status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if response_status_code != 200:
        raise S3ApiError(
            f'Error when generating STS credentials using principal "{s3_credentials["username"]}" '
            f"(Status: {response_status_code})"
        )

    return response["Credentials"]


def _retry_with_deadline(calling, deadline):
    # This is a mecanism to call a function ("calling") and return the
    # result. If the call throw an exception, the mecanism will add a small
    # delay (1s) and redo the call IF the total runtime is within a given
    # deadline.
    #
    # deadline must be against the wall time -> set it with monotonic()
    #
    # For example, if we need to call some external service during a web
    # request, we have only 30s (typical load balancer timeout) to complete
    # the request, but if the external service call is flaky, this mecanism
    # is a good idea: it will try the call until it succeed, but won't timeout

    while True:
        exception = None
        try:
            return calling()
        except Exception as e:
            # we manage the exception outside of the except block to have
            # cleaner stack trace: we might need to re-raise it again after
            exception = e

        if exception:
            if monotonic() < deadline:
                # still have time -> call again
                sleep(1)
                continue
            else:
                # outside deadline, re-raise
                raise exception
        else:
            # we shouldn't be here -> return always succeed or
            # exception != None
            raise RuntimeError("We shouldn't be here")


def generate_sts_user_s3_credentials(
    *,
    role_identifier: str,
    session_identifier: str,
    read_only_buckets: typing.Sequence[models.Bucket] | None = None,
    read_write_buckets: typing.Sequence[models.Bucket] | None = None,
    duration: int = 12 * 60 * 60,
) -> (bool, dict[str, str]):
    """Generate temporary S3 credentials for a specific use case and for specific buckets.
    Use case includes user notebook session, running pipelines, ...

    The process can be summarized like this:
        1. We first check if we already have a IAM role for the team/pipeline/..
        2. If we don't, create the role
        3. Ensure that the app IAM user can assume the team role
        4. Generates a fresh S3 policy and sets it on the role (replacing the existing one)
        5. Assume the team/pipeline/.. role
    """
    s3_credentials = _get_app_s3_credentials()
    if s3_credentials["endpoint_url"]:
        # We are pointing to a MinIO instance, that doesn't support all this.
        # All we can do is generating temporary credentials using the app role.
        return (
            generate_sts_app_s3_credentials(),
            False,
        )

    if not s3_credentials["user_arn"] or not s3_credentials["app_role_arn"]:
        raise S3ApiError(
            f'Credentials "{s3_credentials["username"]}" incomplete: missing user_arn or role_arn'
        )

    # role_name max length 64 chars.
    role_name = f"{s3_credentials['username']}-s3-{role_identifier}"

    if len(role_name) > 63:
        raise S3ApiError(f"Role_name too long ({len(role_name)} chars, max 63)")

    # start the clock -> deadline is now + 25s
    deadline = monotonic() + 25.0

    # if the call fail for technical reason -> retry it. it wont be useful
    # against 403 (see retry_with_deadline). Doc here:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html
    config = Config(retries={"max_attempts": 20, "mode": "standard"})

    iam_client = boto3.client(
        "iam",
        aws_access_key_id=s3_credentials["access_key_id"],
        aws_secret_access_key=s3_credentials["secret_access_key"],
        config=config,
    )

    try:
        role_data = iam_client.get_role(RoleName=role_name)
        found_role = True
    except iam_client.exceptions.NoSuchEntityException:
        # create a new role outside of exception handler -> better stack trace
        found_role = False
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e
    if not found_role:
        assume_role_policy_doc = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"AWS": s3_credentials["user_arn"]},
                    },
                ],
            }
        )
        role_data = iam_client.create_role(
            RoleName=role_name,
            MaxSessionDuration=duration,
            AssumeRolePolicyDocument=assume_role_policy_doc,
            Description="OpenHEXA auto role for notebooks/pipelines",
            Path="/",
            PermissionsBoundary=s3_credentials["permissions_boundary_policy_arn"],
        )

    policy_doc = json.dumps(
        generate_s3_policy(
            read_only_buckets=read_only_buckets,
            read_write_buckets=read_write_buckets,
        )
    )
    if len(policy_doc) > 10240:
        raise S3ApiError(
            f"Role policies cannot exceed 10240 characters (generated policy is {len(policy_doc)} long)"
        )

    # Build a fresh version of the s3 policy and set it as an inline policy
    # on the role (forced update). this call may fail, retry it within
    # the deadline
    _retry_with_deadline(
        lambda: iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName="s3-access",
            PolicyDocument=policy_doc,
        ),
        deadline,
    )

    sts_client = boto3.client(
        "sts",
        aws_access_key_id=s3_credentials["access_key_id"],
        aws_secret_access_key=s3_credentials["secret_access_key"],
        config=config,
    )

    # Create the temporary token. This call will fail a lot if it's a new
    # role. Retry it until the deadline is expired.
    response = _retry_with_deadline(
        lambda: sts_client.assume_role(
            RoleArn=role_data["Role"]["Arn"],
            RoleSessionName=session_identifier,
            DurationSeconds=duration,
        ),
        deadline,
    )

    response_status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if response_status_code != 200:
        raise S3ApiError(
            f'Error when generating STS credentials using principal "{s3_credentials["username"]}" '
            f"(Status: {response_status_code})"
        )

    return response["Credentials"], not found_role


def generate_s3_policy(
    read_write_buckets: typing.Sequence[models.Bucket] | None = None,
    read_only_buckets: typing.Sequence[models.Bucket] | None = None,
) -> dict:
    statements = []

    if read_only_buckets:
        statements.append(
            {
                "Sid": "S3RO",
                "Effect": "Allow",
                "Action": ["s3:ListBucket", "s3:GetObject"],
                "Resource": [
                    *[f"arn:aws:s3:::{bucket.name}" for bucket in read_only_buckets],
                    *[f"arn:aws:s3:::{bucket.name}/*" for bucket in read_only_buckets],
                ],
            }
        )
        statements.append(
            {
                "Sid": "S3RWK",
                "Effect": "Allow",
                "Action": "s3:*Object",
                "Resource": [
                    f"arn:aws:s3:::{bucket.name}/.s3keep"
                    for bucket in read_only_buckets
                ],
            }
        )
    if read_write_buckets:
        statements.append(
            {
                "Sid": "S3AllActions",
                "Effect": "Allow",
                "Action": ["s3:ListBucket", "s3:*Object"],
                "Resource": [
                    *[f"arn:aws:s3:::{bucket.name}" for bucket in read_write_buckets],
                    *[f"arn:aws:s3:::{bucket.name}/*" for bucket in read_write_buckets],
                ],
            }
        )

    return {
        "Version": "2012-10-17",
        "Statement": statements,
    }


def _build_app_s3_client():
    sts_credentials = generate_sts_app_s3_credentials(
        duration=900,
    )
    s3_credentials = _get_app_s3_credentials()
    return boto3.client(
        "s3",
        region_name=s3_credentials["default_region"],
        endpoint_url=(
            None
            if not s3_credentials["endpoint_url"]
            else s3_credentials["endpoint_url"]
        ),
        aws_access_key_id=sts_credentials["AccessKeyId"],
        aws_secret_access_key=sts_credentials["SecretAccessKey"],
        aws_session_token=sts_credentials["SessionToken"],
        config=Config(signature_version="s3v4"),
    )


def head_bucket(
    *,
    bucket: models.Bucket,
):
    s3_client = _build_app_s3_client()

    try:
        return s3_client.head_bucket(Bucket=bucket.name)
    except ClientError as e:
        raise S3ApiError(e)


def generate_download_url(
    *,
    bucket: models.Bucket,
    target_key: str,
):
    s3_client = _build_app_s3_client()

    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket.name, "Key": target_key},
        ExpiresIn=60 * 10,
    )


def generate_upload_url(
    *,
    bucket: models.Bucket,
    target_key: str,
):
    s3_client = _build_app_s3_client()

    return s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket.name,
            "Key": target_key,
        },
        ExpiresIn=60 * 60,
    )


def get_object_metadata(
    *,
    bucket: models.Bucket,
    object_key: str,
):
    client = _build_app_s3_client()
    metadata = client.head_object(Bucket=bucket.name, Key=object_key)

    return {
        "Key": object_key,
        "LastModified": metadata["LastModified"],
        "Size": metadata["ContentLength"],
        "ETag": metadata["ETag"].strip('"'),
        "StorageClass": metadata.get("StorageClass", "STANDARD"),
        "Type": "directory" if _is_dir(metadata) else "file",
    }


def download_file(*, bucket: models.Bucket, object_key: str, target: str):
    client = _build_app_s3_client()
    return client.download_file(Bucket=bucket.name, Key=object_key, Filename=target)


def upload_file(*, bucket: models.Bucket, object_key: str, src_path: str):
    client = _build_app_s3_client()
    return client.upload_file(Bucket=bucket.name, Key=object_key, Filename=src_path)


def list_objects_metadata(*, bucket: models.Bucket):
    client = _build_app_s3_client()
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


def parse_arn(arn):
    # http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
    elements = arn.split(":", 5)
    result = {
        "arn": elements[0],
        "partition": elements[1],
        "service": elements[2],
        "region": elements[3],
        "account": elements[4],
        "resource": elements[5],
        "resource_type": None,
    }
    if "/" in result["resource"]:
        result["resource_type"], result["resource"] = result["resource"].split("/", 1)
    elif ":" in result["resource"]:
        result["resource_type"], result["resource"] = result["resource"].split(":", 1)
    return result
