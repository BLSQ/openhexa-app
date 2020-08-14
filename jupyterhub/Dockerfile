FROM jupyterhub/jupyterhub:1.2

COPY jupyterhub_config.py .

RUN pip install --upgrade pip
RUN pip install dockerspawner oauthenticator psycopg2-binary
