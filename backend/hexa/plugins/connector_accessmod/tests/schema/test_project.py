import uuid

from hexa.core.test import GraphQLTestCase
from hexa.countries.models import Country
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    File,
    Fileset,
    FilesetRole,
    FilesetRoleCode,
    Project,
    ProjectPermission,
)
from hexa.user_management.models import (
    Membership,
    MembershipRole,
    PermissionMode,
    Team,
    User,
)


class ProjectTest(GraphQLTestCase):
    TEAM = None
    WATER_FILESET = None
    SAMPLE_PROJECT = None
    OTHER_PROJECT = None
    WATER_ROLE = None
    USER_JIM = None
    USER_JANE = None
    PERMISSION = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_JIM = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimrocks",
        )
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janesthebest",
        )
        cls.TEAM = Team.objects.create(name="A team")
        cls.OTHER_TEAM = Team.objects.create(name="A different team")
        Membership.objects.create(
            user=cls.USER_JIM, team=cls.TEAM, role=MembershipRole.ADMIN
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="FR",
            author=cls.USER_JIM,
            spatial_resolution=100,
            crs=4326,
        )
        cls.PERMISSION = ProjectPermission.objects.create(
            user=cls.USER_JIM, project=cls.SAMPLE_PROJECT, mode=PermissionMode.OWNER
        )
        cls.OTHER_PROJECT = Project.objects.create(
            name="Other project",
            country="BE",
            author=cls.USER_JIM,
            spatial_resolution=100,
            crs=4326,
        )
        ProjectPermission.objects.create(
            user=cls.USER_JIM, project=cls.OTHER_PROJECT, mode=PermissionMode.OWNER
        )
        cls.WATER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.WATER,
        )
        cls.WATER_FILESET = Fileset.objects.create(
            name="A wonderful water",
            role=cls.WATER_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_JIM,
        )
        cls.WATER_FILE = File.objects.create(
            fileset=cls.WATER_FILESET, uri="afile.tiff", mime_type="image/tiff"
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            author=cls.USER_JIM,
            project=cls.SAMPLE_PROJECT,
            name="A random accessibility analysis",
            water=cls.WATER_FILESET,
        )

    def test_accessmod_project_owner(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
              query accessmodProject($id: String!) {
                accessmodProject(id: $id) {
                  id
                  name
                  spatialResolution
                  country {
                    code
                    flag
                  }
                  owner {
                      __typename
                      ...on User {
                          id
                      }
                  }
                  author {
                    email
                  }
                  members {
                    user { id }
                    team { id }
                    project { id }
                    mode
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
                "country": {
                    "code": "FR",
                    "flag": "http://app.openhexa.test/static/flags/fr.gif",
                },
                "author": {"email": "jim@bluesquarehub.com"},
                "owner": {"__typename": "User", "id": str(self.USER_JIM.id)},
                "members": [
                    {
                        "user": {"id": str(self.USER_JIM.id)},
                        "team": None,
                        "project": {"id": str(self.SAMPLE_PROJECT.id)},
                        "mode": PermissionMode.OWNER,
                    }
                ],
            },
        )

    def test_accessmod_project_not_author(self):
        self.client.force_login(self.USER_JANE)

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
        self.client.force_login(self.USER_JIM)

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
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.OTHER_PROJECT.id)},
                    {"id": str(self.SAMPLE_PROJECT.id)},
                ],
            },
            r["data"]["accessmodProjects"],
        )

    def test_accessmod_projects_with_term(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects(term: "samp", page: 1, perPage: 10) {
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
                "totalItems": 1,
                "items": [
                    {"id": str(self.SAMPLE_PROJECT.id)},
                ],
            },
        )

    def test_accessmod_projects_with_countries(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                query accessmodProjects {
                  accessmodProjects(countries: ["BE"], page: 1, perPage: 10) {
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
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {"id": str(self.OTHER_PROJECT.id)},
                ],
            },
            r["data"]["accessmodProjects"],
        )

    def test_accessmod_projects_with_pagination(self):
        self.client.force_login(self.USER_JIM)

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
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.OTHER_PROJECT.id)},
                    {"id": str(self.SAMPLE_PROJECT.id)},
                ],
            },
            r["data"]["accessmodProjects"],
        )

    def test_accessmod_projects_empty(self):
        self.client.force_login(self.USER_JANE)

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

    def test_create_accessmod_project_by_country(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation createAccessmodProject($input: CreateAccessmodProjectInput!) {
                  createAccessmodProject(input: $input) {
                    success
                    project {
                        name
                        spatialResolution
                        crs
                        country {
                            code
                        }
                        extent
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
            {
                "success": True,
                "project": {
                    "name": "My new project",
                    "spatialResolution": 42,
                    "crs": 4326,
                    "country": {"code": "CD"},
                    "extent": [
                        [x, y]
                        for x, y in Country.objects.get(
                            code="CD"
                        ).simplified_extent.tuple[0]
                    ],
                },
                "errors": [],
            },
            r["data"]["createAccessmodProject"],
        )

    def test_create_accessmod_project_by_raster(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation createAccessmodProject($input: CreateAccessmodProjectInput!) {
                  createAccessmodProject(input: $input) {
                    success
                    project {
                        name
                        spatialResolution
                        crs
                        country {
                            code
                        }
                        extent
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
                    "extent": [[1.0, 2.0], [3.0, 4.0]],
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "project": {
                    "name": "My new project",
                    "spatialResolution": 42,
                    "crs": 4326,
                    "country": {"code": "CD"},
                    "extent": [[1.0, 2.0], [3.0, 4.0]],
                },
                "errors": [],
            },
            r["data"]["createAccessmodProject"],
        )

    def test_create_accessmod_project_errors(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation createAccessmodProject($input: CreateAccessmodProjectInput!) {
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
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput!) {
                  updateAccessmodProject(input: $input) {
                    success
                    project {
                        id
                        name
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": "Updated project!",
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
                },
                "errors": [],
            },
        )

    def test_update_accessmod_project_errors(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput!) {
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
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodProject"],
            {
                "success": False,
                "project": None,
                "errors": ["NAME_DUPLICATE"],
            },
        )

        r = self.run_query(
            """
                mutation updateAccessmodProject($input: UpdateAccessmodProjectInput!) {
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
                    "id": str(uuid.uuid4()),
                    "name": "YOLO",
                }
            },
        )

        self.assertEqual(
            {"success": False, "project": None, "errors": ["NOT_FOUND"]},
            r["data"]["updateAccessmodProject"],
        )

    def test_delete_accessmod_project(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation deleteAccessmodProject($input: DeleteAccessmodProjectInput!) {
                  deleteAccessmodProject(input: $input) {
                    success
                    errors
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
            {"success": True, "errors": []},
        )
        self.assertIsNone(Project.objects.filter(id=self.SAMPLE_PROJECT.id).first())

    def test_create_accessmod_project_member(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation createAccessmodProjectMember($input: CreateAccessmodProjectMemberInput!) {
                  createAccessmodProjectMember(input: $input) {
                    success
                    member {
                      project {
                        id
                      }
                      user {
                        id
                      }
                      team {
                        id
                      }
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "teamId": str(self.TEAM.id),
                    "mode": PermissionMode.OWNER,
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "member": {
                    "project": {"id": str(self.SAMPLE_PROJECT.id)},
                    "user": None,
                    "team": {"id": str(self.TEAM.id)},
                },
                "errors": [],
            },
            r["data"]["createAccessmodProjectMember"],
        )
        # We should end with a single "OWNER" permission
        permission = ProjectPermission.objects.get(project=self.SAMPLE_PROJECT)
        self.assertEqual(self.SAMPLE_PROJECT, permission.project)
        self.assertEqual(self.TEAM, permission.team)
        self.assertEqual(PermissionMode.OWNER, permission.mode)
        self.assertIsNone(permission.user)

    def test_create_accessmod_project_member_errors(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation createAccessmodProjectMember($input: CreateAccessmodProjectMemberInput!) {
                  createAccessmodProjectMember(input: $input) {
                    success
                    member {
                    id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "teamId": str(self.OTHER_TEAM.id),
                    "mode": PermissionMode.OWNER,
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "member": None,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["createAccessmodProjectMember"],
        )

        r = self.run_query(
            """
                mutation createAccessmodProjectMember($input: CreateAccessmodProjectMemberInput!) {
                  createAccessmodProjectMember(input: $input) {
                    success
                    member {
                    id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "teamId": str(self.TEAM.id),
                    "mode": PermissionMode.EDITOR,
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "member": None,
                "errors": ["NOT_IMPLEMENTED"],
            },
            r["data"]["createAccessmodProjectMember"],
        )

    def test_update_accessmod_project_member(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation updateAccessmodProjectMember($input: UpdateAccessmodProjectMemberInput!) {
                  updateAccessmodProjectMember(input: $input) {
                    success
                    member {
                        id
                    }
                    errors
                  }
                }
            """,
            {"input": {"id": str(self.PERMISSION.id), "mode": PermissionMode.EDITOR}},
        )

        self.assertEqual(
            r["data"]["updateAccessmodProjectMember"],
            {
                "success": False,
                "member": None,
                "errors": ["NOT_IMPLEMENTED"],
            },
        )

    def test_delete_accessmod_project_member(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
                mutation deleteAccessmodProjectMember($input: DeleteAccessmodProjectMemberInput!) {
                  deleteAccessmodProjectMember(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.PERMISSION.id),
                }
            },
        )

        self.assertEqual(
            r["data"]["deleteAccessmodProjectMember"],
            {
                "success": False,
                "errors": ["NOT_IMPLEMENTED"],
            },
        )
