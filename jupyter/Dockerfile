FROM jupyter/datascience-notebook:6d42503c684f

# Prefer conda (channel conda-forge) for Python packages
RUN conda install -c conda-forge --quiet --yes \
    's3contents=0.5.1' \
    'hybridcontents=0.3.0' \
    'psycopg2=2.8.5' \
    'geopandas=0.8.1' \
    'rasterstats=0.14.0' \
    'plotly=4.9.0' \
    'descartes=1.1.0' \
    'mapclassify=2.3.0' \
    'voila=0.1.23' \
    && \
    conda clean --all -f -y

# Plotly install requires jupyterlab extensions
# Inspired by https://github.com/jupyter/docker-stacks/blob/master/scipy-notebook/Dockerfile
RUN jupyter labextension install jupyterlab-plotly@4.9.0 --no-build && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && \
    jupyter labextension install plotlywidget@4.9.0 --no-build && \
    jupyter labextension install @jupyter-voila/jupyterlab-preview --no-build && \
    # see https://github.com/BLSQ/habari/issues/36
    # jupyter lab build -y && \
    jupyter lab build -y --minimize=False && \
    jupyter lab clean -y && \
    npm cache clean --force && \
    rm -rf "/home/${NB_USER}/.cache/yarn"

# Use pip for Python packages not in conda
RUN pip install hdx-python-api==4.6.3 tabpy==2.2.0

# R packages (available in conda forge)
RUN conda install -c conda-forge --quiet --yes \
    'r-aws.s3=0.3.21' \
    'r-readxl=1.3.1' \
    'r-rpostgres=1.2.0' \
    && \
    conda clean --all -f -y

# R package not available in conda
RUN R -e "install.packages('EpiEstim', dependencies=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('getPass', dependencies=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "devtools::install_github('reconhub/linelist')"

# custom config
COPY config /etc/jupyter/

# custom local (Python) modules
COPY local_modules /opt/local_modules
ENV PYTHONPATH /opt/local_modules/

# sample files
# k8s: stored in /tmp within the pod, then copied back in the home directory after the PVC has been mounted through
# a postStart hook defined in config.yaml
# (see https://zero-to-jupyterhub.readthedocs.io/en/latest/customizing/user-environment.html#about-user-storage-and-adding-files-to-it)
COPY sample_files/* /tmp/habari_sample_files/
# the next line is for the local docker-compose environment only
COPY sample_files/* /home/jovyan/

# custom startup scripts
# k8s: stored in /tmp within the pod, then copied back in the home directory after the PVC has been mounted through
# a postStart hook defined in config.yaml
# (see https://zero-to-jupyterhub.readthedocs.io/en/latest/customizing/user-environment.html#about-user-storage-and-adding-files-to-it)
COPY ipython-startup/* /tmp/ipython-startup/
# the next lines are for the local docker-compose environment only
USER jovyan
RUN mkdir -p /home/jovyan/.ipython/profile_default/startup
COPY ipython-startup /home/jovyan/.ipython/profile_default/startup
