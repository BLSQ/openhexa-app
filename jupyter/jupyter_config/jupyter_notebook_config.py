import os

from notebook.services.contents.largefilemanager import LargeFileManager
from habari.contents import MultiContentsManager, GCSContentsManager, S3ContentsManager


c = get_config()

c.NotebookApp.contents_manager_class = MultiContentsManager
c.MultiContentsManager.manager_classes = {
    "Bucket 1 (GCP)": GCSContentsManager,
    "Bucket 2 (S3)": S3ContentsManager,
    "Personal workspace (local)": LargeFileManager,
}
c.HybridContentsManager.manager_kwargs = {
    "Bucket 1 (GCP)": {
        "project": os.environ["GCS_PROJECT"],
        "token": "/etc/secrets/service-account.json",
        "bucket": os.environ["GCS_BUCKET_NAME"],
    },
    "Bucket 2 (S3)": {
        "access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
        "bucket": os.environ["S3_BUCKET_NAME"],
    },
    "Personal workspace (local)": {"root_dir": "/home/jovyan"},
}

c.GCSManager.bucket = os.environ["GCS_BUCKET_NAME"]

c.NotebookApp.tornado_settings = {"autoreload": os.environ.get("DEBUG", False)}
