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
    target_organization = forms.CharField(
        label="Target organization id",
        help_text="UUID of the organization to create the workspace under.",
    )
    target_workspace_name = forms.CharField(
        required=False,
        label="Target workspace name",
        help_text="Optional name for the target workspace. "
        "Defaults to the source workspace name.",
    )

    resources = forms.MultipleChoiceField(
        required=False,
        choices=_resource_choices,
        widget=forms.CheckboxSelectMultiple,
        help_text="The workspace-metadata copier always runs.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resources"].initial = _default_resources()

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
