<div align="center">
   <img alt="OpenHEXA Logo" src="https://raw.githubusercontent.com/BLSQ/openhexa-app/main/hexa/static/img/logo/logo_with_text_grey.svg" height="80">
</div>
<p align="center">
    <em>Open-source Data integration platform</em>
</p>
<p align="center">
   <a href="https://github.com/BLSQ/openhexa-frontend/actions/workflows/ci.yml">
      <img alt="Test Suite" src="https://github.com/BLSQ/openhexa-frontend/actions/workflows/ci.yml/badge.svg">
   </a>
</p>

# OpenHEXA Frontend Component

OpenHEXA is an open-source data integration platform developed by [Bluesquare](https://bluesquarehub.com).

Its goal is to facilitate data integration and analysis workflows, in particular in the context of public health
projects.

Please refer to the [OpenHEXA wiki](https://github.com/BLSQ/openhexa/wiki/Home) for more information about OpenHEXA.

The OpenHEXA `frontend` component is a [Next.js](https://Next.js.org/) application. It is a frontend app designed to
connect to an [OpenHEXA](https://github.com/BLSQ/openhexa-app) instance.

The app communicates with OpenHEXA through its [GraphQL](https://graphql.org/) API, and uses the standard OpenHEXA
cookie-based authentication.

## Docker image

OpenHEXA FrontEnd is published as a Docker Image on Docker Hub:
[blsq/openhexa-frontend](https://hub.docker.com/r/blsq/openhexa-frontend)

You can run the frontend component using the following command:

```bash
docker run --rm -p 3000:3000 blsq/openhexa-frontend
```

The server is then exposed at `http://localhost:3000`. However, it has to be
configured so that it can access the OpenHEXA backend (See [openhexa-app](https://github.com/BLSQ/openhexa-app)).

If you're looking something working out of the box for local development, go to the next section.

## Local development

The [Installation instructions](https://github.com/BLSQ/openhexa/wiki/Installation-instructions#development-installation)
section of our wiki gives an overview of the local development setup required to run OpenHEXA locally.

### Requirements

The Frontend component requires a recent (`v20` or newer) version of [Node.js](https://nodejs.org/).

We recommend using [`nvm`](https://github.com/nvm-sh/nvm) to manage multiple versions of Node.

If you use `nvm`, `npm` can be installed using the following command:

```bash
nvm install-latest-npm
```

### Getting started

Notice that contrary to openhexa-app or openhexa-notebook, the advised
environment for local development is not containers.

First, install the dependencies:

```bash
npm install
```

Then, copy `.env.local.dist` and adapt it to your needs:

```bash
cp .env.local.dist .env.local  # adapt the .env file with the required configuration values
```

Before starting the server, the backend ([openhexa-app](https://github.com/BLSQ/openhexa-app/))
should be up and running.

Finally, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see
the result. If you have followed the
[backend development setup instructions](https://github.com/BLSQ/openhexa-app/#local-development),
you should be able to log in with the listed credentials in those instructions:
`root@openhexa.org`/`root` (please [check](https://github.com/BLSQ/openhexa-app#local-development) if it hasn't
been updated).

### Configuration

The following environment variables should be provided at build time
(for the `npm run build`):

- `RELEASE`: a release identifier, such as a Git tag (used for uploading source maps to Sentry)
- `SENTRY_AUTH_TOKEN`: A valid Sentry authentication token

The following environment variables should be provided at run time:

- `OPENHEXA_BACKEND_URL`: the URL of the backend API (used by the nextjs server)
- `SENTRY_TRACES_SAMPLE_RATE`: the [Sentry](https://sentry.io/) sampling rate of traces
- `SENTRY_DSN`: the [Sentry](https://sentry.io/) DSN
- `SENTRY_ENVIRONMENT`: the [Sentry](https://sentry.io/) environment tag
- `DISABLE_ANALYTICS`: set to `true` to disable analytics tracking (only prevent the requests to be sent to the backend)
- `MAX_REQUEST_BODY_SIZE`: the maximum size of the request body. This is used when the backend is proxied by the frontend to upload files.

### Code style

We use ESLint (as provided by Next.js) and prettier to format our code.

Lint and format the code using the following command:

```bash
npm run lint && npm run format
```

## NPM Scripts

- `npm run dev`: Launch Next.js in dev mode and watch files to extract graphql code and generate typescript types and hooks
- `npm run next`: Launch only the Next.js app in dev mode
- `npm run build`: Build the Next.js app
- `npm run start`: Start the app from the build directory (it has to be built before)
- `npm run test`: Run the tests in watch mode
- `npm run test:ci`: Run all the tests in CI mode
- `npm run lint`: Lint files in `src/` using `eslint`
- `npm run format`: Format files in `src/` using `prettier`
- `npm run prepare`: This script is called automatically by npm on `npm install`. It adds the pre-commit hook
- `npm run schema`: Run an introspection query on the graphql backend and generate a `schema.graphql` file. This file is used to generate typescript types & for DX in the IDE
- `npm run codegen`: Generate typescript types found in all the files based on `schema.graphql`
- `npm run i18n:extract`: Extract translatable strings and write `messages.json` files for each language
- `npm run i18n:translate` Translate the `messages.json` files using DeepL (requires a DeepL API key `DEEPL_API_KEY` to be set).

## Internationalization

To extract new strings from the `src/` directory, run the extract command:

```bash
npm run i18n:extract
```

Translations are stored in `public/locales/[lang]/[ns].json`.

To translate the strings using DeepL, run the translate command:

```bash
npm run i18n:translate fr # translate to French
```

or

```bash
npm run i18n:translate fr --overwrite # translate to French and overwrite all the strings
```

You can validate that all the strings are translated using the following command:

```bash
npm run i18n:validate
```

## Versioning

This library follows [Semantic Versioning](http://semver.org/).
Tagging and releases' creation are managed by [release-please](https://github.com/googleapis/release-please) that will create and maintain a pull request with
the next release based on the [commit messages of the new commits](#how-should-i-write-my-commits).

Triggering a new release is done by merging the pull request created by release-please. The result is:

- the version in package.json is bumped
- the changelog.md is updated with the commit messages
- a GitHub release is created
- a docker image is built for the new tag and pushed on the docker registry


### Release Branches

Release-please also run on release branches named `release/*` (ex: release/0.81) for maintaining older versions. When working on a release branch:

1. The same conventional commit format should be used
2. Release-please will create and maintain a PR for the next patch version on that branch
3. Changes can be cherry-picked or implemented directly on the release branch
4. Merging the PR created by release-please will trigger a new patch release for that version

This approach allows us to maintain multiple versions simultaneously while ensuring proper semantic versioning for each release line.


## How should I write my commits?

This project assumes you are using [Conventional Commit messages](https://www.conventionalcommits.org/).

The most important prefixes you should have in mind are:

- `fix:` which represents bug fixes, and correlates to a [SemVer](https://semver.org/)
  patch.
- `feat:` which represents a new feature, and correlates to a SemVer minor.
- `feat!:`, or `fix!:`, `refactor!:`, etc., which represent a breaking change
  (indicated by the `!`) and will result in a SemVer major.
