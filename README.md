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

## Internationalization

To extract new strings from the `src/` directory, run the extract command:

```bash
npm run i18n:extract
```

Translations are stored in `public/locales/[lang]/[ns].json`.


## Deployment

The project is meant to be deployed in a containerized environment, such as [Kubernetes](https://kubernetes.io/).

The following environment variables should be provided at build time (for the `docker build` or `npm run build`):

- `RELEASE`: a release identifier, such as a Git tag (used for uploading source maps to Sentry)
- `SENTRY_AUTH_TOKEN`: A valid Sentry authentication token

The following environment variables should be provided at run time:
- `FALLBACK_URL`: the URL the traffic will be redirected to if NextJS cannot answer the request
- `GRAPHQL_ENDPOINT`: the URL of the OpenHexa GraphQL API
- `SENTRY_DSN`: the [Sentry](https://sentry.io/) DSN
- `SENTRY_ENVIRONMENT`: the [Sentry](https://sentry.io/) environment tag


## Local development

First, install the dependencies

```bash
npm install
# or
yarn
```

Then, copy the sample `.env.local.dist` and adapt it to your needs:

```bash
cp .env.local.dist .env.local
```

Finally, run the development server:

```bash
npm run watch
# or
yarn watch
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.