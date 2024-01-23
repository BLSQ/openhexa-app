import base64
import json

import boto3
from django.conf import settings
from django.core.exceptions import ValidationError

from .basefs import BaseClient, NotFound, ObjectsPage, load_bucket_sample_data_with

default_region = "eu-central-1"


def get_storage_client(type="s3"):
    """type is the boto client type s3 by default but can be sts or other client api"""
    s3 = boto3.client(
        type,
        endpoint_url=settings.AWS_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=default_region,
    )
    return s3


def _is_dir(blob):
    return blob["Size"] == 0 and blob["Key"].endswith("/")


def _is_dir_object(blob, object_key):
    return blob["ContentLength"] == 0 and object_key.endswith("/")


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


def _object_to_dict(blob, bucket_name, object_key):
    name = object_key
    return {
        "name": name.split("/")[-2]
        if _is_dir_object(blob, object_key)
        else name.split("/")[-1],
        "key": name,
        "path": "/".join([bucket_name, name]),
        "content_type": blob.get("ContentType"),
        "updated": blob["LastModified"],
        "size": blob["ContentLength"],
        "type": "directory" if _is_dir_object(blob, object_key) else "file",
    }


def _prefix_to_dict(bucket_name: str, name: str):
    return {
        "name": name.split("/")[-2],
        "key": name,
        "path": "/".join([bucket_name, name]),
        "size": 0,
        "type": "directory",
    }


# allows to keep the test compatible between gcp and s3
# for the fixture, the tests creates blobs
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


def ensure_is_folder(object_key: str):
    if object_key.endswith("/") is False:
        return object_key + "/"
    return object_key


def _get_bucket_object(bucket_name: str, object_key: str):
    client = get_storage_client()
    try:
        object = client.head_object(Bucket=bucket_name, Key=object_key)

    except Exception as e:
        if "the HeadObject operation: Not Found" in str(e):
            raise NotFound(f"{bucket_name} {object_key} not found")
        # else just throw the initial error
        raise e

    return _object_to_dict(object, bucket_name=bucket_name, object_key=object_key)


