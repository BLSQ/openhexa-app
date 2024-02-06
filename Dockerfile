FROM python:3.11 as deps

RUN apt-get update
RUN apt-get install -y mdbtools wait-for-it gdal-bin libgdal-dev proj-bin gettext

RUN pip install --upgrade pip

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/

# Mount a tmp folder inside the container to keep a cache for pip
# see https://pythonspeed.com/articles/docker-cache-pip-downloads/
# Force setuptools version to build pygdal
RUN pip install setuptools==57.5.0 && pip install -r requirements.txt

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
RUN apt-get update
RUN apt-get install -y docker-ce-cli