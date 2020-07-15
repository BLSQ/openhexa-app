import os
from hybridcontents import HybridContentsManager
from s3contents import S3ContentsManager
from notebook.services.contents.largefilemanager import LargeFileManager

c = get_config()

# Storage - we use a mix of "local filesystem" and S3
# (see https://github.com/danielfrg/s3contents and https://github.com/viaduct-ai/hybridcontents)
c.NotebookApp.contents_manager_class = HybridContentsManager
c.HybridContentsManager.manager_classes = {
    '': LargeFileManager,
    'data': S3ContentsManager,
    'shared': S3ContentsManager,
}
S3_BASE_KWARGS = {
    "access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
    "secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
    "bucket": os.environ["S3_BUCKET_NAME"],
}
c.HybridContentsManager.manager_kwargs = {
    '': {},
    'data': {
        **S3_BASE_KWARGS,
        "prefix": "data"
    },
    'shared': {
        **S3_BASE_KWARGS,
        "prefix": "shared"
    }
}
