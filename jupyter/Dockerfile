FROM jupyter/datascience-notebook:42f4c82a07ff

USER root

# System libraries
RUN apt-get update

# For rgdal (R)
RUN apt-get install -y libgdal-dev
# For sf (R)
RUN apt-get install -y libudunits2-dev

# Python packages (conda-forge - preferred method)
RUN conda install -c conda-forge --quiet --yes \
    'descartes=1.1.0' \
    'geoalchemy2=0.6.3' \
    'geopandas=0.8.1' \
    'hybridcontents=0.3.0' \
    'mapclassify=2.3.0' \
    'nbresuse=0.3.6' \
    'plotly=4.12.0' \
    'psycopg2=2.8.6' \
    'rasterstats=0.14.0' \
    's3contents=0.5.1' \
    'voila=0.2.4' \
    && conda clean --all -f -y

# Python packages (pip - for what is not available in conda-forge)
RUN pip install hdx-python-api==4.7.1 tabpy==2.3.1 cowsay==2.0.3

# R packages, in multiple steps for Docker layering (conda-forge - preferred method)
RUN conda install -c conda-forge --quiet --yes \
    'r-rjson=0.2.20' \
    'r-rpostgres=1.2.1' \
    'r-rjava=0.9_13' \
    && conda clean --all -f -y
RUN conda install -c conda-forge --quiet --yes \
    'r-aws.s3=0.3.21' \
    'r-getpass=0.2_2' \
    'r-ggmap=3.0.0' \
    'r-hmisc=4.4_1' \
    'r-maptools=1.0_2' \
    'r-raster=3.3_13' \
    'r-readxl=1.3.1' \
    'r-rcolorbrewer=1.1_2' \
    'r-rgdal=1.5_16' \
    'r-rgeos=0.5_5' \
    'r-rgooglemaps=1.4.5.3' \
    && conda clean --all -f -y
RUN conda install -c conda-forge --quiet --yes \
    'r-sf=0.9_6' \
    'r-tidyverse=1.3.0' \
    'r-viridis=0.5.1' \
    'r-ggthemes=4.2.0' \
    'r-geojsonio=0.9.2' \
    && conda clean --all -f -y

# R packages (cran - for what is not available in conda-forge)
RUN R -e "install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('isotree', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"

# Jupyterlab extensions
# Inspired by https://github.com/jupyter/docker-stacks/blob/master/scipy-notebook/Dockerfile
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@2 --no-build && \
    jupyter labextension install jupyterlab-plotly@4.12.0 --no-build && \
    jupyter labextension install plotlywidget@4.12.0 --no-build && \
    jupyter labextension install @jupyter-voila/jupyterlab-preview --no-build && \
    jupyter labextension install jupyterlab-topbar-extension jupyterlab-system-monitor --no-build && \
    # see https://github.com/BLSQ/habari/issues/36
    # TODO: remove above?
    jupyter lab build -y && \
    # jupyter lab build -y --minimize=False && \
    # TODO: remove above?
    jupyter lab clean -y && \
    npm cache clean --force && \
    rm -rf "/home/${NB_USER}/.cache/yarn"

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
USER $NB_UID
RUN mkdir -p /home/jovyan/.ipython/profile_default/startup
COPY ipython-startup /home/jovyan/.ipython/profile_default/startup
