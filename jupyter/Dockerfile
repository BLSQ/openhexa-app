FROM jupyter/datascience-notebook:acb539921413

RUN pip install s3contents hybridcontents psycopg2-binary

COPY config /etc/jupyter/
COPY SAMPLE_README.md /home/jovyan/README.md
COPY local_modules /opt/local_modules
ENV PYTHONPATH /opt/local_modules/

RUN rm -r /home/$NB_USER/work
