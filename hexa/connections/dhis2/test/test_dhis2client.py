from pathlib import Path

import responses
from django import test

from hexa.connections.dhis2.DHIS2Client import DHIS2Client


class TestDhis2Client(test.TestCase):
    @responses.activate
    def test_successful_authentication(self):
        VERSIONS = ["2.36", "2.37", "2.38", "2.39", "2.40", "2.41"]
        response_dir = Path("hexa", "connections", "dhis2", "test", "fixtures")

        for version in VERSIONS:
            with self.subTest(version=version):
                client = DHIS2Client("https://127.0.0.1:8080/", "admin", "district")
                path_to_version = Path(response_dir, version, "api_authenticate.yaml")
                responses._add_from_file(path_to_version)
                session = client.authenticate()
                assert session.status_code == 200
