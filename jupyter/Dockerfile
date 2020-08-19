FROM jupyter/datascience-notebook:acb539921413

RUN pip install s3contents hybridcontents psycopg2-binary

# custom config
COPY config /etc/jupyter/

# custom local (Python) modules
COPY local_modules /opt/local_modules
ENV PYTHONPATH /opt/local_modules/

# sample files
# k8s: stored in /tmp within the pod, then copied back in the home directory after the PVC has been mounted through
# a postStart hook defined in config.yaml
# (see https://zero-to-jupyterhub.readthedocs.io/en/latest/customizing/user-environment.html#about-user-storage-and-adding-files-to-it)
COPY sample_files/* /opt/habari_sample_files/
# the next line is for the local docker-compose environment only
COPY sample_files/* /home/jovyan/
