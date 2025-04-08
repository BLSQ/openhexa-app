# OpenHEXA Frontend

## Requirements

The Frontend component requires a recent (`v20` or newer) version of [Node.js](https://nodejs.org/).

We recommend using [`nvm`](https://github.com/nvm-sh/nvm) to manage multiple versions of Node.

If you use `nvm`, `npm` can be installed using the following command:

```bash
nvm install-latest-npm
```

## Getting started

Copy the `.env.dist` file to `.env` from the root directory and adapt it to your needs then run the following command:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the app.

## Frontend configuration

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

# NPM Scripts

- `npm run dev`: Launch Next.js in dev mode and watch files to extract graphql code and generate typescript types and hooks
- `npm run next`: Launch only the Next.js app in dev mode
- `npm run build`: Build the Next.js app
- `npm run start`: Start the app from the build directory (it has to be built before)
- `npm run test`: Run the tests in watch mode
- `npm run test:ci`: Run all the tests in CI mode
- `npm run lint`: Lint files in `src/` using `eslint`
- `npm run format`: Format files in `src/` using `prettier`
- `npm run prepare`: This script is called automatically by npm on `npm install`. It adds the pre-commit hook
- `npm run codegen`: Generate typescript types found in all the files based on `schema.graphql`
- `npm run i18n:extract`: Extract translatable strings and write `messages.json` files for each language
- `npm run i18n:translate` Translate the `messages.json` files using DeepL (requires a DeepL API key `DEEPL_API_KEY` to be set).