import os

c = get_config()

# General
c.Spawner.default_url = '/lab'

# Authentication (see https://github.com/jupyterhub/nativeauthenticator)
c.JupyterHub.authenticator_class = 'nativeauthenticator.NativeAuthenticator'
c.Authenticator.admin_users = os.environ['ADMIN_USERNAMES'].split(",")
c.NativeAuthenticator.check_common_password = True
c.NativeAuthenticator.allowed_failed_logins = 3
c.NativeAuthenticator.seconds_before_next_try = 1200

# Docker spawner (see https://github.com/jupyterhub/dockerspawner)
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = os.environ['DOCKER_JUPYTER_CONTAINER']
# This is really useful to avoid "dangling containers" that cannot connect to the Hub anymore
# (and the dreaded The "'ip' trait of a Server instance must be a unicode string, but a value of None
# <class 'NoneType'> was specified" error - see https://github.com/jupyterhub/jupyterhub/issues/2213 and
# https://github.com/defeo/jupyterhub-docker/issues/5)
c.DockerSpawner.remove = True
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.JupyterHub.hub_ip = '0.0.0.0'  # listen on all interfaces
c.JupyterHub.hub_connect_ip = os.environ["HUB_IP"]  # ip as seen on the docker network. Can also be a hostname.

# Hub db (see https://jupyterhub.readthedocs.io/en/stable/api/app.html#jupyterhub.app.JupyterHub.db_url and
# https://jupyterhub.readthedocs.io/en/stable/reference/database.html#using-an-rdbms-postgresql-mysql)
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_HUB_DB = os.environ["POSTGRES_HUB_DB"]
c.JupyterHub.db_url = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_HUB_DB}'

# POSTGRES_CONTENT_DB = os.environ["POSTGRES_CONTENT_DB"]
