import os

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
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.JupyterHub.hub_ip = '0.0.0.0'  # listen on all interfaces
c.JupyterHub.hub_connect_ip = os.environ["HUB_IP"]  # ip as seen on the docker network. Can also be a hostname.

