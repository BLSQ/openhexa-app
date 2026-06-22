"""Forms backing the workspace-duplicator admin views."""

from django import forms

from hexa.workspace_duplicator.orchestrator import WORKSPACE_COPIERS


def _resource_choices() -> list[tuple[str, str]]:
    return [(c.name, c.label) for c in WORKSPACE_COPIERS]


def _default_resources() -> list[str]:
    return [c.name for c in WORKSPACE_COPIERS]


def _mandatory_resources() -> set[str]:
    return {c.name for c in WORKSPACE_COPIERS if c.mandatory}


class MigrateWorkspaceForm(forms.Form):
    """Pick a source endpoint, a target endpoint, and the resources to copy.

    A blank server URL means the local server; credentials are required only for
    a remote (URL-bearing) side. The mandatory workspace-metadata copier is
    always run regardless of what the operator selects.
    """

    source_url = forms.URLField(
        required=False,
        label="Source server URL",
        help_text="GraphQL endpoint of the source server. Leave blank for the local server.",
    )
    source_email = forms.EmailField(required=False, label="Source superuser email")
    source_password = forms.CharField(
        required=False, label="Source superuser password", widget=forms.PasswordInput
    )
    source_slug = forms.CharField(label="Source workspace slug")

    target_url = forms.URLField(
        required=False,
        label="Target server URL",
        help_text="GraphQL endpoint of the target server. Leave blank for the local server.",
    )
    target_email = forms.EmailField(required=False, label="Target superuser email")
    target_password = forms.CharField(
        required=False, label="Target superuser password", widget=forms.PasswordInput
    )
    target_organization = forms.CharField(
        required=False,
        label="Target organization id",
        help_text="Optional UUID of the organization to create the workspace under.",
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
        for field in (f"{side}_email", f"{side}_password"):
            if not self.cleaned_data.get(field):
                self.add_error(
                    field,
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
