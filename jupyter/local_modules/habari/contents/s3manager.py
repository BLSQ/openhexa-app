from s3contents import S3ContentsManager as BaseS3ContentsManager

from .largefiles import save as save_override


class S3ContentsManager(BaseS3ContentsManager):
    """Placeholder for overriding S3ContentsManager"""

    def save(self, model, path):
        return save_override(BaseS3ContentsManager, self, model, path)
