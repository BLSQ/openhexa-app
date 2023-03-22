FROM python:3.9 as deps

RUN apt-get update
RUN apt-get install -y mdbtools wait-for-it gdal-bin libgdal-dev proj-bin

RUN pip install --upgrade pip

# Needed for TailwindCSS
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/

# Mount a tmp folder inside the container to keep a cache for pip
# see https://pythonspeed.com/articles/docker-cache-pip-downloads/
# Force setuptools version to build pygdal
RUN pip install setuptools==57.5.0 && pip install -r requirements.txt


FROM deps as build
COPY . /code/

ENV SECRET_KEY="collectstatic"
RUN python manage.py tailwind install
RUN python manage.py tailwind build --no-input
RUN python manage.py collectstatic --noinput

FROM build as dev
# We need to have the docker client in the container to run docker-compose commands and execute pipelines
RUN mkdir -m 0755 -p /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
RUN apt-get install -y docker-ce-cli
ENTRYPOINT ["/code/docker-entrypoint.sh"]
CMD start


FROM build as production
ENTRYPOINT ["/code/docker-entrypoint.sh"]
CMD start
