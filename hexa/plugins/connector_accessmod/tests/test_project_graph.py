from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import Project
from hexa.user_management.models import User


class AccessmodProjectGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimrocks",
        )
        cls.USER_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janesthebest",
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            owner=cls.USER_1,
            spatial_resolution=100,
            crs=4326,
        )
        cls.OTHER_PROJECT = Project.objects.create(
            name="Other project",
            country="BE",
            owner=cls.USER_1,
            spatial_resolution=100,
            crs=4326,
        )

    def test_accessmod_project_owner(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodProject($id: String!) {
                  accessmodProject(id: $id) {
                    id
                    name
                    spatialResolution
                    country {
                        code
                    }
                    owner {
                        email
                    }
                  }
                }
            """,
            {"id": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessmodProject"],
            {
                "id": str(self.SAMPLE_PROJECT.id),
                "name": "Sample project",
                "spatialResolution": 100,
                "country": {"code": "BE"},
                "owner": {"email": "jim@bluesquarehub.com"},
            },
        )

    def test_accessmod_project_not_owner(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodProject($id: String!) {
                  accessmodProject(id: $id) {
                    id
                  }
                }
            """,
            {"id": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessmodProject"],
            None,
        )

    def test_accessmod_projects(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodProjects"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.OTHER_PROJECT.id)},
                    {"id": str(self.SAMPLE_PROJECT.id)},
                ],
            },
        )

    def test_accessmod_projects_with_pagination(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects(page: 1, perPage: 10) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodProjects"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.OTHER_PROJECT.id)},
                    {"id": str(self.SAMPLE_PROJECT.id)},
                ],
            },
        )

    def test_accessmod_projects_empty(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodProjects"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 0,
                "items": [],
            },
        )

    def test_create_accessmod_project(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation createAccessmodProject($input: CreateAccessmodProjectInput) {
                  createAccessmodProject(input: $input) {
                    success
                    project {
                        name
                        spatialResolution
                        crs
                        country {
                            code
                        }
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "name": "My new project",
                    "spatialResolution": 42,
                    "crs": 4326,
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["createAccessmodProject"],
            {
                "success": True,
                "project": {
                    "name": "My new project",
                    "spatialResolution": 42,
                    "crs": 4326,
                    "country": {"code": "CD"},
                },
                "errors": [],
            },
        )

    def test_create_accessmod_project_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation createAccessmodProject($input: CreateAccessmodProjectInput) {
                  createAccessmodProject(input: $input) {
                    success
                    project {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "name": self.SAMPLE_PROJECT.name,
                    "spatialResolution": 42,
                    "crs": 4326,
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["createAccessmodProject"],
            {"success": False, "project": None, "errors": ["NAME_DUPLICATE"]},
        )

    def test_update_accessmod_project(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput) {
                  updateAccessmodProject(input: $input) {
                    success
                    project {
                        id
                        name
                        country {
                            code
                        }
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": "Updated project!",
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodProject"],
            {
                "success": True,
                "project": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": "Updated project!",
                    "country": {"code": "CD"},
                },
                "errors": [],
            },
        )

    def test_update_accessmod_project_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput) {
                  updateAccessmodProject(input: $input) {
                    success
                    project {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": self.OTHER_PROJECT.name,
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodProject"],
            {
                "success": False,
                "project": {"id": str(self.SAMPLE_PROJECT.id)},
                "errors": ["NAME_DUPLICATE"],
            },
        )

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput) {
                  updateAccessmodProject(input: $input) {
                    success
                    project {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": "YOLO",
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodProject"],
            {"success": True, "project": None, "errors": ["NOT_FOUND"]},
        )

    def test_delete_accessmod_project(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation deleteAccessmodProject($input: DeleteAccessmodProjectInput) {
                  deleteAccessmodProject(input: $input) {
                    success
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                }
            },
        )

        self.assertEqual(
            r["data"]["deleteAccessmodProject"],
            {
                "success": True,
            },
        )
        self.assertIsNone(Project.objects.filter(id=self.SAMPLE_PROJECT.id).first())
