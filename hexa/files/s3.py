import boto3
import typing
import json
from django.conf import settings
from django.core.exceptions import ValidationError
from dataclasses import dataclass
import botocore

from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, botocore.response.StreamingBody):
        return None
    raise TypeError("Type %s not serializable" % type(obj))


@dataclass
class ObjectsPage:
    items: typing.List[any]
    has_next_page: bool
    has_previous_page: bool
    page_number: int


def get_storage_client(type="s3"):
    # TODO see if I can reuse the existing "aws" related things in django settings
    s3 = boto3.client(
        type,
        endpoint_url="http://minio:9000",
        aws_access_key_id="minio_access_key",
        aws_secret_access_key="minio_secret_key",
    )
    return s3


def _is_dir(blob):
    return blob["Size"] == 0 and blob["Key"].endswith("/")


def _blob_to_dict(blob, bucket_name):
    name = blob["Key"]
    return {
        "name": name.split("/")[-2] if _is_dir(blob) else name.split("/")[-1],
        "key": name,
        "path": "/".join([bucket_name, name]),
        "content_type": blob.get("ContentType"),
        "updated": blob["LastModified"],
        "size": blob["Size"],
        "type": "directory" if _is_dir(blob) else "file",
    }


def _prefix_to_dict(bucket_name: str, name: str):
    return {
        "name": name.split("/")[-2],
        "key": name,
        "path": "/".join([bucket_name, name]),
        "size": 0,
        "type": "directory",
    }


class S3BucketWrapper:
    def __init__(self, bucket_name) -> None:
        self.bucket_name = bucket_name
        self.name = bucket_name  # keep backward compat with gcp

    def blob(self, file_name, size=None, content_type="text/plain"):
        get_storage_client().put_object(
            Body="file_name",
            Bucket=self.bucket_name,
            Key=file_name,
            ContentType=content_type,
        )


def _create_bucket(bucket_name: str):
    s3 = get_storage_client()
    try:
        return s3.create_bucket(Bucket=bucket_name)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        # https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
        raise ValidationError(f"{bucket_name} already exist")


def _upload_object(bucket_name: str, file_name: str, source: str):
    return get_storage_client().put_object(
        Filename=source,
        Bucket=bucket_name,
        Key=file_name,
    )


def _list_bucket_objects(bucket_name, prefix, page, per_page, ignore_hidden_files):
    prefix = prefix or ""
    max_items = (page * per_page) + 1
    start_offset = (page - 1) * per_page
    end_offset = page * per_page

    response = get_storage_client().list_objects_v2(
        Bucket=bucket_name, Delimiter="/", Prefix=prefix
    )
    prefixes = (
        sorted([x["Prefix"] for x in response["CommonPrefixes"]])
        if "CommonPrefixes" in response
        else []
    )
    objects = []
    for current_prefix in prefixes:
        res = _prefix_to_dict(bucket_name, current_prefix)
        if current_prefix == prefix:
            continue
        if not ignore_hidden_files or not res["name"].startswith("."):
            objects.append(res)

    files = response.get("Contents", [])

    for file in files:
        if _is_dir(file):
            # We ignore objects that are directories (object with a size = 0 and ending with a /)
            # because they are already listed in the prefixes
            continue

        res = _blob_to_dict(file, bucket_name)

        if res["key"] == prefix:
            continue

        if not ignore_hidden_files or not res["name"].startswith("."):
            objects.append(res)

    return ObjectsPage(
        items=objects[start_offset:end_offset],
        page_number=page,
        has_previous_page=page > 1,
        has_next_page=len(objects) > page * per_page,
    )


def _delete_bucket(bucket_name: str, fully):
    s3 = get_storage_client()
    try:
        response = s3.list_objects_v2(
            Bucket=bucket_name,
        )

        if fully:
            while response["KeyCount"] > 0:
                print(
                    "Deleting %d objects from bucket %s"
                    % (len(response["Contents"]), bucket_name)
                )
                response = s3.delete_objects(
                    Bucket=bucket_name,
                    Delete={
                        "Objects": [{"Key": obj["Key"]} for obj in response["Contents"]]
                    },
                )
                response = s3.list_objects_v2(
                    Bucket=bucket_name,
                )
        return s3.delete_bucket(Bucket=bucket_name)
    except s3.exceptions.NoSuchBucket:
        return


