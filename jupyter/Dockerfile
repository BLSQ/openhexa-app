FROM jupyter/datascience-notebook:016833b15ceb


USER root

# System libraries
RUN apt-get update

# For rgdal (R)
RUN apt-get install -y libgdal-dev
# For sf (R)
RUN apt-get install -y libudunits2-dev

# Update conda - because why not? Trying to "improve" performance
RUN conda update anaconda

# R packages, in multiple steps for Docker layering (conda-forge - preferred method)
RUN conda install -c conda-forge --quiet --yes \
    'r-aws.s3=0.*' \
    'r-geojsonio=0.*' \
    'r-getpass=0.*' \
    'r-ggmap=3.*' \
    'r-ggthemes=4.*' \
    'r-hmisc=4.*' \
    'r-maptools=1.*' \
    'r-plotly=4.*' \
    'r-raster=3.*' \
    'r-readxl=1.*' \
    'r-rcolorbrewer=1.*' \
    'r-rgdal=1.*' \
    'r-rgeos=0.*' \
    'r-rgooglemaps=1.*' \
    'r-rjava=0.*' \
    'r-rjson=0.*' \
    'r-rpostgres=1.*' \
    'r-sf=0.*' \
    'r-tidyverse=1.*' \
    'r-viridis=0.*' \
    && conda clean --all -f -y

# Python packages, in multiple steps for Docker layering (conda-forge - preferred method)
RUN conda install -c conda-forge --quiet --yes \
    'dask-ml=1.*' \
    'descartes=1.*' \
    'geoalchemy2=0.*' \
    'geopandas=0.*' \
    'hybridcontents=0.*' \
    'ipywidgets=7.*' \
    'lxml=4.*' \
    'mapclassify=2.*' \
    'nbresuse=0.*' \
    'plotly=4.*' \
    'psycopg2=2.*' \
    'rapidfuzz=0.*' \
    'rasterstats=0.*' \
    's3contents=0.*' \
    && conda clean --all -f -y

# Python packages (pip - for what is not available in conda-forge)
RUN pip install \
    'cowsay==3.*' \
    'hdx-python-api==4.*' \
    'jupyterlab-topbar==0.*' \
    'jupyterlab-system-monitor==0.*' \
    'tabpy==2.*'

# R packages (cran - for what is not available in conda-forge)
RUN R -e "install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('isotree', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"

# Jupyterlab extensions - check if still necessary
RUN jupyter labextension install jupyterlab-plotly@4.* --no-build && \
    jupyter labextension install plotlywidget@4.* --no-build && \
    jupyter lab build -y && \
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
