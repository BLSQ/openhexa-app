from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.connector_dhis2.models import Instance


def notebooks_credentials(credentials: NotebooksCredentials):
    """
    Provides the notebooks credentials data that allows users to access DHIS2 Instances
    in the notebooks component.
    """

    instances = Instance.objects.filter_for_user(credentials.user)
    if not (credentials.user.is_active and credentials.user.is_superuser):
        instances = instances.filter(instancepermission__show_credentials=True)

    if len(instances) > 0:
        for instance in instances:
            credentials.update_env(
                {
                    f"{instance.env_name}_URL": instance.api_credentials.api_url,
                    f"{instance.env_name}_USERNAME": instance.api_credentials.username,
                    f"{instance.env_name}_PASSWORD": instance.api_credentials.password,
                }
            )

        credentials.update_env(
            {"DHIS2_INSTANCES_SLUGS": ",".join([x.slug for x in instances])}
        )
