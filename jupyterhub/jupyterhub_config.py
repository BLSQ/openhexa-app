import os
from oauthenticator.github import GitHubOAuthenticator

c = get_config()

# General
c.Spawner.default_url = '/lab'

# Docker Spawner (see https://github.com/jupyterhub/dockerspawner)
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = os.environ['DOCKER_JUPYTER_CONTAINER']
c.DockerSpawner.debug = True
# This is really useful to avoid "dangling containers" that cannot connect to the Hub anymore
# (and the dreaded The "'ip' trait of a Server instance must be a unicode string, but a value of None
# <class 'NoneType'> was specified" error - see https://github.com/jupyterhub/jupyterhub/issues/2213 and
# https://github.com/defeo/jupyterhub-docker/issues/5)
c.DockerSpawner.remove = True
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.env_keep = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_BUCKET_NAME"]
c.JupyterHub.hub_ip = '0.0.0.0'  # listen on all interfaces
c.JupyterHub.hub_connect_ip = os.environ["HUB_IP"]  # ip as seen on the docker network. Can also be a hostname.

# Oauthenticator (see https://github.com/jupyterhub/oauthenticator)
c.JupyterHub.authenticator_class = GitHubOAuthenticator
