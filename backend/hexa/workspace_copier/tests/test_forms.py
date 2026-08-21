from django.test import SimpleTestCase

from hexa.workspace_copier.forms import CopyWorkspaceForm


def _base_data(**overrides):
    data = {
        "source_url": "",
        "source_token": "",
        "source_slug": "my-workspace",
        "target_url": "",
        "target_token": "",
        "target_mode": "new",
        "target_organization": "org-1",
        "resources": ["connections"],
    }
    data.update(overrides)
    return data


class CopyWorkspaceFormTest(SimpleTestCase):
    def test_local_endpoints_need_no_token(self):
        form = CopyWorkspaceForm(data=_base_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_target_organization_is_required(self):
        form = CopyWorkspaceForm(data=_base_data(target_organization=""))
        self.assertFalse(form.is_valid())
        self.assertIn("target_organization", form.errors)

    def test_existing_mode_needs_no_organization(self):
        form = CopyWorkspaceForm(
            data=_base_data(
                target_mode="existing",
                target_organization="",
                target_workspace_slug="existing-ws",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_existing_mode_requires_slug(self):
        form = CopyWorkspaceForm(data=_base_data(target_mode="existing"))
        self.assertFalse(form.is_valid())
        self.assertIn("target_workspace_slug", form.errors)

    def test_existing_mode_drops_new_workspace_fields(self):
        form = CopyWorkspaceForm(
            data=_base_data(
                target_mode="existing",
                target_workspace_name="Ignored",
                target_workspace_slug="existing-ws",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["target_organization"], "")
        self.assertEqual(form.cleaned_data["target_workspace_name"], "")

    def test_new_mode_drops_slug(self):
        form = CopyWorkspaceForm(data=_base_data(target_workspace_slug="leftover"))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["target_workspace_slug"], "")

    def test_remote_source_requires_token(self):
        form = CopyWorkspaceForm(
            data=_base_data(source_url="https://example.org/graphql/")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("source_token", form.errors)

    def test_remote_source_with_token_is_valid(self):
        form = CopyWorkspaceForm(
            data=_base_data(
                source_url="https://example.org/graphql/",
                source_token="src-token",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_mandatory_resource_always_included(self):
        form = CopyWorkspaceForm(data=_base_data(resources=["connections"]))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn("workspace", form.cleaned_data["resources"])

    def test_resource_rows_nest_options_under_their_copier(self):
        rows = {
            row["checkbox"].data["value"]: row
            for row in CopyWorkspaceForm().resource_rows()
        }
        self.assertEqual(
            [option.name for option in rows["datasets"]["options"]],
            ["all_dataset_versions"],
        )
        self.assertEqual(rows["connections"]["options"], [])

    def test_mandatory_resource_renders_checked_and_locked(self):
        rows = {
            row["checkbox"].data["value"]: row
            for row in CopyWorkspaceForm().resource_rows()
        }
        self.assertTrue(rows["workspace"]["mandatory"])
        self.assertFalse(rows["datasets"]["mandatory"])
        markup = str(rows["workspace"]["checkbox"])
        self.assertIn("checked", markup)
        self.assertIn("disabled", markup)

    def test_empty_resources_defaults_to_all(self):
        form = CopyWorkspaceForm(data=_base_data(resources=[]))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn("workspace", form.cleaned_data["resources"])
        self.assertIn("pipelines", form.cleaned_data["resources"])
