FROM jupyter/datascience-notebook:acb539921413

RUN pip install s3contents hybridcontents

COPY jupyter_config /etc/jupyter/

COPY local_modules /opt/local_modules
ENV PYTHONPATH /opt/local_modules/

RUN rm -r /home/$NB_USER/work