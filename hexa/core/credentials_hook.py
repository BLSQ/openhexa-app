import hexa.core.models
from hexa.notebooks.credentials import NotebooksCredentials


def custom_credentials(credentials: NotebooksCredentials):

    env = hexa.core.models.Credentials.objects.filter(user=credentials.user)

    if env:
        credentials.update_env(env)
