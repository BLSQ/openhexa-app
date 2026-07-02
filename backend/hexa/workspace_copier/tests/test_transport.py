from unittest.mock import MagicMock

import httpx
from django.test import SimpleTestCase
from openhexa.graphql.graphql_client.exceptions import (
    GraphQLClientGraphQLMultiError,
)

from hexa.workspace_copier.transport import GraphQLError, gql


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
