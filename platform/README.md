Habari Platform
===============

Super WIP.

Note that we use TailwindCSS (& TailwindUI), through [django-tailwind](https://github.com/timonweb/django-tailwind). 

Local development
-----------------

Launch locally with with `docker-compose up`.

Start tailwind in dev mode:

`docker-compose run web python manage.py tailwind start`.

Deploying
---------

TBC.


Build production stylesheet:

`docker-compose run web python manage.py tailwind build`.
