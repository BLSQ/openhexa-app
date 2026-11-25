"""Forms backing the workspace-copier admin views."""

from django import forms
from django.conf import settings

from hexa.workspace_copier.orchestrator import WORKSPACE_COPIERS
from hexa.workspace_copier.templates import DEFAULT_SOURCE_URL

CUSTOM_SERVER = "custom"

SERVER_PRESETS = [
    (DEFAULT_SOURCE_URL, "Production (SaaS)"),
    ("https://api.demo.openhexa.org/graphql/", "Demo"),
    ("http://localhost:8000/graphql/", "Localhost"),
]


def _server_choices() -> list[tuple[str, str]]:
    """List the servers a side can be, each labelled with its GraphQL endpoint."""
    this_server_url = f"{settings.BASE_URL.rstrip('/')}/graphql/"
    return [
        ("", f"This server — {this_server_url}"),
        *((url, f"{label} — {url}") for url, label in SERVER_PRESETS),
        (CUSTOM_SERVER, "Other…"),
    ]


def _resource_choices() -> list[tuple[str, str]]:
    return [(c.name, c.label) for c in WORKSPACE_COPIERS]


def _default_resources() -> list[str]:
    return [c.name for c in WORKSPACE_COPIERS]


def _mandatory_resources() -> set[str]:
    return {c.name for c in WORKSPACE_COPIERS if c.mandatory}


def _option_fields() -> dict[str, tuple[str, ...]]:
    return {c.name: c.option_fields for c in WORKSPACE_COPIERS if c.option_fields}


def _help_texts() -> dict[str, str]:
    return {c.name: c.help_text for c in WORKSPACE_COPIERS if c.help_text}


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

    Each side's server is picked from a list; ``clean`` turns that choice into
    the ``source_url`` / ``target_url`` the service expects, where blank means
    this server's GraphQL endpoint. Picking this server on both sides makes it
    a same-server copy, which also copies the database and static web apps.
    This server is reached over GraphQL like any
    other, so a token is required on both sides. The mandatory
    workspace-metadata copier is always run regardless of what the operator
    selects.
    """

    source_server = forms.ChoiceField(
        required=False,
        label="Source server",
        choices=_server_choices,
    )
    source_url = forms.URLField(
        required=False,
        label="Custom server URL",
        help_text="GraphQL endpoint of the source server, "
        "e.g. https://api.example.org/graphql/",
    )
    source_token = forms.CharField(
        label="Source ServiceAccount token",
        widget=forms.PasswordInput(render_value=True),
    )
    source_slug = forms.CharField(
        label="Source workspace slug",
        help_text="On this server, type to search by slug or name.",
    )

    target_server = forms.ChoiceField(
        required=False,
        label="Target server",
        choices=_server_choices,
    )
    target_url = forms.URLField(
        required=False,
        label="Custom server URL",
        help_text="GraphQL endpoint of the target server, "
        "e.g. https://api.example.org/graphql/",
    )
    target_token = forms.CharField(
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
        help_text="UUID of the organization to create the workspace under. "
        "On this server, type to search by name.",
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
        help_text="Slug of the existing workspace to copy into. "
        "On this server, type to search by slug or name.",
    )

    disable_ssl_verification = forms.BooleanField(
        required=False,
        label="Disable SSL certificate verification",
        label_suffix="",
        help_text="Only for a server whose certificate is known to be expired or "
        "self-signed.",
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
    include_connection_secrets = forms.BooleanField(
        required=False,
        initial=True,
        label="Include connection secrets",
        label_suffix="",
        help_text="Copy stored credentials and API keys. If unchecked, "
        "connections are copied without their secret values.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resources"].initial = _default_resources()
        for field in self.fields.values():
            # The admin's own class for text inputs, so they get its width.
            if isinstance(
                field.widget, forms.TextInput | forms.URLInput | forms.PasswordInput
            ):
                field.widget.attrs.setdefault("class", "vTextField")

    def resource_rows(self):
        """Pair each resource checkbox with the option fields tuning that resource.

        Lets the template nest a copier's options under its own checkbox instead
        of listing them all after the resource list, where nothing says which
        resource they affect.
        """
        option_fields = _option_fields()
        help_texts = _help_texts()
        mandatory = _mandatory_resources()
        for checkbox in self["resources"]:
            name = str(checkbox.data["value"])
            yield {
                "checkbox": checkbox,
                "mandatory": name in mandatory,
                "help_text": help_texts.get(name, ""),
                "options": [self[field] for field in option_fields.get(name, ())],
            }

    def _resolve_server_url(self, cleaned, side):
        server = cleaned.get(f"{side}_server", "")
        if server != CUSTOM_SERVER:
            cleaned[f"{side}_url"] = server
            # The custom URL row is hidden then, so an error on a leftover
            # value would block the form without being shown.
            self.errors.pop(f"{side}_url", None)
        elif not cleaned.get(f"{side}_url") and f"{side}_url" not in self.errors:
            self.add_error(f"{side}_url", "This field is required.")

    def clean(self):
        cleaned = super().clean()
        self._resolve_server_url(cleaned, "source")
        self._resolve_server_url(cleaned, "target")
        # Only the explicit "This server" choice counts: a custom URL has
        # several valid spellings for this server, so it is never guessed from.
        cleaned["same_server"] = (
            cleaned.get("source_server") == "" and cleaned.get("target_server") == ""
        )

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

        # The mandatory copiers' boxes are disabled, so they are never posted:
        # an empty selection means "only the mandatory ones", not "everything".
        selected = set(cleaned.get("resources") or [])
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
