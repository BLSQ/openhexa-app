from typing import Dict, List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType

from hexa.notebooks.credentials import NotebooksCredentials
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.plugins.connector_dhis2.models import Instance


def get_env(instances: List[Tuple[Instance, Optional[str]]]) -> Dict[str, str]:
    env = {}
    if len(instances) > 0:
        for instance, label in instances:
            if not label:
                label = instance.slug
            label = label.replace("-", "_").upper()

            env[f"DHIS2_{label}_URL"] = instance.api_credentials.api_url
            env[f"DHIS2_{label}_USERNAME"] = instance.api_credentials.username
            env[f"DHIS2_{label}_PASSWORD"] = instance.api_credentials.password

        env["DHIS2_INSTANCES_SLUGS"] = ",".join(
            [
                (label if label else instance.slug).replace("-", "_").upper()
                for instance, label in instances
            ]
        )

    return env


def notebooks_credentials(credentials: NotebooksCredentials):
    """
    Provides the notebooks credentials data that allows users to access DHIS2 Instances
    in the notebooks component.
    """
    instances = Instance.objects.filter_for_user(credentials.user)
    if not (credentials.user.is_authenticated and credentials.user.is_superuser):
        instances = instances.filter(
            instancepermission__enable_notebooks_credentials=True
        )

    credentials.update_env(get_env([(x, None) for x in instances]))


def pipelines_credentials(credentials: PipelinesCredentials):
    """
    Provides the notebooks credentials data that allows users to access DHIS2 Instances
    in the pipelines component.
    """
    instances = []
    if hasattr(credentials.pipeline, "authorized_datasources"):
        authorized_datasource = credentials.pipeline.authorized_datasources.filter(
            datasource_type=ContentType.objects.get_for_model(Instance)
        )
        instances = [(x.datasource, x.slug) for x in authorized_datasource]
    else:
        # Pipelines V2
        authorized_datasource = Instance.objects.filter_for_user(
            credentials.pipeline.user
        )
        instances = [(x, None) for x in authorized_datasource]

    credentials.env.update(get_env(instances))
