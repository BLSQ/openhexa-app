import json
import typing

from django import test
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from hexa.plugins.connector_airflow.authentication import DAGRunUser
from hexa.user_management.models import User


class TestCase(test.TestCase):
    def _pre_setup(self):
        _pre_setup = super()._pre_setup()
        self.client.defaults = {
            **self.client.defaults,
            "HTTP_HOST": "app.openhexa.test",
        }

        return _pre_setup

    @staticmethod
    def mock_request(user: typing.Union[AnonymousUser, User, DAGRunUser]):
        request = HttpRequest()
        request.user = user
        request.session = {}
        request.META["HTTP_HOST"] = "app.openhexa.test"

        return request


class GraphQLTestCase(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def run_query(self, query, variables=None):
        return json.loads(
            self.client.post(
                "/graphql/",
                json.dumps(
                    {
                        "operationName": None,
                        "variables": variables if variables is not None else {},
                        "query": query,
                    }
                ),
                content_type="application/json",
            ).content
        )
