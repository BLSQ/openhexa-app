FROM python:3.9

RUN apt-get update
RUN apt-get install -y mdbtools wait-for-it gdal-bin libgdal-dev proj-bin

RUN pip install --upgrade pip

# Needed for TailwindCSS
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/

# Mount a tmp folder inside the container to keep a cache for pip
# see https://pythonspeed.com/articles/docker-cache-pip-downloads/
# Force setuptools version to build pygdal
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install setuptools==57.5.0 && pip install -r requirements.txt

COPY . /code/

ENV SECRET_KEY="collectstatic"
RUN python manage.py tailwind install
RUN python manage.py tailwind build --no-input
RUN python manage.py collectstatic --noinput

ENTRYPOINT ["/code/docker-entrypoint.sh"]
CMD start
