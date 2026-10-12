from unittest.mock import MagicMock

import httpx
from django.test import SimpleTestCase, override_settings
from openhexa.graphql.graphql_client.exceptions import (
    GraphQLClientGraphQLMultiError,
)

from hexa.workspace_copier.transport import GraphQLError, build_http_client, gql


class GqlErrorTranslationTest(SimpleTestCase):
    def _client(self, *, is_success=True, status_code=200, get_data_side_effect=None):
        client = MagicMock()
        resp = MagicMock(spec=httpx.Response)
        resp.is_success = is_success
        resp.status_code = status_code
        resp.text = "body"
        client.execute.return_value = resp
        if get_data_side_effect is not None:
            client.get_data.side_effect = get_data_side_effect
        else:
            client.get_data.return_value = {"ok": True}
        return client

    def test_returns_data_on_success(self):
        client = self._client()
        self.assertEqual(
            gql(client, "query Q { ok }", operation_name="Q"), {"ok": True}
        )

    def test_http_error_raises_graphql_error(self):
        client = self._client(is_success=False, status_code=500)
        with self.assertRaises(GraphQLError):
            gql(client, "query Q { ok }", operation_name="Q")

    def test_graphql_level_error_is_translated(self):
        # A 200 with a top-level `errors` array makes the SDK's get_data raise
        # GraphQLClientGraphQLMultiError; gql must surface it as GraphQLError so
        # per-item handlers catch it instead of aborting the whole copy.
        multi_error = GraphQLClientGraphQLMultiError.from_errors_dicts(
            [{"message": "permission denied"}]
        )
        client = self._client(get_data_side_effect=multi_error)
        with self.assertRaises(GraphQLError) as ctx:
            gql(client, "query Q { ok }", operation_name="Q")
        self.assertIn("permission denied", str(ctx.exception))


class InternalUrlRoutingTest(SimpleTestCase):
    def _sent_url(self, url: str) -> str:
        sent = []

        def handler(request):
            sent.append(str(request.url))
            return httpx.Response(200)

        with build_http_client(transport=httpx.MockTransport(handler)) as client:
            client.get(url)
        return sent[0]

    @override_settings(
        BASE_URL="http://localhost:8000", INTERNAL_BASE_URL="http://app:8000"
    )
    def test_public_url_is_routed_to_internal_url(self):
        self.assertEqual(
            self._sent_url("http://localhost:8000/files/dl/abc/?attachment=true"),
            "http://app:8000/files/dl/abc/?attachment=true",
        )

    @override_settings(
        BASE_URL="http://localhost:8000", INTERNAL_BASE_URL="http://app:8000"
    )
    def test_other_hosts_are_untouched(self):
        for url in (
            "https://api.openhexa.org/graphql/",
            "http://localhost:8001/graphql/",
        ):
            self.assertEqual(self._sent_url(url), url)

    @override_settings(
        BASE_URL="https://api.openhexa.org",
        INTERNAL_BASE_URL="https://api.openhexa.org",
    )
    def test_no_op_when_internal_url_is_the_public_one(self):
        url = "https://api.openhexa.org/graphql/"
        self.assertEqual(self._sent_url(url), url)
