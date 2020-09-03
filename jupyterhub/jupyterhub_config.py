import os
from oauthenticator.github import GitHubOAuthenticator

c = get_config()

# General
c.Spawner.default_url = "/lab"

# Docker Spawner (see https://github.com/jupyterhub/dockerspawner)
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.DockerSpawner.image = os.environ["DOCKER_JUPYTER_CONTAINER"]
c.DockerSpawner.debug = True
# This is really useful to avoid "dangling containers" that cannot connect to the Hub anymore
# (and the dreaded The "'ip' trait of a Server instance must be a unicode string, but a value of None
# <class 'NoneType'> was specified" error - see https://github.com/jupyterhub/jupyterhub/issues/2213 and
# https://github.com/defeo/jupyterhub-docker/issues/5)
c.DockerSpawner.remove = True
c.DockerSpawner.network_name = os.environ["DOCKER_NETWORK_NAME"]
c.DockerSpawner.env_keep = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
    "S3_BUCKET_NAME_PUBLIC",
    "S3_BUCKET_NAME_LAKE",
    "S3_BUCKET_NAME_NOTEBOOKS",
    "EXPLORE_DB_URL",
    "EXPLORE_DB_USER",
    "EXPLORE_DB_PASSWORD",
    "EXPLORE_DB_HOST",
    "EXPLORE_DB_PORT",
    "EXPLORE_DB_NAME",
]
# Mount a volume for sensitive files (they cannot be part of the Docker image)
c.DockerSpawner.volumes = {
    f"{os.environ['PROJECT_PATH']}/local_secrets": "/etc/secrets"
}
c.DockerSpawner.environment = {
    "GOOGLE_APPLICATION_CREDENTIALS": "/etc/secrets/service-account.json"
}
c.JupyterHub.hub_ip = "0.0.0.0"  # listen on all interfaces
c.JupyterHub.hub_connect_ip = os.environ[
    "HUB_IP"
]  # ip as seen on the docker network. Can also be a hostname.

# Oauthenticator (see https://github.com/jupyterhub/oauthenticator)
c.JupyterHub.authenticator_class = GitHubOAuthenticator

# Use Postgres as the hub database
c.JupyterHub.db_url = os.environ["HUB_DB_URL"]
