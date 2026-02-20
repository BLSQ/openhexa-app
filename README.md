<div align="center">
   <img alt="OpenHEXA Logo" src="https://raw.githubusercontent.com/BLSQ/openhexa-app/main/backend/hexa/static/img/logo/logo_with_text_black.svg" height="80">
</div>
<p align="center">
    <em>Open-source Data integration platform</em>
</p>

OpenHEXA is an open-source data integration platform developed by [Bluesquare](https://bluesquarehub.com).

Its goal is to facilitate data integration and analysis workflows, in particular in the context of public health
projects.

Please refer to the [OpenHEXA wiki](https://github.com/BLSQ/openhexa/wiki/Home) for more information about OpenHEXA.

This repository contains the code of the following components:
 - The `backend` component, which mostly offers a GraphQL API and an infrastructure to run data pipelines.
 - The `frontend` component, which is a NextJS application that allows you to interact with the OpenHEXA platform.

Other components are available in separate repositories:
  - [openhexa-docker-images](https://github.com/BLSQ/openhexa-docker-images): Docker images used for the pipelines & Jupyterlab environments.
  - [openhexa-sdk-python](https://github.com/BLSQ/openhexa-sdk-python): Python SDK used to build data pipelines.
  - [openhexa-toolbox](https://github.com/BLSQ/openhexa-toolbox): A set of tools to interact with common third parties ([IASO](https://github.com/BLSQ/iaso), [DHIS2](https://github.com/dhis2), ...)
  - [openhexa](https://github.com/BLSQ/openhexa): The main repository that gathers all the documentation, the wiki and the debian package of OpenHEXA.

# Changelog

For details please refer to the [CHANGELOG.md](CHANGELOG.md) file.

You can also refer to the [backend](backend/README.md) & [frontend](frontend/README.md) README files for more details on versions prior to v1.0.2.

# Release workflow

This project follows [Semantic Versioning](http://semver.org/).
Tagging and releases' creation are managed by [release-please](https://github.com/googleapis/release-please) that will create and maintain a pull request with
the next release based on the [commit messages of the new commits](#how-should-i-write-my-commits).

On creation of a new release, the following actions are performed:
  - The changelog is updated with the new changes.
  - The version in the `pyproject.toml` file is updated.
  - The version in the `package.json` file is updated.
  - A new release is created in GitHub.
  - Docker images are built and pushed to Docker Hub: [blsq/openhexa-app](https://hub.docker.com/r/blsq/openhexa-app) & [blsq/openhexa-frontend](https://hub.docker.com/r/blsq/openhexa-frontend).

This process can also run on release branches named `release/*` (ex: release/0.81) for maintaining older versions. When working on a release branch:

1. Create a new release branch from the related version `git checkout -b release/0.81 0.81.1`
2. The same conventional commit format should be used
3. Release-please will create and maintain a PR for the next patch version on that branch
4. Changes can be cherry-picked or implemented directly on the release branch
5. Merging the PR created by release-please will trigger a new patch release for that version

This approach allows us to maintain multiple versions simultaneously while ensuring proper semantic versioning for each release line.

## Code style

Our backend code is linted using [`ruff`](https://docs.astral.sh/ruff/). It also handles code formatting, and import sorting.

We currently target the Python 3.13 syntax.

We use a [pre-commit](https://pre-commit.com/) hook to lint the code before committing. Make sure that `pre-commit` is
installed, and run `pre-commit install` the first time you check out the code. Linting will again be checked
when submitting a pull request.

You can run the lint tools manually using `pre-commit run --all`.

Our frontend code is linted using [`eslint`](https://eslint.org/) as provided by Next.js.

Lint and format the code using the following command:

```bash
npm run lint && npm run format
```

# Getting started

The [Installation instructions](https://github.com/BLSQ/openhexa/wiki/Installation-instructions#development-installation)
section of our wiki gives an overview of the local development setup required to run OpenHEXA locally.

To ease the setup of the environment and management of dependencies, we are using containerization, in particular
[Docker](https://www.docker.com/). As such, we provide a `docker-compose.yaml` file for local development.

## Backend

When running the backend component using `docker compose`, the code of this repository is mounted as a volume within the
container, so that any change you make in your local copy of the codebase is directly reflected in the running
container.

1. Prepare the `.env` :
    ```sh
       cp .env.dist .env
       # Set WORKSPACE_STORAGE_LOCATION to a local directory to use a local storage backend for workspaces (ex: /Users/yolanfery/Desktop/data/openhexa)
       # Set the OPENHEXA_BACKEND_URL to the URL of the backend (ex: http://localhost:8000)
     ```
2. Navigate to the backend directory:
    ```sh
    cd backend
    ```
3. Run the backend server:
   ```sh
   docker network create openhexa
   docker compose build
   docker compose run app fixtures
   docker compose up
   ```

### Python requirements

Python requirements are handled with [pip-tools](https://github.com/jazzband/pip-tools), you will need to install it.

We use `pip-tools` since it allows us to lock down the versions of all of the packages that our Python code depends on in the `requirements.txt` file. We want this file to include versions for not just the direct dependencies, but also versions for all of the transitive dependencies as well, that is, the versions of modules that our directly dependent modules themselves depend on.

For this reason, **instead of updating `requirements.txt` directly, we update `requirements.in`**.
Then you run in the root directory:

```sh
pip-compile --no-emit-index-url requirements.in
```

You can then rebuild the Docker image.

## Frontend

1. Prepare the `.env` :
    ```sh
       cp .env.dist .env
       # Set WORKSPACE_STORAGE_LOCATION to a local directory to use a local storage backend for workspaces (ex: /Users/yolanfery/Desktop/data/openhexa)
       # Set the OPENHEXA_BACKEND_URL to the URL of the backend (ex: http://localhost:8000)
     ```
2. Navigate to the frontend directory:
    ```sh
    cd frontend
    ```
3. Install the required Node.js dependencies:
    ```sh
    npm install
    ```
4. Run the frontend development server:
    ```sh
    npm run dev
    ```

This will correctly configure all the environment variables, fill the database with some initial data and start the base
`db` and `app` services. The app is then exposed on `localhost:8000`. Two main paths are available:

- http://localhost:8000/graphql for the GraphQL API
- http://localhost:8000/ready for the readiness endpoint

Anything else will be redirected to the frontend served at `http://localhost:3000`.

You can then log in with the following credentials: `root@openhexa.org`/`root`


## Backend & Frontend

You can run the frontend along with the backend in a single command :
```sh
  docker compose --profile frontend up
```

## Pipelines

If you need the pipelines or want to work on them, there are 2 optional services to run: `pipelines_runner` and/or
`pipelines_scheduler`. You can run them with the following command **instead of** `docker compose up`:

```bash
docker compose --profile pipelines up
```

The [Writing OpenHEXA pipelines](https://github.com/BLSQ/openhexa/wiki/Writing-OpenHexa-pipelines) section of the wiki
contains the instructions needed to build and deploy a data pipeline on OpenHEXA.

To deploy and run data pipelines locally, you will need to:

1. Create a workspace on your local instance
2. Configure the SDK to use your local instance as the backend

```bash
openhexa config set_url http://localhost:8000
```

You can now deploy your pipelines to your local OpenHEXA instance.

Please refer to the [SDK documentation](https://github.com/BLSQ/openhexa-sdk-python/blob/main/README.md#using-a-local-installation-of-openhexa-to-run-pipelines)
for more information.

### Testing with Docker Desktop Kubernetes

By default, pipelines run using Docker spawner. If you want to test the Kubernetes spawner locally using Docker Desktop's built-in Kubernetes cluster:

1. **Enable Kubernetes in Docker Desktop**:
   - Open Docker Desktop settings
   - Go to "Kubernetes" section
   - Check "Enable Kubernetes"
   - Click "Apply & Restart"

2. **Update your `.env` file**:
   ```bash
   PIPELINE_SCHEDULER_SPAWNER=kubernetes
   INTERNAL_BASE_URL=http://host.docker.internal:8000
   ```

3. **Restart the pipelines services**:
   ```bash
   docker compose --profile pipelines down
   docker compose --profile pipelines up
   ```

The `pipelines_runner` service is already configured to work with Docker Desktop Kubernetes. It will:
- Automatically detect local development mode via `IS_LOCAL_DEV=true`
- Mount your `~/.kube` config for cluster access
- Patch the kubeconfig to use `host.docker.internal` for communication between pods and services
- Skip production-specific requirements (node affinity, tolerations, FUSE devices)
- Use `IfNotPresent` image pull policy to leverage local images

## Dataset worker
Generation of file samples and metadata calculation are done in separate worker, in order to run it locally you
can make use of `dataset_worker` by adding `dataset_worker` profile to the list of enabed profiles.

````
docker compose --profile dataset_worker up
````

## Running commands on the container

The app Docker image contains an entrypoint. You can use the following to list the available commands:

```bash
docker compose run app help
```

As an example, use the following command to run the migrations:

```bash
docker compose run app migrate
```

## Analytics
We use [Mixpanel](https://mixpanel.com/home/) to track users and their actions. If you want to enable it, set the `MIXPANEL_TOKEN` environment variable with the token from your Mixpanel project and restart the application.


## Debugging

If you want to run the backend app in debugger mode, you can override the default command to execute by adding a
`docker-compose.debug.yaml` file in order to use the your favorite debugger package and wait for a debugger to attach.

### Using `debugpy` for **VSCode**

```yaml
# docker-compose.debug.yaml

services:
  app:
    entrypoint: []
    command:
      - "sh"
      - "-c"
      # If you want to wait for the debugger client to be attached before running the server
      # - |
      #   pip install debugpy \
      #   && python -m debugpy --listen 0.0.0.0:5678 --wait-for-client /code/manage.py runserver 0.0.0.0:8000
      - |
        pip install debugpy \
        && python -m debugpy --listen 0.0.0.0:5678 /code/manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
      - "5678:5678"
```

You can then add a new configuration in VSCode to run the app in debugger mode:


```json
# .vscode/launch.json

{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach OpenHEXA Debugger",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/code"
                }
            ],
            "django": true,
            "justMyCode": false
        }
    ]
}
```
Run the app with `docker compose -f docker-compose.yaml -f docker-compose.debug.yaml up` & start the debugger from VSCode.

### Using **Pycharm**

```yaml
# docker-compose.debug.yaml

services:
  app:
    entrypoint: []
    # Used when running in normal mode.
    command: ["/code/docker-entrypoint.sh", "manage", "runserver", "0.0.0.0:8000"]
    ports:
      - "8000:8000"
```

Create a new interpreter configuration in Pycharm with the following settings:

![Pycharm Interpreter Configuration](docs/images/pycharm-interpreter-configuration.png)

Create a new django server run configuration by setting the following options:
- Python interpreter: The one you just created
- In "Docker Compose" section; Command and options: `-f docker-compose.yaml -f docker-compose.debug.yaml up`

Run the configuration in debug mode.

### PgAdmin as dev tool

For development purposes, you can define a pgAdmin service as Docker container. In this example, let's say in *docker-compose.dev.yaml*.

```yaml
# docker-compose.dev.yaml

services:
  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_DEFAULT_EMAIL:-root@openhexa.org}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_DEFAULT_PASSWORD:-root}
      PGADMIN_CONFIG_SERVER_MODE: "False"
      PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED: "False"
    ports:
      - "${PGADMIN_PORT:-5050}:80"
    depends_on:
      - db
    networks:
      - openhexa
    volumes:
      - pgadmin_data:/var/lib/pgadmin4

volumes:
  pgadmin_data:
```

Next run the following command:

```bash
docker compose -f docker-compose.yaml -f docker-compose.dev.yaml [-f docker-compose.debug.yaml] up
```

In the browser, go to http://localhost:5050 and log in using credentials defined in the *docker-compose.dev.yaml* file.

![PgAdmin dev tool](docs/images/pg-admin-dashboard.png)

Finally create a new connection to the server:

![PgAdmin dev tool](docs/images/pg-admin-server-setup-1.png)

![PgAdmin dev tool](docs/images/pg-admin-server-setup-2.png)

The address of the server must be the one of the database container gateway, on the 5434 port.

## Running the tests

### Backend
Use the following command to run the backend tests:

```bash
docker compose --profile test run app test
```

Some tests call external resources (such as the public DHIS2 API) and will slow down the suite. You can exclude them
when running the test suite for unrelated parts of the codebase:

```bash
docker compose --profile test run app test --exclude-tag=external
```

You can run a specific test as it follows:

```bash
docker compose --profile test run app test hexa.core.tests.CoreTest.test_ready_200
```

Adding the `--profile test` will launch optional services that are needed for the tests to run (e.g. `azurite` to test the Azure storage backend).

If you're running tests directly inside the container with `./manage.py`, you'll need to specify the settings explicitly and ensure the test services (like `azurite`) are running:

```bash
docker compose --profile test up -d azurite
python manage.py test --settings=config.settings.test
```

There are many other options, if you want to find out more, look at the [documentation of Django test harness](https://docs.djangoproject.com/en/4.2/topics/testing/overview/#running-tests),
as it is what we are using.


### Frontend

Jest is used for the frontend tests.

```bash
cd frontend
npm run test
```


### I18N

## Backend
You can extract the strings to translate with the following command:

```bash
docker compose run app manage makemessages -l fr # Where fr is the language code
```

You can then translate the strings in the `hexa/locale` folder.

To compile the translations, run the following command:

```bash
docker compose run app manage compilemessages
```


## Frontend

Translations are stored in `frontend/public/locales/[lang]/[ns].json`.
To extract new strings from the `frontend/src/` directory, run the extract command:

```bash
cd frontend
npm run i18n:extract
```

To translate the strings using DeepL, run the translate command after setting the `DEEPL_API_KEY` environment variable:

```bash
npm run i18n:translate fr # translate to French
# OR
npm run i18n:translate fr --overwrite # translate to French and overwrite all the strings
```

You can validate that all the strings are translated using the following command:

```bash
npm run i18n:validate
```

# License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.

# FAQ

## How should I write my commits?

This project assumes you are using [Conventional Commit messages](https://www.conventionalcommits.org/).

The most important prefixes you should have in mind are:

- `fix:` which represents bug fixes, and correlates to a [SemVer](https://semver.org/)
  patch.
- `feat:` which represents a new feature, and correlates to a SemVer minor.
- `feat!:`, or `fix!:`, `refactor!:`, etc., which represent a breaking change
  (indicated by the `!`) and will result in a SemVer major.
