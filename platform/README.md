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

This Django application can be deployed on any server that supports Python. The `k8s` directory contains a sample 
Kubernetes deployment config.

The platform docker image can be built using the "Build Platform image" Github workflow.

Don't forget to build the production stylesheet before rebuilding your image:

`docker-compose run web python manage.py tailwind build`.