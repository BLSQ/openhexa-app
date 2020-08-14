FROM jupyterhub/jupyterhub:1.2

COPY jupyterhub_config.py .

RUN pip install --upgrade pip
RUN pip install dockerspawner==0.11.1 oauthenticator==0.11.0 psycopg2-binary==2.8.5
