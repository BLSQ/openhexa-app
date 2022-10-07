<div align="center">
   <img alt="OpenHexa Logo" src="https://raw.githubusercontent.com/BLSQ/openhexa-app/main/hexa/static/img/logo/logo_with_text_grey.svg" height="80">
</div>
<p align="center">
    <em>Open-source Data integration platform</em>
</p>
<!--<p align="center">
   <a href="https://github.com/BLSQ/openhexa-app/actions/workflows/test.yml">
      <img alt="Test Suite" src="https://github.com/BLSQ/openhexa-frontend/actions/workflows/test.yml/badge.svg">
   </a>
</p>-->

# OpenHexa Frontend Component

OpenHexa is an **open-source data integration platform** that allows users to:

- Explore data coming from a variety of sources in a **data catalog**
- Schedule **data pipelines** for extraction & transformation operations
- Perform data analysis in **notebooks**
- Create rich data **visualizations**

<div align="center">
   <img alt="OpenHexa Screenshot" src="https://test.openhexa.org/img/screenshot_catalog.png" hspace="10" height="150">
   <img alt="OpenHexa Screenshot" src="https://test.openhexa.org/img/screenshot_notebook.png" hspace="10" height="150">
</div>

OpenHexa is an open-source product built by [Bluesquare](https://bluesquarehub.com) and released under the MIT license.

## OpenHexa architecture

The OpenHexa platform is composed of **four main components**:

- The [**App component**](https://github.com/BLSQ/openhexa-app) (soon to be renamed Backend), a
  [Django](https://djangoproject.com) application that provides the business logic and a GraphQLAPI
- The [**Frontend component**](https://github.com/BLSQ/openhexa-frontend), a [Next.js](https://nextjs.org/)
  application that the user-facing interface
- The [**Notebooks component**](https://github.com/BLSQ/openhexa-notebooks) (a customized
  [JupyterHub](https://jupyter.org/hub) setup)
- The [**Data Pipelines component**](https://github.com/BLSQ/openhexa-pipelines), a series of containerized data
  pipelines that are meant to be deployed in an [Airflow](https://airflow.apache.org/) cluster

This repository contains the code for the **Frontend component**, which serves as the user-facing part of the OpenHexa
stack.

## Frontend component overview

The OpenHexa frontend component is a [Next.js](https://nextjs.org/) application. It is a frontend app designed to
connect to an [OpenHexa](https://github.com/BLSQ/openhexa-app) instance.

The app communicates with OpenHexa through its [GraphQL](https://graphql.org/) API, and uses the standard OpenHexa
cookie-based authentication.

## Local development

### Getting started

First, install the dependencies:

```bash
npm install
```

Then, copy `.env.local.dist` and adapt it to your needs:

```bash
cp .env.local.dist .env.local
nano .env.local
```

Finally, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Code style

We use ESLint (as provided by NextJS) and prettier to format our code.

Lint and format the code using the following command:

```bash
npm run lint && npm run format
```

### Component library

We use [Ladle](https://ladle.dev/) to develop our component library.

Ladle offers a web interface that allows developers to browse and test individual components and their parameters.

You can run Ladle and open its web interface using `npm run ladle`.

## NPM Scripts

* `npm run dev`: Launch Nextjs in dev mode and watch files to extract graphql code and generate typescript types and hooks
* `npm run next`: Launch only the Nextjs app in dev mode
* `npm run build`: Build the Nextjs app
* `npm run start`: Start the app from the build directory (it has to be built before) 
* `npm run test`: Run the tests in watch mode
* `npm run test:ci`: Run all the tests in CI mode
* `npm run lint`: Lint files in `src/` using `eslint`
* `npm run format`: Format files in `src/` using `prettier`
* `npm run prepare`: This script is called automatically by npm on `npm install`. It adds the pre-commit hook
* `npm run schema`: Run an introspection query on the graphql backend and generate a `schema.graphql` file. This file is used to generate typescript types & for DX in the IDE
* `npm run codegen`: Generate typescript types found in all the files based on `schema.graphql`
* `npm run i18n:extract`: Extract translatable strings and write `messages.json` files for each language


## Internationalization

To extract new strings from the `src/` directory, run the extract command:

```bash
npm run i18n:extract
```

Translations are stored in `public/locales/[lang]/[ns].json`.

## Versioning

This library follows [Semantic Versioning](http://semver.org/).
Tagging and releases' creation are managed by [release-please](https://github.com/googleapis/release-please) that will create and maintain a pull request with the next release based on the [commit messages of the new commits](#how-should-i-write-my-commits).


Triggering a new release is done by merging the pull request created by release-please. The result is:
* the version in package.json is bumped
* the changelog.md is updated with the commit messages
* a github release is created
* a docker image is built for the new tag and pushed on the docker registry


## How should I write my commits?

This project assumes you are using [Conventional Commit messages](https://www.conventionalcommits.org/).

The most important prefixes you should have in mind are:

* `fix:` which represents bug fixes, and correlates to a [SemVer](https://semver.org/)
  patch.
* `feat:` which represents a new feature, and correlates to a SemVer minor.
* `feat!:`,  or `fix!:`, `refactor!:`, etc., which represent a breaking change
  (indicated by the `!`) and will result in a SemVer major.


## Deployment

The project is meant to be deployed in a containerized environment, such as [Kubernetes](https://kubernetes.io/).

The following environment variables should be provided at build time (for the `docker build` or `npm run build`):

- `RELEASE`: a release identifier, such as a Git tag (used for uploading source maps to Sentry)
- `SENTRY_AUTH_TOKEN`: A valid Sentry authentication token

The following environment variables should be provided at run time:
- `FALLBACK_URL`: the URL the traffic will be redirected to if NextJS cannot answer the request
- `GRAPHQL_ENDPOINT`: the URL of the OpenHexa GraphQL API
- `SENTRY_TRACES_SAMPLE_RATE`: the [Sentry](https://sentry.io/) sampling rate of traces
- `SENTRY_DSN`: the [Sentry](https://sentry.io/) DSN
- `SENTRY_ENVIRONMENT`: the [Sentry](https://sentry.io/) environment tag
