from unittest.mock import patch

from django.test import TestCase
from graphql import GraphQLError

from hexa.user_management.errors import AuthenticationError

from .sentry import setup_sentry


class SentryBeforeSendTest(TestCase):
    def setUp(self):
        with patch("sentry_sdk.init") as mock_init:
            setup_sentry("https://fake@sentry.io/123")
            self.before_send = mock_init.call_args[1]["before_send"]

    def _make_hint(self, exc):
        return {"exc_info": (type(exc), exc, None)}

    def test_filters_authentication_error(self):
        exc = AuthenticationError()
        event = {"tags": {}}
        self.assertIsNone(self.before_send(event, self._make_hint(exc)))

    def test_filters_graphql_wrapped_authentication_error(self):
        auth_error = AuthenticationError()
        graphql_error = GraphQLError("Resolver requires an authenticated user")
        graphql_error.__cause__ = auth_error
        event = {"tags": {}}
        self.assertIsNone(self.before_send(event, self._make_hint(graphql_error)))

    def test_passes_through_other_errors(self):
        exc = ValueError("something else")
        event = {"tags": {}}
        self.assertEqual(self.before_send(event, self._make_hint(exc)), event)

    def test_filters_connection_test_errors(self):
        exc = Exception("connection failed")
        event = {"tags": {"connection_test": True}}
        self.assertIsNone(self.before_send(event, self._make_hint(exc)))

    def test_circular_exception_chain_does_not_loop(self):
        exc_a = ValueError("a")
        exc_b = ValueError("b")
        exc_a.__cause__ = exc_b
        exc_b.__cause__ = exc_a
        event = {"tags": {}}
        self.assertEqual(self.before_send(event, self._make_hint(exc_a)), event)
