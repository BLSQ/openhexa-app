import fnmatch
import io
import json
from mimetypes import guess_type

import boto3
import sentry_sdk
from botocore.config import Config
from botocore.exceptions import ClientError

from .base import ObjectsPage, Storage, StorageObject, load_bucket_sample_data_with

LARGE_DIRECTORY_THRESHOLD = 500


def _is_dir(obj: dict) -> bool:
    return obj.get("Size", 0) == 0 and obj.get("Key", "").endswith("/")


def _s3_object_to_storage_obj(obj: dict, bucket_name: str) -> StorageObject:
    key = obj["Key"]
    if _is_dir(obj):
        return StorageObject(
            name=key.rstrip("/").split("/")[-1],
            key=key,
            path=f"{bucket_name}/{key}",
            type="directory",
        )
    last_modified = obj.get("LastModified")
    return StorageObject(
        name=key.split("/")[-1],
        key=key,
        path=f"{bucket_name}/{key}",
        type="file",
        size=obj.get("Size", 0),
        updated_at=last_modified.isoformat() if last_modified else None,
        content_type=guess_type(key)[0] or "application/octet-stream",
    )


def _prefix_to_storage_obj(prefix: str, bucket_name: str) -> StorageObject:
    return StorageObject(
        name=prefix.rstrip("/").split("/")[-1],
        key=prefix,
        path=f"{bucket_name}/{prefix}",
        type="directory",
    )


