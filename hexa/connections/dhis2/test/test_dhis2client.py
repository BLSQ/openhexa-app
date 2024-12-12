import responses
from django import test

from hexa.connections.dhis2.DHIS2Client import DHIS2Client


class TestDhis2Client(test.TestCase):
    @classmethod
    def setup_class(cls):
        PROTOCOL = "https"
        HOST_NAME = "127.0.0.1"
        API_VERSION = "2.37.0"
        cls.client = DHIS2Client(
            f"{PROTOCOL}://{HOST_NAME}/{API_VERSION}", "admin", "district"
        )

    @responses.activate
    def test_successful_authentication(self):
        CASES = [("2.36"), ("2.37"), ("2.38"), ("2.39"), ("2.40"), ("2.41")]
        for version in CASES:
            with self.subTest(version=version):
                responses.dir("tests/dhis2/responses/2.36/api_authenticate.yaml")
                session = self.client.authenticate()
                assert session.status_code == 200

    @responses.activate
    def test_failure_authentication(self):
        responses.dir("tests/dhis2/responses/2.36/api_authenticate_failure.yaml")
        with self.assertRaises(Exception):
            self.client.authenticate()
