from django.test import SimpleTestCase

from hexa.workspace_copier.forms import CUSTOM_SERVER, CopyWorkspaceForm
from hexa.workspace_copier.templates import DEFAULT_SOURCE_URL


def _base_data(**overrides):
    data = {
        "source_server": "",
        "source_url": "",
        "source_token": "src-token",
        "source_slug": "my-workspace",
        "target_server": "",
        "target_url": "",
        "target_token": "tgt-token",
        "target_mode": "new",
        "target_organization": "org-1",
        "resources": ["connections"],
    }
    data.update(overrides)
    return data


class CopyWorkspaceFormTest(SimpleTestCase):
    def test_this_server_on_both_sides_is_a_same_server_copy(self):
        form = CopyWorkspaceForm(data=_base_data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.cleaned_data["same_server"])

    def test_another_server_on_one_side_is_not_a_same_server_copy(self):
        for side in ("source", "target"):
            with self.subTest(side=side):
                form = CopyWorkspaceForm(
                    data=_base_data(**{f"{side}_server": DEFAULT_SOURCE_URL})
                )
                self.assertTrue(form.is_valid(), form.errors)
                self.assertFalse(form.cleaned_data["same_server"])

    def test_same_server_cannot_be_posted(self):
        form = CopyWorkspaceForm(
            data=_base_data(source_server=DEFAULT_SOURCE_URL, same_server="on")
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(form.cleaned_data["same_server"])

    def test_token_is_required_for_this_server_too(self):
        form = CopyWorkspaceForm(data=_base_data(source_token="", target_token=""))
        self.assertFalse(form.is_valid())
        self.assertIn("source_token", form.errors)
        self.assertIn("target_token", form.errors)

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

    def test_source_url_requires_token(self):
        form = CopyWorkspaceForm(
            data=_base_data(
                source_server=CUSTOM_SERVER,
                source_url="https://example.org/graphql/",
                source_token="",
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("source_token", form.errors)

    def test_custom_server_uses_the_typed_url(self):
        form = CopyWorkspaceForm(
            data=_base_data(
                source_server=CUSTOM_SERVER, source_url="https://example.org/graphql/"
            )
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data["source_url"], "https://example.org/graphql/"
        )

    def test_custom_server_requires_a_url(self):
        form = CopyWorkspaceForm(data=_base_data(target_server=CUSTOM_SERVER))
        self.assertFalse(form.is_valid())
        self.assertIn("target_url", form.errors)
        self.assertNotIn("source_url", form.errors)

    def test_preset_server_resolves_to_its_url(self):
        form = CopyWorkspaceForm(data=_base_data(source_server=DEFAULT_SOURCE_URL))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["source_url"], DEFAULT_SOURCE_URL)

    def test_this_server_ignores_a_leftover_custom_url(self):
        form = CopyWorkspaceForm(
            data=_base_data(target_url="https://example.org/graphql/")
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["target_url"], "")

    def test_unknown_server_is_rejected(self):
        form = CopyWorkspaceForm(
            data=_base_data(source_server="https://evil.example.org/graphql/")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("source_server", form.errors)

    def test_server_choices_show_their_url(self):
        labels = dict(CopyWorkspaceForm().fields["source_server"].choices)
        self.assertEqual(
            labels[DEFAULT_SOURCE_URL], f"Production (SaaS) — {DEFAULT_SOURCE_URL}"
        )
        self.assertTrue(labels[""].startswith("This server — http"))
        self.assertEqual(labels[CUSTOM_SERVER], "Other…")

    def test_ssl_verification_is_on_by_default(self):
        form = CopyWorkspaceForm(data=_base_data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(form.cleaned_data["disable_ssl_verification"])

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
        self.assertEqual(
            [option.name for option in rows["connections"]["options"]],
            ["include_connection_secrets"],
        )

    def test_connection_secrets_included_by_default(self):
        self.assertTrue(CopyWorkspaceForm()["include_connection_secrets"].initial)

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

    def test_empty_resources_copies_only_the_mandatory_ones(self):
        form = CopyWorkspaceForm(data=_base_data(resources=[]))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["resources"], {"workspace"})
