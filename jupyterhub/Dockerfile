FROM jupyterhub/jupyterhub:1.2

COPY jupyterhub_config.py .

RUN pip install --upgrade pip
RUN pip install dockerspawner==0.11.1 jupyterhub-nativeauthenticator==0.0.5