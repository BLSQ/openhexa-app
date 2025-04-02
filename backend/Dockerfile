FROM python:3.12-slim AS deps

RUN \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && \
  apt-get install -y build-essential mdbtools wait-for-it gdal-bin libgdal-dev proj-bin gettext lsb-release procps && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

  # Set up work directory
RUN mkdir /code
WORKDIR /code

# Upgrade pip and install requirements
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip setuptools==68.0.0

# Install project dependencies from requirements.txt
COPY requirements.txt /code/

RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt  && \ 
    apt-get remove -y build-essential && \
    apt-get autoremove -y

# Copy the rest of the application
COPY . /code/

ARG DJANGO_SETTINGS_MODULE

# Rootless
ARG USER=openhexa
ARG GROUP=openhexa
RUN groupadd --gid 1000 $GROUP &&\
  useradd --gid 1000 --uid 1000 --no-create-home --home-dir /code --no-log-init --shell /bin/bash $USER &&\
  passwd -d $USER

RUN chown -R $USER:$GROUP /code/
RUN mkdir /data && chown $USER:$GROUP /data
USER $USER:$GROUP

# Entry point
ARG WORKSPACE_STORAGE_LOCATION
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
ENV WORKSPACE_STORAGE_LOCATION=${WORKSPACE_STORAGE_LOCATION}
ENTRYPOINT ["/code/docker-entrypoint.sh"]
CMD ["start"]

FROM deps AS app
ARG DJANGO_SETTINGS_MODULE
ARG WORKSPACE_STORAGE_LOCATION
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
ENV WORKSPACE_STORAGE_LOCATION=${WORKSPACE_STORAGE_LOCATION}
RUN python manage.py collectstatic --noinput

# Staged used to run the pipelines scheduler and runner
FROM app AS pipelines
ARG DJANGO_SETTINGS_MODULE
ARG WORKSPACE_STORAGE_LOCATION
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
ENV WORKSPACE_STORAGE_LOCATION=${WORKSPACE_STORAGE_LOCATION}

USER root:root

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg && \
    mkdir -m 0755 -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Rootless
RUN groupadd --gid 999 docker
RUN usermod -aG docker $USER
USER $USER:$GROUP
