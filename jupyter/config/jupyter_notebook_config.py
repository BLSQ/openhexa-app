import os

from notebook.services.contents.largefilemanager import LargeFileManager
from habari.contents import MultiContentsManager, S3ContentsManager


c = get_config()

c.NotebookApp.contents_manager_class = MultiContentsManager
c.MultiContentsManager.manager_classes = {
    "": LargeFileManager,
    f"s3:{os.environ['S3_BUCKET_NAME_PUBLIC']}": S3ContentsManager,
    f"s3:{os.environ['S3_BUCKET_NAME_LAKE']}": S3ContentsManager,
    f"s3:{os.environ['S3_BUCKET_NAME_NOTEBOOKS']}": S3ContentsManager,
}
c.MultiContentsManager.manager_kwargs = {
    "": {},
    f"s3:{os.environ['S3_BUCKET_NAME_PUBLIC']}": {
        "access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
        "bucket": os.environ["S3_BUCKET_NAME_PUBLIC"],
    },
    f"s3:{os.environ['S3_BUCKET_NAME_LAKE']}": {
        "access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
        "bucket": os.environ["S3_BUCKET_NAME_LAKE"],
    },
    f"s3:{os.environ['S3_BUCKET_NAME_NOTEBOOKS']}": {
        "access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
        "bucket": os.environ["S3_BUCKET_NAME_NOTEBOOKS"],
    },
}
# Fix for https://github.com/BLSQ/habari/issues/31
c.GenericFileCheckpoints.root_dir = "./.checkpoints"

c.NotebookApp.tornado_settings = {"autoreload": os.environ.get("DEBUG", False)}
