"""Forms backing the workspace-copier admin views."""

from django import forms

from hexa.workspace_copier.orchestrator import WORKSPACE_COPIERS
from hexa.workspace_copier.templates import DEFAULT_SOURCE_URL


def _resource_choices() -> list[tuple[str, str]]:
    return [(c.name, c.label) for c in WORKSPACE_COPIERS]


def _default_resources() -> list[str]:
    return [c.name for c in WORKSPACE_COPIERS]


def _mandatory_resources() -> set[str]:
    return {c.name for c in WORKSPACE_COPIERS if c.mandatory}


def _option_fields() -> dict[str, tuple[str, ...]]:
    return {c.name: c.option_fields for c in WORKSPACE_COPIERS if c.option_fields}


class ResourceSelect(forms.CheckboxSelectMultiple):
    """Checkbox list where a mandatory copier is checked and locked.

    ``clean`` adds those back whatever is submitted, so an enabled box would
    offer a choice that doesn't exist.
    """

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        if str(value) in _mandatory_resources():
            option["attrs"]["checked"] = True
            option["attrs"]["disabled"] = True
        return option


class CopyWorkspaceForm(forms.Form):
    """Pick a source endpoint, a target endpoint, and the resources to copy.

    A blank server URL means the local server; a token is required only for a
    remote (URL-bearing) side. The mandatory workspace-metadata copier is always
    run regardless of what the operator selects.
    """

    source_url = forms.URLField(
        required=False,
        label="Source server URL",
        help_text="GraphQL endpoint of the source server. Leave blank for the local server.",
    )
    source_token = forms.CharField(
        required=False,
        label="Source ServiceAccount token",
        widget=forms.PasswordInput(render_value=True),
    )
    source_slug = forms.CharField(label="Source workspace slug")

    target_url = forms.URLField(
        required=False,
        label="Target server URL",
        help_text="GraphQL endpoint of the target server. Leave blank for the local server.",
    )
    target_token = forms.CharField(
        required=False,
        label="Target ServiceAccount token",
        widget=forms.PasswordInput(render_value=True),
    )
    target_mode = forms.ChoiceField(
        label="Target workspace",
        choices=[
            ("new", "Create a new workspace"),
            ("existing", "Copy into an existing workspace"),
        ],
        initial="new",
        widget=forms.RadioSelect,
        help_text="Copying into an existing workspace makes the copy idempotent: "
        "resources that already exist are skipped, so an interrupted run can be "
        "re-run safely.",
    )
    target_organization = forms.CharField(
        required=False,
        label="Target organization id",
        help_text="UUID of the organization to create the workspace under.",
    )
    target_workspace_name = forms.CharField(
        required=False,
        label="Target workspace name",
        help_text="Optional name for the new workspace. "
        "Defaults to the source workspace name.",
    )
    target_workspace_slug = forms.CharField(
        required=False,
        label="Target workspace slug",
        help_text="Slug of the existing workspace to copy into.",
    )

    resources = forms.MultipleChoiceField(
        required=False,
        choices=_resource_choices,
        widget=ResourceSelect,
    )
    all_dataset_versions = forms.BooleanField(
        required=False,
        label="Copy all dataset versions",
        label_suffix="",
        help_text="Off by default: only each dataset's latest version is copied.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resources"].initial = _default_resources()

    def resource_rows(self):
        """Pair each resource checkbox with the option fields tuning that resource.

        Lets the template nest a copier's options under its own checkbox instead
        of listing them all after the resource list, where nothing says which
        resource they affect.
        """
        option_fields = _option_fields()
        mandatory = _mandatory_resources()
        for checkbox in self["resources"]:
            name = str(checkbox.data["value"])
            yield {
                "checkbox": checkbox,
                "mandatory": name in mandatory,
                "options": [self[field] for field in option_fields.get(name, ())],
            }

    def _clean_endpoint_credentials(self, side: str) -> None:
        url = self.cleaned_data.get(f"{side}_url")
        if not url:
            return
        if not self.cleaned_data.get(f"{side}_token"):
            self.add_error(
                f"{side}_token",
                f"Required when a {side} server URL is set (remote endpoint).",
            )

    def clean(self):
        cleaned = super().clean()
        self._clean_endpoint_credentials("source")
        self._clean_endpoint_credentials("target")

        if cleaned.get("target_mode") == "existing":
            # Hidden fields may still carry values typed before switching mode.
            cleaned["target_organization"] = ""
            cleaned["target_workspace_name"] = ""
            if not cleaned.get("target_workspace_slug"):
                self.add_error("target_workspace_slug", "This field is required.")
        else:
            cleaned["target_workspace_slug"] = ""
            if not cleaned.get("target_organization"):
                self.add_error("target_organization", "This field is required.")

        selected = set(cleaned.get("resources") or _default_resources())
        selected |= _mandatory_resources()
        cleaned["resources"] = selected
        return cleaned


class CopyTemplatesForm(forms.Form):
    """Pick a source and target server to copy all pipeline templates between.

    Templates are server-wide, so there is no workspace slug or resource
    selection — both sides are remote and each needs a ServiceAccount token. The
    target organization is where the host "Template pipelines" workspace is
    created when it doesn't already exist.
    """

    source_url = forms.URLField(
        label="Source server URL",
        initial=DEFAULT_SOURCE_URL,
        help_text="GraphQL endpoint of the source server. Defaults to production.",
    )
    source_token = forms.CharField(
        label="Source ServiceAccount token",
        widget=forms.PasswordInput(render_value=True),
    )

    target_url = forms.URLField(
        label="Target server URL",
        help_text="GraphQL endpoint of the target server.",
    )
    target_token = forms.CharField(
        label="Target ServiceAccount token",
        widget=forms.PasswordInput(render_value=True),
    )
    target_organization = forms.CharField(
        label="Target organization id",
        help_text="UUID of the organization the host 'Template pipelines' "
        "workspace is created under when needed.",
    )
