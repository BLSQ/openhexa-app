from __future__ import annotations

from typing import TYPE_CHECKING

from google.cloud._helpers import _bytes_to_unicode
from google.cloud.exceptions import NotFound

if TYPE_CHECKING:
    from .bucket import MockBucket


class MockBlob:
    def __init__(self, name, bucket: MockBucket, size=None, content_type=None):
        self.name = _bytes_to_unicode(name)
        self._content = None
        self._content_type = content_type
        self.bucket = bucket

    @property
    def size(self):
        if self._content is not None:
            return len(self._content)
        return None

    @property
    def content_type(self):
        return self._content_type

    @property
    def updated(self):
        return None

    def upload_from_string(self, content, content_type=None):
        if isinstance(content, str):
            content = content.encode()
        self._content = content
        if content_type:
            self._content_type = content_type
        self.bucket._blobs[self.name] = self

    def upload_from_file(self, file):
        self._content = file.read()
        self.bucket._blobs[self.name] = self

    def upload_from_filename(self, filename):
        with open(filename, "rb") as f:
            self.upload_from_file(f)

    def download_as_bytes(self):
        if self._content is None:
            raise NotFound(f"Blob {self.name} not found")
        return self._content

    def generate_signed_url(self, *args, **kwargs):
        return f"http://signed-url/{self.name}"

    def __repr__(self):
        return f"<MockBlob: {self.name}>"
