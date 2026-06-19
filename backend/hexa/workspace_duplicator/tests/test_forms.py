from django.test import SimpleTestCase

from hexa.workspace_duplicator.forms import MigrateWorkspaceForm


def _base_data(**overrides):
    data = {
        "source_url": "",
        "source_email": "",
        "source_password": "",
        "source_slug": "my-workspace",
        "target_url": "",
        "target_email": "",
        "target_password": "",
        "target_organization": "",
        "resources": ["connections"],
    }
    data.update(overrides)
    return data


class MigrateWorkspaceFormTest(SimpleTestCase):
    def test_local_endpoints_need_no_credentials(self):
        form = MigrateWorkspaceForm(data=_base_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_remote_source_requires_credentials(self):
        form = MigrateWorkspaceForm(
            data=_base_data(source_url="https://example.org/graphql/")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("source_email", form.errors)
        self.assertIn("source_password", form.errors)

    def test_remote_source_with_credentials_is_valid(self):
        form = MigrateWorkspaceForm(
            data=_base_data(
                source_url="https://example.org/graphql/",
                source_email="admin@example.org",
                source_password="secret",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_mandatory_resource_always_included(self):
        form = MigrateWorkspaceForm(data=_base_data(resources=["connections"]))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn("workspace", form.cleaned_data["resources"])

    def test_empty_resources_defaults_to_all(self):
        form = MigrateWorkspaceForm(data=_base_data(resources=[]))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn("workspace", form.cleaned_data["resources"])
        self.assertIn("pipelines", form.cleaned_data["resources"])
