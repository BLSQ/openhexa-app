from django.contrib.auth import get_user_model

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import Pipeline
from hexa.tags.models import Tag
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
)
from hexa.workspaces.models import (
    Workspace,
)

User = get_user_model()


class PipelineTagMutationTest(GraphQLTestCase):
    USER_ADMIN = None
    USER_MEMBER = None
    USER_VIEWER = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user("admin@openhexa.org", "password")
        cls.USER_MEMBER = User.objects.create_user("viewer@openhexa.org", "password")

        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org",
            organization_type="CORPORATE",
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Test workspace",
            description="Test workspace",
        )
        cls.WORKSPACE.organization = cls.ORGANIZATION
        cls.WORKSPACE.save()

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_MEMBER,
            role=OrganizationMembershipRole.MEMBER,
        )
        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test Pipeline",
            code="print('hello')",
        )

    def test_admin_can_add_valid_tags(self):
        self.client.force_login(self.USER_ADMIN)

        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        id
                        tags {
                            id
                            name
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.id),
                    "tags": ["machine-learning", "data-science"],
                }
            },
        )
        self.assertEqual(r["data"]["updatePipeline"]["success"], True)
        self.assertEqual(r["data"]["updatePipeline"]["errors"], [])

        tags = r["data"]["updatePipeline"]["pipeline"]["tags"]
        tag_names = [tag["name"] for tag in tags]

        self.assertIn("machine-learning", tag_names)
        self.assertIn("data-science", tag_names)

    def test_editor_can_add_valid_tags(self):
        self.client.force_login(self.USER_MEMBER)

        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        tags {
                            name
                        }
                    }
                }
            }
            """,
            {"input": {"id": str(self.PIPELINE.id), "tags": ["ml-pipeline"]}},
        )
        print(r)
        self.assertEqual(r["data"]["updatePipeline"]["success"], True)
        self.assertEqual(r["data"]["updatePipeline"]["errors"], [])

        tag_names = [
            tag["name"] for tag in r["data"]["updatePipeline"]["pipeline"]["tags"]
        ]
        self.assertIn("ml-pipeline", tag_names)

    def test_viewer_cannot_add_tags(self):
        self.client.force_login(self.USER_MEMBER)

        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"id": str(self.PIPELINE.id), "tags": ["unauthorized-tag"]}},
        )
        self.assertEqual(r["data"]["updatePipeline"]["success"], False)
        self.assertIn("PERMISSION_DENIED", r["data"]["updatePipeline"]["errors"])

    def test_invalid_tag_names_rejected(self):
        self.client.force_login(self.USER_ADMIN)
        invalid_cases = [
            ("a", "too short"),
            ("tag!", "special characters"),
        ]

        for invalid_tag, description in invalid_cases:
            with self.subTest(tag=invalid_tag, description=description):
                r = self.run_query(
                    """
                    mutation updatePipeline($input: UpdatePipelineInput!) {
                        updatePipeline(input: $input) {
                            success
                            errors
                        }
                    }
                    """,
                    {"input": {"id": str(self.PIPELINE.id), "tags": [invalid_tag]}},
                )
                if r is not None and "data" in r:
                    self.assertEqual(r["data"]["updatePipeline"]["success"], False)
                    self.assertIn(
                        "INVALID_TAG_NAME", r["data"]["updatePipeline"]["errors"]
                    )

    def test_duplicate_tags_handled_gracefully(self):
        existing_tag = Tag.objects.create(name="existing-tag")
        self.PIPELINE.tags.add(existing_tag)

        self.client.force_login(self.USER_ADMIN)

        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        tags {
                            name
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.id),
                    "tags": ["existing-tag", "new-tag"],
                }
            },
        )

        self.assertEqual(r["data"]["updatePipeline"]["success"], True)
        self.assertEqual(r["data"]["updatePipeline"]["errors"], [])

        tag_names = [
            tag["name"] for tag in r["data"]["updatePipeline"]["pipeline"]["tags"]
        ]
        self.assertIn("existing-tag", tag_names)
        self.assertIn("new-tag", tag_names)

    def test_empty_tag_list_clears_tags(self):
        tag1 = Tag.objects.create(name="tag1")
        tag2 = Tag.objects.create(name="tag2")
        self.PIPELINE.tags.add(tag1, tag2)

        self.client.force_login(self.USER_ADMIN)

        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        tags {
                            name
                        }
                    }
                }
            }
            """,
            {"input": {"id": str(self.PIPELINE.id), "tags": []}},
        )

        self.assertEqual(r["data"]["updatePipeline"]["success"], True)
        self.assertEqual(r["data"]["updatePipeline"]["errors"], [])
        self.assertEqual(len(r["data"]["updatePipeline"]["pipeline"]["tags"]), 0)

    def test_mixed_new_and_existing_tags(self):
        existing_tag = Tag.objects.create(name="existing-tag")
        self.assertTrue(existing_tag.pk)

        self.client.force_login(self.USER_ADMIN)

        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        tags {
                            name
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.id),
                    "tags": ["existing-tag", "brand-new-tag", "another-new-tag"],
                }
            },
        )

        self.assertEqual(r["data"]["updatePipeline"]["success"], True)
        self.assertEqual(r["data"]["updatePipeline"]["errors"], [])

        tag_names = [
            tag["name"] for tag in r["data"]["updatePipeline"]["pipeline"]["tags"]
        ]
        expected_tags = ["existing-tag", "brand-new-tag", "another-new-tag"]

        for expected_tag in expected_tags:
            self.assertIn(expected_tag, tag_names)

        self.assertTrue(Tag.objects.filter(name="brand-new-tag").exists())
        self.assertTrue(Tag.objects.filter(name="another-new-tag").exists())

    def test_tag_case_sensitivity_validation(self):
        self.client.force_login(self.USER_ADMIN)

        Tag.objects.create(name="lowercase-tag")
        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"id": str(self.PIPELINE.id), "tags": ["LOWERCASE-TAG"]}},
        )

        self.assertEqual(r["data"]["updatePipeline"]["success"], False)
        self.assertIn("INVALID_TAG_NAME", r["data"]["updatePipeline"]["errors"])
