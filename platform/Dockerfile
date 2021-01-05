FROM python:3

RUN apt-get update
RUN apt-get install -y mdbtools wait-for-it
RUN pip install --upgrade pip

# Needed for TailwindCSS
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

ENV SECRET_KEY="connectstatic"
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "config.wsgi:application"]
