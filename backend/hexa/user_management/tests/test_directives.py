from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from graphql import GraphQLField, GraphQLString

from hexa.core.test import TestCase
from hexa.user_management.errors import AuthenticationError
from hexa.user_management.schema.types import LoginRequiredDirective
from hexa.webapps.models import PublicWebappUser, Webapp


class LoginRequiredDirectiveTest(TestCase):
    def _resolve(self, principal, **directive_args):
        field = GraphQLField(GraphQLString, resolve=lambda *_, **__: "ok")
        directive = LoginRequiredDirective(
            "loginRequired", directive_args, field, None, None
        )
        directive.visit_field_definition(field, None)
        info = SimpleNamespace(
            context={"request": SimpleNamespace(user=principal, session={})}
        )
        return field.resolve(None, info)

    def test_anonymous_is_refused(self):
        with self.assertRaises(AuthenticationError):
            self._resolve(AnonymousUser(), allowPublicWebapp=True)

    def test_public_webapp_visitor_is_refused_by_default(self):
        with self.assertRaises(AuthenticationError):
            self._resolve(PublicWebappUser(Webapp(is_public=True)))

    def test_public_webapp_visitor_is_allowed_when_opted_in(self):
        self.assertEqual(
            "ok",
            self._resolve(
                PublicWebappUser(Webapp(is_public=True)), allowPublicWebapp=True
            ),
        )
