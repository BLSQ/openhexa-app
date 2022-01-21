from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import FilesetFormat, FilesetRole, Project
from hexa.user_management.models import User


class AccessmodFileGraphTest(GraphQLTestCase):
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
        )
        cls.OTHER_PROJECT = Project.objects.create(
            name="Other project", country="BE", owner=cls.USER_1, spatial_resolution=100
        )
        cls.ZONE_ROLE = FilesetRole.objects.create(
            name="Zone", format=FilesetFormat.RASTER
        )

    def test_full_upload_workflow(self):
        self.client.force_login(self.USER_1)

        # Step 1: create fileset
        r1 = self.run_query(
            """
                mutation createAccessmodFileset($input: CreateAccessmodFilesetInput) {
                  createAccessmodFileset(input: $input) {
                    success
                    fileset {
                        name
                        role {
                            id
                        }
                    }
                  }
                }
            """,
            {
                "input": {
                    "name": "A nice zone file",
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "roleId": str(self.ZONE_ROLE.id),
                }
            },
        )
        self.assertEqual(
            r1["data"]["createAccessmodFileset"],
            {
                "success": True,
                "fileset": {
                    "name": "A nice zone file",
                    "role": {"id": str(self.ZONE_ROLE.id)},
                },
            },
        )

        # r = self.run_query(
        #     """
        #         mutation prepareAccessModFileUpload($input: PrepareAccessModFileUploadInput) {
        #           prepareAccessModFileUpload(input: $input) {
        #             success
        #             uploadUrl
        #             fileUri
        #           }
        #         }
        #     """,
        #     {
        #         "input": {
        #             "id": str(self.SAMPLE_PROJECT.id),
        #         }
        #     },
        # )
        #
        # self.assertEqual(
        #     r["data"]["deleteAccessmodProject"],
        #     {
        #         "success": True,
        #     },
        # )
        # self.assertIsNone(Project.objects.filter(id=self.SAMPLE_PROJECT.id).first())
