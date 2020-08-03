import os

from habari import GCSManager

c.NotebookApp.contents_manager_class = GCSManager
c.GCSManager.bucket = os.environ["GCS_BUCKET_NAME"]

c.NotebookApp.tornado_settings = {"autoreload": os.environ.get("DEBUG", False)}
