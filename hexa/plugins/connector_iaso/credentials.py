from slugify import slugify

import hexa.plugins.connector_iaso.models as models
from hexa.notebooks.credentials import NotebooksCredentials
from hexa.pipelines.credentials import PipelinesCredentials


def notebooks_credentials(credentials: NotebooksCredentials):
    """Provides the notebooks credentials data that allows users to access IASO instance in the notebooks component."""

    iaso_tokens = models.ApiToken.objects.filter(user=credentials.user)
    if iaso_tokens:
        env = {}

        for t in iaso_tokens:
            label = slugify(
                t.iaso_account.name, separator="_", word_boundary=True
            ).upper()
            env[f"IASO_{label}_URL"] = t.iaso_account.api_url
            env[f"IASO_{label}_TOKEN"] = t.token

        credentials.update_env(env)


def pipelines_credentials(credentials: PipelinesCredentials):
    """Provides the pipelines credentials data that allows users to access IASO instance in the pipelines component."""
    # TODO
