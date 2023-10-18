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

Its goal is to facilitate data integration and analysis workflows, in particular in the context of public health projects.

Please refer to the [OpenHexa wiki](https://github.com/BLSQ/openhexa/wiki/Home) for more information, about OpenHexa.

This repository contains the code for what we call the `app` component, which mostly offers a GraphQL API and an 
infrastructure to run data pipelines.

For more information about the technical aspects of OpenHexa, you might be interested in the two following wiki pages:

- [Installing OpenHexa](https://github.com/BLSQ/openhexa/wiki/Installation-instructions)
- [Technical Overview](https://github.com/BLSQ/openhexa/wiki/Technical-overview)

Local development
-----------------

To ease the setup of the environment and management of dependencies, we are  using containerization, in particular 
Docker. As such, we provide a `docker-compose.yaml` file for local development. When running it, the present code base 
is mounted inside the container. That means that the changes are reflected directly in the container environment 
allowing you to develop.

The following steps will get you up and running:

```bash
cp .env.dist .env
docker network create openhexa
docker compose build
docker compose run app fixtures
docker compose run app manage tailwind install
docker compose run app manage tailwind build
docker compose up
```

This will correctly configure all the environment variables, fill the database with some initial data and start the 
base `db` and `app` services. The app is then exposed on `localhost:8000`. Two main paths are available:

- http://localhost:8000/graphql for the GraphQL API
- http://localhost:8000/ready for the readiness endpoint 

Anything else will be redirected to the frontend served at `http://localhost:3000`.

If you need the optional services `dataworker`, `pipelines_runner` & `pipelines_scheduler`, you can run the following 
command **instead of** `docker compose up`:

```bash
docker compose --profile pipelines --profile dataworker up 
```

You can then log in with the following credentials: `root@openhexa.org`/`root`

Python requirements are handled with [pip-tools](https://github.com/jazzband/pip-tools), you will need to install it. 
When you want to add a requirement, simply update `requirements.in` and run `pip-compile` in the root directory. You 
can then rebuild the Docker image.

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

There are many other options, if you want to find out more, look at the
[documentation of Django test harness](https://docs.djangoproject.com/en/4.2/topics/testing/overview/#running-tests),
as it is what we are using.

Test coverage is evaluated using the [`coverage`](https://github.com/nedbat/coveragepy) library:

```bash
docker compose run app coveraged-test
```

If you have the .coverage generated, you can also create HTML report from the
container:

```bash
docker compose run app bash
coverage html
```

The reports are put into the directory `htmlcov`. You might need to change the
ownership of those files to get access to them.

### Code style

Our python code is linted using [`black`](https://github.com/psf/black), [`isort`](https://github.com/PyCQA/isort) and [`autoflake`](https://github.com/myint/autoflake).
We currently target the Python 3.9 syntax.

We use a [pre-commit](https://pre-commit.com/) hook to lint the code before committing. Make sure that `pre-commit` is
installed, and run `pre-commit install` the first time you check out the code. Linting will again be checked
when submitting a pull request.

You can run the lint tools manually using `pre-commit run --all`.

OpenHexa uses [TailwindUI](https://tailwindui.com/), [TailwindCSS](https://tailwindcss.com/)
and [Heroicons](https://heroicons.com/) for the user interface.


### Two-factor authentication

The two-factor authentication implemented in OpenHexa is optional and can be enabled per user.

In order to enable the two-factor authentication you need to create a `Feature` with the code `two_factor`.
You can then link this `Feature` to specific users by creating the corresponding `FeatureFlag` of by setting 
`force_activate` on the `Feature` to `True` to enable it for everyone.