class S3Client(BaseClient):
    def create_bucket(self, bucket_name: str):
        s3 = get_storage_client()
        try:
            bucket = s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": default_region},
            )

            # Define the configuration rules
            cors_configuration = {
                "CORSRules": [
                    {
                        "AllowedHeaders": [
                            "Authorization",
                            "Content-Range",
                            "Accept",
                            "Content-Type",
                            "Origin",
                            "Range",
                        ],
                        "AllowedMethods": ["GET", "PUT"],
                        "AllowedOrigins": settings.CORS_ALLOWED_ORIGINS,
                        "ExposeHeaders": [
                            "ETag",
                            "x-amz-request-id",
                            "Authorization",
                            "Content-Range",
                            "Accept",
                            "Content-Type",
                            "Origin",
                            "Range",
                        ],
                        "MaxAgeSeconds": 3000,
                    }
                ]
            }

            s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_configuration)
            return S3BucketWrapper(bucket_name)
        except s3.exceptions.ClientError as exc:
            # https://github.com/VeemsHQ/veems/blob/3e2e75c3407bc1f98395fe94c0e03367a82852c9/veems/media/upload_manager.py#L51C1-L51C1

            if "MalformedXML" in str(exc):
                from warnings import warn

                warn(
                    "Put bucket CORS failed. "
                    "Only if using Minio S3 backend is this okay, "
                    "otherwise investigate. %s",
                    DeprecationWarning,
                    stacklevel=2,
                )
            else:
                raise exc
        except s3.exceptions.BucketAlreadyOwnedByYou:
            # https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
            raise ValidationError(f"{bucket_name} already exist")

        return S3BucketWrapper(bucket_name)

    def upload_object(self, bucket_name: str, file_name: str, source: str):
        return get_storage_client().upload_file(source, bucket_name, file_name)

    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        s3 = get_storage_client()

        object = {
            "Body": "",
            "Bucket": bucket_name,
            "Key": ensure_is_folder(folder_key),
            "ContentType": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        s3.put_object(**object)

        final_object = s3.get_object(Bucket=bucket_name, Key=object["Key"])

        # the get_object isn't the same payload as the list :(
        final_object["Key"] = object["Key"]
        final_object["Size"] = 0
        return _blob_to_dict(final_object, bucket_name)

    def generate_download_url(
        self, bucket_name: str, target_key: str, force_attachment=False
    ):
        s3 = get_storage_client()
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": target_key},
            ExpiresIn=3600,
        )
        return url

    def generate_upload_url(
        self,
        bucket_name: str,
        target_key: str,
        content_type: str = None,
        raise_if_exists: bool = False,
    ):
        s3_client = get_storage_client()

        if raise_if_exists:
            try:
                s3_client.head_object(Bucket=bucket_name, Key=target_key)
                raise ValidationError(
                    f"File already exists. Choose a different object key Object {target_key}."
                )
            except s3_client.exceptions.ClientError as e:
                if e.response["Error"]["Code"] != "404":
                    # don't hide non "not found errors"
                    raise e

        params = {
            "Bucket": bucket_name,
            "Key": target_key,
        }

        if content_type:
            params["ContentType"] = content_type

        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params=params,
            ExpiresIn=3600,  # URL expiration time in seconds
        )
        return url

    def get_bucket_object(self, bucket_name: str, object_key: str):
        return _get_bucket_object(bucket_name, object_key)

    def list_bucket_objects(
        self,
        bucket_name,
        prefix=None,
        page: int = 1,
        per_page=30,
        query=None,
        ignore_hidden_files=True,
    ):
        prefix = prefix or ""
        max_items = (page * per_page) + 1
        start_offset = (page - 1) * per_page
        end_offset = page * per_page
        paginator = get_storage_client().get_paginator("list_objects_v2")

        pages = paginator.paginate(
            Bucket=bucket_name,
            Delimiter="/",
            Prefix=prefix,
        )

        def is_object_match_query(obj):
            if ignore_hidden_files and obj["name"].startswith("."):
                return False
            if not query:
                return True
            return query.lower() in obj["name"].lower()

        pageIndex = 0
        for response in pages:
            pageIndex = pageIndex + 1

            prefixes = (
                sorted([x["Prefix"] for x in response["CommonPrefixes"]])
                if "CommonPrefixes" in response
                else []
            )
            objects = []

            for current_prefix in prefixes:
                res = _prefix_to_dict(bucket_name, current_prefix)
                if is_object_match_query(res):
                    objects.append(res)

            files = response.get("Contents", [])

            for file in files:
                if _is_dir(file):
                    # We ignore objects that are directories (object with a size = 0 and ending with a /)
                    # because they are already listed in the prefixes
                    continue

                res = _blob_to_dict(file, bucket_name)

                if res["key"] == prefix and prefix.endswith("/"):
                    print("skipping ", res, prefix)
                    continue

                if is_object_match_query(res):
                    objects.append(res)

        sorted(objects, key=lambda x: x["key"])
        items = objects[start_offset:end_offset]

        return ObjectsPage(
            items=items,
            page_number=page,
            has_previous_page=page > 1,
            has_next_page=len(objects) > (page * per_page),
        )

    # TODO handle read-only mode.
    def get_short_lived_downscoped_access_token(self, bucket_name):
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
        # TODO what if we really want a real s3 see *ignored* ?
        #  - we probably need the roleArn and RoleSessionName ?
        #  - is this AWS_USER_ARN and AWS_APP_ROLE_ARN ?
        response = sts_service.assume_role(
            RoleArn=settings.AWS_APP_ROLE_ARN or "arn:x:ignored:by:minio:",
            RoleSessionName="ignored-by-minio",
            Policy=json.dumps(policy),
            DurationSeconds=token_lifetime,
        )

        return [
            {
                "endpoint_url": sts_service.__dict__["meta"].__dict__["_endpoint_url"],
                "aws_access_key_id": response["Credentials"]["AccessKeyId"],
                "aws_secret_access_key": response["Credentials"]["SecretAccessKey"],
                "aws_session_token": response["Credentials"]["SessionToken"],
            },
            response["Credentials"]["Expiration"],
            "s3",
        ]

    def delete_bucket(self, bucket_name: str, fully: bool = False):
        s3 = get_storage_client()
        try:
            response = s3.list_objects_v2(
                Bucket=bucket_name,
            )

            if fully:
                while response["KeyCount"] > 0:
                    # print("Deleting %d objects from bucket %s" % (len(response["Contents"]), bucket_name))
                    response = s3.delete_objects(
                        Bucket=bucket_name,
                        Delete={
                            "Objects": [
                                {"Key": obj["Key"]} for obj in response["Contents"]
                            ]
                        },
                    )
                    response = s3.list_objects_v2(
                        Bucket=bucket_name,
                    )
            return s3.delete_bucket(Bucket=bucket_name)
        except s3.exceptions.NoSuchBucket:
            return
        except s3.exceptions.ClientError as exc:

            if "InvalidBucketName" in str(exc):
                return

            raise exc

    def delete_object(self, bucket_name: str, file_name: str):
        client = get_storage_client()
        blob = _get_bucket_object(bucket_name=bucket_name, object_key=file_name)
        if blob["type"] == "directory":
            blobs = self.list_bucket_objects(bucket_name=bucket_name, prefix=file_name)
            client.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": [{"Key": b["key"]} for b in blobs]},
            )
        else:
            client.delete_object(Bucket=bucket_name, Key=file_name)
        return

    def load_bucket_sample_data(self, bucket_name: str):
        return load_bucket_sample_data_with(bucket_name, self)

    def get_token_as_env_variables(self, token):
        # the fuse config
        json_config = {
            "AWS_ENDPOINT": token["endpoint_url"],
            "AWS_ACCESS_KEY_ID": token["aws_access_key_id"],
            "AWS_SECRET_ACCESS_KEY": token["aws_secret_access_key"],
            "AWS_SESSION_TOKEN": token["aws_session_token"],
            "AWS_DEFAULT_REGION": token.get("default_region", ""),
        }

        return {
            "AWS_ACCESS_KEY_ID": token["aws_access_key_id"],
            "AWS_SECRET_ACCESS_KEY": token["aws_secret_access_key"],
            "AWS_ENDPOINT_URL": token["endpoint_url"],
            "AWS_SESSION_TOKEN": token["aws_session_token"],
            "AWS_S3_FUSE_CONFIG": base64.b64encode(
                json.dumps(json_config).encode()
            ).decode(),
        }
