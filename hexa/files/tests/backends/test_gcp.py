from hexa.core.test import TestCase
from hexa.files.backends.gcp import GCPStorage


class GCPStorageTest(TestCase):
    storage = None

    def setUp(self):
        super().setUp()
        self.storage = GCPStorage(
            service_account_key="service_account",
            project_id="test",
            bucket_name="test",
        )
