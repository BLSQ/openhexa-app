FROM python:3.12-slim as deps

RUN \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && \
  apt-get install -y build-essential mdbtools wait-for-it gdal-bin libgdal-dev proj-bin gettext lsb-release procps && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install --upgrade pip

RUN mkdir /code
WORKDIR /code

RUN \
  --mount=type=cache,target=/root/.cache \ 
  --mount=type=bind,source=requirements.txt,target=/code/requirements.txt \
  pip install setuptools==57.5.0 && pip install -r requirements.txt

COPY . /code/

ENV SECRET_KEY="collectstatic"
ENV DJANGO_SETTINGS_MODULE config.settings.production
ENTRYPOINT ["/code/docker-entrypoint.sh"]
CMD start

FROM deps as app
ENV DJANGO_SETTINGS_MODULE config.settings.production
RUN python manage.py collectstatic --noinput

# Staged used to run the pipelines scheduler and runner
FROM app as pipelines
ENV DJANGO_SETTINGS_MODULE config.settings.production
RUN mkdir -m 0755 -p /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update && apt-get install -y docker-ce-cli