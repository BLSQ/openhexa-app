from unittest.mock import Mock

from google.cloud._helpers import _bytes_to_unicode


class MockBlob:
    def __init__(
        self,
        name,
        bucket,
        size=None,
        content_type=None,
    ):
        self.name = _bytes_to_unicode(name)
        self.size = size
        self._content_type = content_type
        self.bucket = bucket

        self.upload_from_string = Mock()

    @property
    def content_type(self):
        return self._content_type

    @property
    def updated(self):
        return None

    def generate_signed_url(self, *args, **kwargs):
        return f"http://signed-url/{self.name}"

    def upload_from_filename(self, file_name):
        self.bucket._blobs.append(self)

    def __repr__(self) -> str:
        return f"<MockBlob: {self.name}>"