class S3Storage(Storage):
    storage_type = "s3"

    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        region: str,
        endpoint_url: str | None = None,
        public_endpoint_url: str | None = None,
        role_arn: str | None = None,
    ):
        super().__init__()
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self.region = region
        self._endpoint_url = endpoint_url or None
        self._public_endpoint_url = public_endpoint_url or endpoint_url or None
        self._role_arn = role_arn or None
        self._client = None
        self._public_client = None

    def _build_client(self, endpoint_url: str | None = None):
        return boto3.client(
            "s3",
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key,
            region_name=self.region,
            endpoint_url=endpoint_url,
            config=Config(signature_version="s3v4"),
        )

    @property
    def client(self):
        if self._client is None:
            self._client = self._build_client(self._endpoint_url)
        return self._client

    @property
    def public_client(self):
        """Separate client used only for generating presigned URLs.

        When endpoint_url and public_endpoint_url differ (typical MinIO setup where
        the internal host differs from the externally-reachable host), presigned URLs
        must be signed against the public endpoint so clients can actually reach them.
        """
        if self._public_client is None:
            self._public_client = self._build_client(self._public_endpoint_url)
        return self._public_client

    def bucket_exists(self, bucket_name: str) -> bool:
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                return False
            raise

    def create_bucket(self, bucket_name: str, *args, **kwargs) -> str:
        if self.bucket_exists(bucket_name):
            raise self.exceptions.AlreadyExists(
                f"S3: Bucket {bucket_name} already exists!"
            )
        try:
            # us-east-1 is the default region and rejects an explicit LocationConstraint
            if self.region == "us-east-1":
                self.client.create_bucket(Bucket=bucket_name)
            else:
                self.client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.region},
                )
            return bucket_name
        except ClientError as e:
            if e.response["Error"]["Code"] in (
                "BucketAlreadyExists",
                "BucketAlreadyOwnedByYou",
            ):
                raise self.exceptions.AlreadyExists(
                    f"S3: Bucket {bucket_name} already exists!"
                )
            raise

    def delete_bucket(self, bucket_name: str, force: bool = False) -> None:
        if force:
            paginator = self.client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket_name):
                objects = page.get("Contents", [])
                if objects:
                    self.client.delete_objects(
                        Bucket=bucket_name,
                        Delete={"Objects": [{"Key": obj["Key"]} for obj in objects]},
                    )
        try:
            self.client.delete_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
            raise

    def save_object(
        self, bucket_name: str, file_path: str, file: io.BufferedReader
    ) -> None:
        self.client.upload_fileobj(file, bucket_name, file_path)

    def create_bucket_folder(self, bucket_name: str, folder_key: str) -> StorageObject:
        if not folder_key.endswith("/"):
            folder_key += "/"
        self.client.put_object(Bucket=bucket_name, Key=folder_key, Body=b"")
        return StorageObject(
            name=folder_key.rstrip("/").split("/")[-1],
            key=folder_key,
            path=f"{bucket_name}/{folder_key}",
            type="directory",
        )

    def get_bucket_object(
        self, bucket_name: str, object_key: str
    ) -> StorageObject | None:
        try:
            response = self.client.head_object(Bucket=bucket_name, Key=object_key)
            obj = {
                "Key": object_key,
                "Size": response["ContentLength"],
                "LastModified": response["LastModified"],
            }
            return _s3_object_to_storage_obj(obj, bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] not in ("404", "NoSuchKey"):
                raise

        if not object_key.endswith("/"):
            try:
                self.client.head_object(Bucket=bucket_name, Key=object_key + "/")
                return StorageObject(
                    name=object_key.split("/")[-1],
                    key=object_key + "/",
                    path=f"{bucket_name}/{object_key}/",
                    type="directory",
                )
            except ClientError as e:
                if e.response["Error"]["Code"] not in ("404", "NoSuchKey"):
                    raise

        raise self.exceptions.NotFound(f"Object {object_key} not found")

    def list_bucket_objects(
        self,
        bucket_name,
        prefix=None,
        match_glob=None,
        page: int = 1,
        per_page=30,
        query=None,
        ignore_hidden_files=True,
    ) -> ObjectsPage:
        max_items = (page * per_page) + 1
        start_offset = (page - 1) * per_page
        end_offset = page * per_page

        lower_match_glob = match_glob.lower() if match_glob else None

        def is_match(name: str) -> bool:
            lower_name = name.lower()
            if ignore_hidden_files and any(
                part.startswith(".") for part in name.split("/")
            ):
                return False
            if query and query.lower() not in lower_name:
                return False
            if lower_match_glob and not fnmatch.fnmatch(lower_name, lower_match_glob):
                return False
            return True

        objects = []
        paginator = self.client.get_paginator("list_objects_v2")
        paginate_kwargs = {"Bucket": bucket_name}
        if prefix:
            paginate_kwargs["Prefix"] = prefix

        if match_glob:
            # Flat recursive listing for glob — client-side fnmatch filtering
            total_seen = 0
            for s3_page in paginator.paginate(**paginate_kwargs):
                contents = s3_page.get("Contents", [])
                total_seen += len(contents)
                if total_seen > LARGE_DIRECTORY_THRESHOLD:
                    sentry_sdk.capture_message(
                        f"Large directory listing: bucket '{bucket_name}' returned {total_seen}+ items",
                        level="warning",
                    )
                for obj in contents:
                    if is_match(
                        obj["Key"].split("/")[-1]
                        or obj["Key"].rstrip("/").split("/")[-1]
                    ):
                        objects.append(_s3_object_to_storage_obj(obj, bucket_name))
                if len(objects) >= max_items:
                    break
        else:
            # Hierarchical listing: directories (CommonPrefixes) before files within each page
            paginate_kwargs["Delimiter"] = "/"
            for s3_page in paginator.paginate(**paginate_kwargs):
                for common_prefix in s3_page.get("CommonPrefixes", []):
                    name = common_prefix["Prefix"].rstrip("/").split("/")[-1]
                    if is_match(name):
                        objects.append(
                            _prefix_to_storage_obj(common_prefix["Prefix"], bucket_name)
                        )
                for obj in s3_page.get("Contents", []):
                    if not _is_dir(obj):
                        name = obj["Key"].split("/")[-1]
                        if is_match(name):
                            objects.append(_s3_object_to_storage_obj(obj, bucket_name))
                if len(objects) >= max_items:
                    break

        return ObjectsPage(
            items=objects[start_offset:end_offset],
            page_number=page,
            has_previous_page=page > 1,
            has_next_page=len(objects) > end_offset,
        )

    def delete_object(self, bucket_name: str, object_key: str) -> None:
        try:
            self.client.head_object(Bucket=bucket_name, Key=object_key)
            self.client.delete_object(Bucket=bucket_name, Key=object_key)
            return
        except ClientError as e:
            if e.response["Error"]["Code"] not in ("404", "NoSuchKey"):
                raise

        # Not found as a file — try as a directory prefix
        dir_prefix = object_key if object_key.endswith("/") else object_key + "/"
        paginator = self.client.get_paginator("list_objects_v2")
        keys_to_delete = []
        for s3_page in paginator.paginate(Bucket=bucket_name, Prefix=dir_prefix):
            for obj in s3_page.get("Contents", []):
                keys_to_delete.append({"Key": obj["Key"]})

        if not keys_to_delete:
            raise self.exceptions.NotFound(f"Object {object_key} not found")

        for i in range(0, len(keys_to_delete), 1000):
            self.client.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": keys_to_delete[i : i + 1000]},
            )

    def generate_download_url(
        self, *, bucket_name: str, target_key: str, force_attachment=False, **kwargs
    ) -> str | None:
        params = {"Bucket": bucket_name, "Key": target_key}
        if force_attachment:
            filename = target_key.split("/")[-1]
            params["ResponseContentDisposition"] = f"attachment; filename={filename}"
        return self.public_client.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=600,
        )

    def generate_upload_url(
        self,
        *,
        bucket_name: str,
        target_key: str,
        content_type: str | None = None,
        raise_if_exists: bool = False,
        **kwargs,
    ) -> tuple[str, dict | None]:
        if raise_if_exists:
            try:
                self.client.head_object(Bucket=bucket_name, Key=target_key)
                raise self.exceptions.AlreadyExists(target_key)
            except ClientError as e:
                if e.response["Error"]["Code"] not in ("404", "NoSuchKey"):
                    raise

        params = {"Bucket": bucket_name, "Key": target_key}
        if content_type:
            params["ContentType"] = content_type

        url = self.public_client.generate_presigned_url(
            "put_object",
            Params=params,
            ExpiresIn=3600,
        )
        return url, None

    def read_object(self, bucket_name: str, file_path: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=file_path)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
                raise self.exceptions.NotFound(f"Object {file_path} not found")
            raise

    def load_bucket_sample_data(self, bucket_name: str):
        load_bucket_sample_data_with(bucket_name, self)

    def _assume_role_credentials(self, bucket_name: str) -> dict:
        sts_client = boto3.client(
            "sts",
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key,
            region_name=self.region,
            endpoint_url=self._endpoint_url,
        )
        policy = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:ListBucket",
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:DeleteObject",
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{bucket_name}",
                            f"arn:aws:s3:::{bucket_name}/*",
                        ],
                    }
                ],
            }
        )
        response = sts_client.assume_role(
            RoleArn=self._role_arn,
            RoleSessionName=f"openhexa-workspace-{bucket_name}",
            Policy=policy,
            DurationSeconds=3600,
        )
        return response["Credentials"]

    def get_bucket_mount_config(self, bucket_name: str) -> dict:
        base = {
            "WORKSPACE_STORAGE_ENGINE_S3_BUCKET_NAME": bucket_name,
            "WORKSPACE_STORAGE_ENGINE_S3_REGION_NAME": self.region,
            "WORKSPACE_STORAGE_ENGINE_S3_ENDPOINT_URL": self._endpoint_url or "",
        }

        if self._role_arn:
            try:
                creds = self._assume_role_credentials(bucket_name)
                return {
                    **base,
                    "WORKSPACE_STORAGE_ENGINE_S3_ACCESS_KEY_ID": creds["AccessKeyId"],
                    "WORKSPACE_STORAGE_ENGINE_S3_SECRET_ACCESS_KEY": creds[
                        "SecretAccessKey"
                    ],
                    "WORKSPACE_STORAGE_ENGINE_S3_SESSION_TOKEN": creds["SessionToken"],
                }
            except Exception:
                pass  # fall through to static credentials

        return {
            **base,
            "WORKSPACE_STORAGE_ENGINE_S3_ACCESS_KEY_ID": self._access_key_id,
            "WORKSPACE_STORAGE_ENGINE_S3_SECRET_ACCESS_KEY": self._secret_access_key,
        }