def _get_short_lived_downscoped_access_token(bucket_name):
    # highly inspired by https://gist.github.com/manics/305f4cc56d0ac6431893cde17b1ba8c4

    token_lifetime = 3600
    if settings.GCS_TOKEN_LIFETIME is not None:
        token_lifetime = int(settings.GCS_TOKEN_LIFETIME)

    sts_service = get_storage_client("sts")
    prefix = "*"

    # Access policies
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html#policies_session
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html
    # https://aws.amazon.com/premiumsupport/knowledge-center/s3-folder-user-access/

    # TODO adapt/verify that the policy matches the gcp token one
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ListObjectsInBucket",
                "Effect": "Allow",
                "Action": "s3:ListBucket",
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
                "Condition": {"StringLike": {"s3:prefix": [prefix]}},
            },
            {
                "Sid": "ManageObjectsInBucket",
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": [f"arn:aws:s3:::{bucket_name}/{prefix}"],
            },
        ],
    }

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts.html#STS.Client.assume_role
    # TODO what if we really want a real s3 ?
    # we probably need the roleArn and RoleSessionName ?
    # is this AWS_USER_ARN and AWS_APP_ROLE_ARN ?
    response = sts_service.assume_role(
        RoleArn="arn:x:ignored:by:minio:",
        RoleSessionName="ignored-by-minio",
        # PolicyArns=[{'arn': 'string'}],
        Policy=json.dumps(policy),
        DurationSeconds=token_lifetime,
    )

    # response_json = json.dumps(response, indent=4, default=json_serial)
    # for debugging

    return [
        {
            "endpoint_url": sts_service.__dict__["meta"].__dict__["_endpoint_url"],
            "aws_access_key_id": response["Credentials"]["AccessKeyId"],
            "aws_secret_access_key": response["Credentials"]["SecretAccessKey"],
            "aws_session_token": response["Credentials"]["SessionToken"],
        },
        response["Credentials"]["Expiration"],
    ]


def ensure_is_folder(object_key: str):
    if object_key.endswith("/") is False:
        return object_key + "/"
    return object_key


def _create_bucket_folder(bucket_name: str, folder_key: str):
    s3 = get_storage_client()

    object = {
        "Body": "",
        "Bucket": bucket_name,
        "Key": ensure_is_folder(folder_key),
        "ContentType": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    s3.put_object(**object)

    final_object = s3.get_object(Bucket=bucket_name, Key=object["Key"])
    # print(json.dumps(object, indent=4, default=json_serial))
    # the get_object isn't the same payload as the list :(
    final_object["Key"] = object["Key"]
    final_object["Size"] = 0
    return _blob_to_dict(final_object, bucket_name)


class S3Client:
    @staticmethod
    def create_bucket(bucket_name: str):
        _create_bucket(bucket_name)
        return S3BucketWrapper(bucket_name)

    @staticmethod
    def upload_object(bucket_name: str, file_name: str, source: str):
        return _upload_object(bucket_name, file_name, source)

    @staticmethod
    def create_bucket_folder(bucket_name: str, folder_key: str):
        return _create_bucket_folder(bucket_name, folder_key)

    @staticmethod
    def generate_download_url(
        bucket_name: str, target_key: str, force_attachment=False
    ):
        return _generate_download_url(bucket_name, target_key, force_attachment)

    @staticmethod
    def get_bucket_object(bucket_name: str, object_key: str):
        return _get_bucket_object(bucket_name, object_key)

    @staticmethod
    def list_bucket_objects(
        bucket_name, prefix=None, page: int = 1, per_page=30, ignore_hidden_files=True
    ):
        return _list_bucket_objects(
            bucket_name, prefix, page, per_page, ignore_hidden_files
        )

    @staticmethod
    def get_short_lived_downscoped_access_token(bucket_name):
        return _get_short_lived_downscoped_access_token(bucket_name)

    @staticmethod
    def delete_bucket(bucket_name: str, fully: bool = False):
        return _delete_bucket(bucket_name, fully)
