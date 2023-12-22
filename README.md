<div align="center">
   <img alt="OpenHexa Logo" src="https://raw.githubusercontent.com/BLSQ/openhexa-app/main/hexa/static/img/logo/logo_with_text_grey.svg" height="80">
</div>
<p align="center">
    <em>Open-source Data integration platform</em>
</p>
<p align="center">
   <a href="https://github.com/BLSQ/openhexa-app/actions/workflows/test.yml">
      <img alt="Test Suite" src="https://github.com/BLSQ/openhexa-app/actions/workflows/test.yml/badge.svg">
   </a>
</p>

OpenHexa App Component
======================

OpenHexa is an open-source data integration platform developed by [Bluesquare](https://bluesquarehub.com).

Its goal is to facilitate data integration and analysis workflows, in particular in the context of public health 
projects.

Please refer to the [OpenHexa wiki](https://github.com/BLSQ/openhexa/wiki/Home) for more information about OpenHexa.

This repository contains the code for what we call the `app` component, which mostly offers a GraphQL API and an 
infrastructure to run data pipelines.

For more information about the technical aspects of OpenHexa, you might be interested in the two following wiki pages:

- [Installing OpenHexa](https://github.com/BLSQ/openhexa/wiki/Installation-instructions)
- [Technical Overview](https://github.com/BLSQ/openhexa/wiki/Technical-overview)

Container
---------

OpenHexa App is published as a Docker Image on Docker Hub:
[blsq/openhexa-app](https://hub.docker.com/r/blsq/openhexa-app).

You can run a simple interactive bash session as it follows:

```bash
docker run --rm -ti blsq/openhexa-app bash
```

Other commands are available:

```
  Available commands:

  start             : start django server using gunicorn
  makemigrations    : generate a django migration
  migrate           : run django migrations
  test              : launch django tests
  manage            : run django manage.py
  fixtures          : migrate, create superuser, load fixtures and reindex
  bash              : run bash
  coveraged-test    : launch django tests and show a coverage report

  Any arguments passed will be forwarded to the executed command
```

If you run the Django server, it will look for a database server. If you need
something working out of the box for local development, go to the next section.

Local development
-----------------

To ease the setup of the environment and management of dependencies, we are using containerization, in particular
Docker. As such, we provide a `docker-compose.yaml` file for local development. When running it, the present code base
is mounted inside the container. That means that the changes are reflected directly in the container environment
allowing you to develop.

The following steps will get you up and running:

```bash
cp .env.dist .env
docker network create openhexa
docker compose build
docker compose run app fixtures
docker compose up
```

This will correctly configure all the environment variables, fill the database with some initial data and start the base
`db` and `app` services. The app is then exposed on `localhost:8000`. Two main paths are available:

- http://localhost:8000/graphql for the GraphQL API
- http://localhost:8000/ready for the readiness endpoint 

Anything else will be redirected to the frontend served at `http://localhost:3000`.

You can then log in with the following credentials: `root@openhexa.org`/`root`

Python requirements are handled with [pip-tools](https://github.com/jazzband/pip-tools), you will need to install it.
When you want to add a requirement, simply update `requirements.in` and run `pip-compile` in the root directory. You
can then rebuild the Docker image.

### Pipelines

If you need the pipelines or want to work on them, there are 2 optional services to run: `pipelines_runner` and/or
`pipelines_scheduler`. You can run them with the following command **instead of** `docker compose up`:

```bash
docker compose --profile pipelines up
```

As for the backend, the code base is mounted inside the container. That means that the changes are reflected directly in
the container environment allowing you to develop.

When it's up and running, you can submit a pipeline. For that, you can follow the [README of the OpenHexa SDK Python]
(https://github.com/BLSQ/openhexa-sdk-python/blob/main/README.md#quickstart). It will help you to scaffold your first
OpenHexa pipeline project and submit it.

Before submitting a pipeline, you need to make sure the next steps:

1. create a workspace on your local instance `http://localhost:3000/workspaces/`, this will provide you a workspace name
   and token,
2. [configure the URL of the backend API] (https://github.com/BLSQ/openhexa-sdk-python/blob/main/README.md#using-a-local-installation-of-the-openhexa-backend-to-run-pipelines)
   used by your pipeline project:
   ```bash
   openhexa config set_url http://localhost:8000
   ```

When it's done, you can push your pipeline to your local instance.

### Data worker

If you need the optional services `dataworker`, you can run the following command **instead of** `docker compose up`:

```bash
docker compose --profile dataworker up 
```

### Running commands on the container

The app Docker image contains an entrypoint. You can use the following to list the available commands:

```bash
docker compose run app help
```

As an example, use the following command to run the migrations:

```bash
docker compose run app migrate
```

### Running the tests

Running the tests is as simple as:

```bash
docker compose run app test
```

Some tests call external resources (such as the public DHIS2 API) and will slow down the suite. You can exclude them
when running the test suite for unrelated parts of the codebase:

```bash
docker compose run app test --exclude-tag=external
```

You can run a specific test as it follows:

```bash
docker compose run app test hexa.core.tests.CoreTest.test_ready_200
```

There are many other options, if you want to find out more, look at the [documentation of Django test harness](https://docs.djangoproject.com/en/4.2/topics/testing/overview/#running-tests),
as it is what we are using.

### Code style

Our python code is linted using [`black`](https://github.com/psf/black), [`isort`](https://github.com/PyCQA/isort) and [`autoflake`](https://github.com/myint/autoflake).
We currently target the Python 3.9 syntax.

We use a [pre-commit](https://pre-commit.com/) hook to lint the code before committing. Make sure that `pre-commit` is
installed, and run `pre-commit install` the first time you check out the code. Linting will again be checked
when submitting a pull request.

You can run the lint tools manually using `pre-commit run --all`.

## Versioning

This library follows [Semantic Versioning](http://semver.org/).
Tagging and releases' creation are managed by [release-please](https://github.com/googleapis/release-please) that will create and maintain a pull request with 
the next release based on the [commit messages of the new commits](#how-should-i-write-my-commits).

Triggering a new release is done by merging the pull request created by release-please. The result is:
* the changelog.md is updated with the commit messages
* a GitHub release is created
* a docker image is built for the new tag and pushed on the docker registry

## How should I write my commits?

This project assumes you are using [Conventional Commit messages](https://www.conventionalcommits.org/).

The most important prefixes you should have in mind are:

* `fix:` which represents bug fixes, and correlates to a [SemVer](https://semver.org/)
  patch.
* `feat:` which represents a new feature, and correlates to a SemVer minor.
* `feat!:`,  or `fix!:`, `refactor!:`, etc., which represent a breaking change
  (indicated by the `!`) and will result in a SemVer major.

### Two-factor authentication

The two-factor authentication implemented in OpenHexa is optional and can be enabled per user.

In order to enable the two-factor authentication you need to create a `Feature` with the code `two_factor`.
You can then link this `Feature` to specific users by creating the corresponding `FeatureFlag` of by setting 
`force_activate` on the `Feature` to `True` to enable it for everyone.