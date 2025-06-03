from unittest.mock import patch

import responses
from openhexa.toolbox.iaso import IASO

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.fixtures.iaso.iaso_fixtures import (
    iaso_mocked_auth_token,
    iaso_mocked_forms,
    iaso_mocked_orgunits,
    iaso_mocked_projects,
)
from hexa.workspaces.utils import (
    IASOMetadataQueryType,
    query_iaso_metadata,
    toolbox_client_from_connection,
)


class TestIASOClientMethods(TestCase):
    USER_SERENA = None
    USER_ADMIN = None

    @classmethod
    def setUp(cls):
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )
        cls.USER_JIM = User.objects.create_user("jim@bluesquarehub.com", "jim&password")

        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "admin", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN, name="Workspace's title"
            )

        WorkspaceMembership.objects.create(
            user=cls.USER_SERENA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_JIM,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.connection = Connection.objects.create_if_has_perm(
            cls.USER_JIM,
            cls.WORKSPACE,
            name="IASO connection 1",
            slug="iaso-connection-1",
            connection_type=ConnectionType.IASO,
        )
        cls.connection.set_fields(
            cls.USER_JIM,
            [
                {
                    "code": "url",
                    "value": "https://iaso-staging.bluesquare.org",
                    "secret": False,
                },
                {"code": "username", "value": "admin", "secret": False},
                {"code": "password", "value": "district", "secret": True},
            ],
        )
        cls.connection.save()

    @responses.activate
    def test_iaso_connection_from_slug(self):
        responses.add(
            responses.POST,
            "https://iaso-staging.bluesquare.org/api/token/",
            json=iaso_mocked_auth_token,
            status=200,
        )
        self.assertTrue(self.connection.connection_type == ConnectionType.IASO)
        iaso = toolbox_client_from_connection(self.connection)
        self.assertEqual(type(iaso), IASO)

    @responses.activate
    def test_iaso_connection_get_org_units(self):
        responses.add(
            responses.POST,
            "https://iaso-staging.bluesquare.org/api/token/",
            json=iaso_mocked_auth_token,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://iaso-staging.bluesquare.org/api/orgunits/tree/search/?page=1&limit=10&validation_status=VALID",
            json=iaso_mocked_orgunits,
            status=200,
        )
        iaso = toolbox_client_from_connection(self.connection)
        self.assertIsNotNone(iaso)
        org_units = iaso.get_org_units(optimized=True)
        self.assertIsNotNone(org_units)

    @responses.activate
    def test_iaso_connection_get_org_units_with_search(self):
        responses.add(
            responses.POST,
            "https://iaso-staging.bluesquare.org/api/token/",
            json=iaso_mocked_auth_token,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://iaso-staging.bluesquare.org/api/orgunits/tree/search/?search=test&page=1&limit=10&validation_status=VALID&smallSearch=true",
            json=iaso_mocked_orgunits,
            status=200,
        )
        iaso = toolbox_client_from_connection(self.connection)
        self.assertIsNotNone(iaso)
        org_units = iaso.get_org_units(optimized=True, search="test")
        self.assertEqual(len(org_units), 1)

    @responses.activate
    def test_get_forms_with_search(self):
        responses.add(
            responses.POST,
            "https://iaso-staging.bluesquare.org/api/token/",
            json=iaso_mocked_auth_token,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://iaso-staging.bluesquare.org/api/forms/?org_units=1&projects=1&search=test&page=1&limit=10",
            json=iaso_mocked_forms,
            status=200,
        )

        params = {}
        filters = [
            {"type": "org_units", "value": [1]},
            {"type": "projects", "value": [1]},
        ]
        for filter_ in filters:
            params[filter_["type"]] = filter_["value"]
        params["search"] = "test"

        iaso = toolbox_client_from_connection(self.connection)
        self.assertIsNotNone(iaso)
        forms = query_iaso_metadata(iaso, IASOMetadataQueryType.IASO_FORMS, **params)
        self.assertEqual(len(forms.items), 1)

    @responses.activate
    def test_get_projects_with_search(self):
        responses.add(
            responses.POST,
            "https://iaso-staging.bluesquare.org/api/token/",
            json=iaso_mocked_auth_token,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://iaso-staging.bluesquare.org/api/projects/?search=test&page=1&limit=10",
            json=iaso_mocked_projects,
            status=200,
        )

        iaso = toolbox_client_from_connection(self.connection)
        self.assertIsNotNone(iaso)
        projects = query_iaso_metadata(
            iaso, IASOMetadataQueryType.IASO_PROJECTS, search="test"
        )
        self.assertEqual(len(projects.items), 1)
