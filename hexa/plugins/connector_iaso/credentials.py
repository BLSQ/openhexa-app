from django.contrib.contenttypes.models import ContentType
from slugify import slugify

from hexa.notebooks.credentials import NotebooksCredentials
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.plugins.connector_iaso.models import Account, ApiToken


def notebooks_credentials(credentials: NotebooksCredentials):
    """Provides the notebooks credentials data that allows users to access IASO instance in the notebooks component."""

    iaso_tokens = ApiToken.objects.filter(user=credentials.user)
    if iaso_tokens:
        env = {}
        for t in iaso_tokens:
            label = slugify(
                t.iaso_account.name, separator="_", word_boundary=True
            ).upper()
            url = t.iaso_account.api_url
            if url.endswith("/api/"):
                url = url[:-4]
            env[f"IASO_{label}_URL"] = url
            env[f"IASO_{label}_TOKEN"] = t.token

        credentials.update_env(env)


def pipelines_credentials(credentials: PipelinesCredentials):
    """Provides the pipelines credentials data that allows users to access IASO instance in the pipelines component."""

    authorized_datasources = credentials.pipeline.authorized_datasources.filter(
        datasource_type=ContentType.objects.get_for_model(Account)
    )
    accounts = [x.datasource for x in authorized_datasources]
    env = {}
    for a in accounts:
        iaso_tokens = ApiToken.objects.filter(
            iaso_account=a, user=credentials.pipeline.user
        )
        if iaso_tokens:
            t = iaso_tokens[0]
            label = slugify(
                t.iaso_account.name, separator="_", word_boundary=True
            ).upper()
            url = t.iaso_account.api_url
            if url.endswith("/api/"):
                url = url[:-4]
            env[f"IASO_{label}_URL"] = url
            env[f"IASO_{label}_TOKEN"] = t.token
    credentials.env.update(env)
