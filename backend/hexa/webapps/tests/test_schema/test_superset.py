from hexa.core.test import GraphQLTestCase
from hexa.superset.models import SupersetDashboard, SupersetInstance
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.webapps.models import SupersetWebapp, Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

CREATE_WEBAPP_MUTATION = """
    mutation createWebapp($input: CreateWebappInput!) {
        createWebapp(input: $input) {
            success
            errors
            webapp {
                id
                name
                type
                source {
                    ... on SupersetSource {
                        instance { id name }
                        dashboardId
                    }
                    ... on IframeSource {
                        url
                    }
                }
            }
        }
    }
"""

UPDATE_WEBAPP_MUTATION = """
    mutation updateWebapp($input: UpdateWebappInput!) {
        updateWebapp(input: $input) {
            success
            errors
            webapp {
                id
                name
                source {
                    ... on SupersetSource {
                        instance { id name }
                        dashboardId
                    }
                }
            }
        }
    }
"""

DELETE_WEBAPP_MUTATION = """
    mutation deleteWebapp($input: DeleteWebappInput!) {
        deleteWebapp(input: $input) {
            success
            errors
        }
    }
"""

SUPERSET_INSTANCES_QUERY = """
    query supersetInstances($workspaceSlug: String!) {
        supersetInstances(workspaceSlug: $workspaceSlug) {
            id
            name
            url
        }
    }
"""

WEBAPP_QUERY = """
    query webapp($workspaceSlug: String!, $slug: String!) {
        webapp(workspaceSlug: $workspaceSlug, slug: $slug) {
            id
            name
            type
            source {
                ... on SupersetSource {
                    instance { id name }
                    dashboardId
                }
            }
        }
    }
"""


class SupersetWebappGraphQLTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORG = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-superset-gql",
        )
        cls.SUPERSET_INSTANCE = SupersetInstance.objects.create(
            name="Main Superset",
            url="https://superset.example.com",
            api_username="test",
            api_password="password",
            organization=cls.ORG,
        )
        cls.SUPERSET_INSTANCE_2 = SupersetInstance.objects.create(
            name="Other Superset",
            url="https://other-superset.example.com",
            api_username="test2",
            api_password="password2",
            organization=cls.ORG,
        )
        cls.USER_ADMIN = User.objects.create_user(
            "admin@superset-test.com",
            "admin",
        )
        cls.USER_VIEWER = User.objects.create_user(
            "viewer@superset-test.com",
            "viewer",
        )
        cls.USER_OUTSIDE = User.objects.create_user(
            "outside@superset-test.com",
            "outside",
        )
        cls.WORKSPACE = Workspace.objects.create(
            name="Superset Workspace",
            organization=cls.ORG,
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_ADMIN,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_VIEWER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_superset_instances_query(self):
        self.client.force_login(self.USER_ADMIN)
        response = self.run_query(
            SUPERSET_INSTANCES_QUERY,
            {"workspaceSlug": self.WORKSPACE.slug},
        )
        instances = response["data"]["supersetInstances"]
        self.assertEqual(len(instances), 2)
        ids = {i["id"] for i in instances}
        self.assertIn(str(self.SUPERSET_INSTANCE.id), ids)
        self.assertIn(str(self.SUPERSET_INSTANCE_2.id), ids)

    def test_superset_instances_query_no_org(self):
        workspace_no_org = Workspace.objects.create(
            name="No Org WS Instances",
            slug="no-org-ws-instances",
            db_name="noorgwsinst",
        )
        WorkspaceMembership.objects.create(
            user=self.USER_ADMIN,
            workspace=workspace_no_org,
            role=WorkspaceMembershipRole.ADMIN,
        )
        self.client.force_login(self.USER_ADMIN)
        response = self.run_query(
            SUPERSET_INSTANCES_QUERY,
            {"workspaceSlug": workspace_no_org.slug},
        )
        self.assertEqual(response["data"]["supersetInstances"], [])

    def test_superset_instances_query_non_member(self):
        self.client.force_login(self.USER_OUTSIDE)
        response = self.run_query(
            SUPERSET_INSTANCES_QUERY,
            {"workspaceSlug": self.WORKSPACE.slug},
        )
        self.assertEqual(response["data"]["supersetInstances"], [])

    def test_create_superset_webapp(self):
        self.client.force_login(self.USER_ADMIN)
        response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "My Superset Dashboard",
                    "description": "A test dashboard",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-abc",
                        }
                    },
                }
            },
        )
        result = response["data"]["createWebapp"]
        self.assertTrue(result["success"])
        self.assertEqual(result["webapp"]["name"], "My Superset Dashboard")
        self.assertEqual(result["webapp"]["type"], "SUPERSET")
        self.assertEqual(
            result["webapp"]["source"]["instance"]["id"],
            str(self.SUPERSET_INSTANCE.id),
        )
        self.assertEqual(result["webapp"]["source"]["dashboardId"], "ext-abc")

        webapp = SupersetWebapp.objects.get(id=result["webapp"]["id"])
        self.assertEqual(webapp.superset_dashboard.external_id, "ext-abc")

    def test_create_superset_webapp_permission_denied(self):
        self.client.force_login(self.USER_VIEWER)
        response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "Denied Dashboard",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-denied",
                        }
                    },
                }
            },
        )
        result = response["data"]["createWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("PERMISSION_DENIED", result["errors"])

    def test_create_superset_webapp_invalid_instance(self):
        self.client.force_login(self.USER_ADMIN)
        response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "Bad Instance",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": "00000000-0000-0000-0000-000000000000",
                            "dashboardId": "ext-nope",
                        }
                    },
                }
            },
        )
        result = response["data"]["createWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("SUPERSET_INSTANCE_NOT_FOUND", result["errors"])

    def test_create_superset_webapp_no_org(self):
        workspace_no_org = Workspace.objects.create(
            name="No Org WS Create",
            slug="no-org-ws-create",
            db_name="noorgwscreate",
        )
        WorkspaceMembership.objects.create(
            user=self.USER_ADMIN,
            workspace=workspace_no_org,
            role=WorkspaceMembershipRole.ADMIN,
        )
        self.client.force_login(self.USER_ADMIN)
        response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "No Org Dashboard",
                    "workspaceSlug": workspace_no_org.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-no-org",
                        }
                    },
                }
            },
        )
        result = response["data"]["createWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("SUPERSET_NOT_CONFIGURED", result["errors"])

    def test_create_two_webapps_same_external_dashboard(self):
        self.client.force_login(self.USER_ADMIN)
        response1 = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "Dashboard Copy 1",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-shared",
                        }
                    },
                }
            },
        )
        response2 = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "Dashboard Copy 2",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-shared",
                        }
                    },
                }
            },
        )
        self.assertTrue(response1["data"]["createWebapp"]["success"])
        self.assertTrue(response2["data"]["createWebapp"]["success"])

        webapp1 = SupersetWebapp.objects.get(
            id=response1["data"]["createWebapp"]["webapp"]["id"]
        )
        webapp2 = SupersetWebapp.objects.get(
            id=response2["data"]["createWebapp"]["webapp"]["id"]
        )
        self.assertNotEqual(
            webapp1.superset_dashboard_id, webapp2.superset_dashboard_id
        )

    def test_update_superset_webapp_dashboard(self):
        self.client.force_login(self.USER_ADMIN)
        create_response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "To Update",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-original",
                        }
                    },
                }
            },
        )
        webapp_id = create_response["data"]["createWebapp"]["webapp"]["id"]

        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": webapp_id,
                    "name": "Updated Name",
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE_2.id),
                            "dashboardId": "ext-updated",
                        }
                    },
                }
            },
        )
        result = response["data"]["updateWebapp"]
        self.assertTrue(result["success"])
        self.assertEqual(result["webapp"]["name"], "Updated Name")
        self.assertEqual(
            result["webapp"]["source"]["instance"]["id"],
            str(self.SUPERSET_INSTANCE_2.id),
        )
        self.assertEqual(result["webapp"]["source"]["dashboardId"], "ext-updated")

    def test_update_superset_webapp_name_only(self):
        self.client.force_login(self.USER_ADMIN)
        create_response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "Original Name",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-keep",
                        }
                    },
                }
            },
        )
        webapp_id = create_response["data"]["createWebapp"]["webapp"]["id"]

        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {"input": {"id": webapp_id, "name": "Renamed"}},
        )
        result = response["data"]["updateWebapp"]
        self.assertTrue(result["success"])
        self.assertEqual(result["webapp"]["name"], "Renamed")
        self.assertEqual(result["webapp"]["source"]["dashboardId"], "ext-keep")

    def test_update_type_mismatch(self):
        self.client.force_login(self.USER_ADMIN)
        iframe_webapp = Webapp.objects.create(
            name="Iframe App",
            slug="iframe-app",
            url="https://example.com",
            workspace=self.WORKSPACE,
            created_by=self.USER_ADMIN,
            type=Webapp.WebappType.IFRAME,
        )

        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": str(iframe_webapp.id),
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-wrong",
                        }
                    },
                }
            },
        )
        result = response["data"]["updateWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("TYPE_MISMATCH", result["errors"])

    def test_delete_superset_webapp(self):
        self.client.force_login(self.USER_ADMIN)
        create_response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "To Delete",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-delete",
                        }
                    },
                }
            },
        )
        webapp_id = create_response["data"]["createWebapp"]["webapp"]["id"]
        dashboard_id = SupersetWebapp.objects.get(id=webapp_id).superset_dashboard_id

        response = self.run_query(
            DELETE_WEBAPP_MUTATION,
            {"input": {"id": webapp_id}},
        )
        self.assertTrue(response["data"]["deleteWebapp"]["success"])
        self.assertFalse(Webapp.objects.filter(id=webapp_id).exists())
        self.assertFalse(SupersetDashboard.objects.filter(id=dashboard_id).exists())

    def test_delete_superset_webapp_permission_denied(self):
        self.client.force_login(self.USER_ADMIN)
        create_response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "Protected",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-protected",
                        }
                    },
                }
            },
        )
        webapp_id = create_response["data"]["createWebapp"]["webapp"]["id"]

        self.client.force_login(self.USER_VIEWER)
        response = self.run_query(
            DELETE_WEBAPP_MUTATION,
            {"input": {"id": webapp_id}},
        )
        self.assertFalse(response["data"]["deleteWebapp"]["success"])
        self.assertIn("PERMISSION_DENIED", response["data"]["deleteWebapp"]["errors"])
        self.assertTrue(SupersetWebapp.objects.filter(id=webapp_id).exists())

    def test_webapp_query_superset_source(self):
        self.client.force_login(self.USER_ADMIN)
        create_response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "Query Test",
                    "workspaceSlug": self.WORKSPACE.slug,
                    "source": {
                        "superset": {
                            "instanceId": str(self.SUPERSET_INSTANCE.id),
                            "dashboardId": "ext-query",
                        }
                    },
                }
            },
        )
        webapp_id = create_response["data"]["createWebapp"]["webapp"]["id"]
        webapp = Webapp.objects.get(id=webapp_id)

        response = self.run_query(
            WEBAPP_QUERY,
            {
                "workspaceSlug": self.WORKSPACE.slug,
                "slug": webapp.slug,
            },
        )
        result = response["data"]["webapp"]
        self.assertEqual(result["name"], "Query Test")
        self.assertEqual(result["type"], "SUPERSET")
        self.assertEqual(
            result["source"]["instance"]["id"], str(self.SUPERSET_INSTANCE.id)
        )
        self.assertEqual(result["source"]["dashboardId"], "ext-query")

    def test_superset_instances_org_admin_access(self):
        org_admin = User.objects.create_user("orgadmin@superset-test.com", "password")
        OrganizationMembership.objects.create(
            organization=self.ORG,
            user=org_admin,
            role=OrganizationMembershipRole.ADMIN,
        )
        self.client.force_login(org_admin)
        response = self.run_query(
            SUPERSET_INSTANCES_QUERY,
            {"workspaceSlug": self.WORKSPACE.slug},
        )
        instances = response["data"]["supersetInstances"]
        self.assertEqual(len(instances), 2)
