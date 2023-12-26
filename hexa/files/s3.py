import boto3
import typing
from dataclasses import dataclass

@dataclass
class ObjectsPage:
    items: typing.List[any]
    has_next_page: bool
    has_previous_page: bool
    page_number: int


def get_storage_client():
    s3 = boto3.client(
        "s3",
        endpoint_url="http://minio:9000",
        aws_access_key_id="minio_access_key",
        aws_secret_access_key="minio_secret_key",
    )
    return s3

def _is_dir(blob):
    return blob["Size"] == 0 and blob["Key"].endswith("/")

def _blob_to_dict(blob, bucket_name):
    print(blob)
    name = blob["Key"]
    return {
        "name": name.split("/")[-2] if _is_dir(blob) else name.split("/")[-1],
        "key": name,
        "path": "/".join([bucket_name, name]),
        "content_type": blob.get('ContentType'),
        "updated": blob['LastModified'],
        "size": blob['Size'],
        "type": "directory" if _is_dir(blob) else "file",
    }


class S3BucketWrapper:
    def __init__(self, bucket_name) -> None:
        self.bucket_name = bucket_name
        self.name = bucket_name # keep backward compat with gcp

    def blob(self, file_name, size=None, content_type="text/plain"):
        get_storage_client().put_object(
            Body="file_name",
            Bucket=self.bucket_name,
            Key=file_name,
            ContentType=content_type
        )


def _create_bucket(bucket_name: str):
    try:
        return get_storage_client().create_bucket(Bucket=bucket_name)
    except:
        return None


def _upload_object(bucket_name: str, file_name: str, source: str):
    return get_storage_client().put_object(
        Filename=source,
        Bucket=bucket_name,
        Key=file_name,
    )

def  _list_bucket_objects(
            bucket_name, prefix, page, per_page, ignore_hidden_files
    ):

    max_items = (page * per_page) + 1
    start_offset = (page - 1) * per_page
    end_offset = page * per_page

    response = get_storage_client().list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = response.get("Contents")
    objects = []
    for file in files:
        res = _blob_to_dict(file, bucket_name)
        if not ignore_hidden_files or not res["name"].startswith("."):
            objects.append(res)        
        print(f"file_name: {file['Key']}, size: {file['Size']}")

    return ObjectsPage(
            items=objects[start_offset:end_offset],
            page_number=page,
            has_previous_page=page > 1,
            has_next_page=len(objects) > page * per_page,
        )





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
