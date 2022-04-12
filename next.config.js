/** @type {import('next').NextConfig} */

const { withSentryConfig } = require("@sentry/nextjs");
const { i18n } = require("./next-i18next.config");

const { FALLBACK_URL = "" } = process.env;

const config = {
  publicRuntimeConfig: {
    GRAPHQL_ENDPOINT: process.env.GRAPHQL_ENDPOINT,
    SENTRY_DSN: process.env.SENTRY_DSN,
    SENTRY_ENVIRONMENT: process.env.SENTRY_ENVIRONMENT,
  },

  poweredByHeader: false, // Disable 'x-powered-by' header
  reactStrictMode: true,
  trailingSlash: false,
  i18n,

  async rewrites() {
    return {
      // After checking all Next.js pages (including dynamic routes)...
      // ...and static files we proxy any other requests
      fallback: [
        // Proxied static files do not need to have a trailing slash
        {
          source: "/static/:path*",
          destination: `${FALLBACK_URL}/static/:path*`,
        },
        {
          source: "/:path*",
          destination: `${FALLBACK_URL}/:path*/`,
        },
      ],
    };
  },
};

const sentryWebpackPluginOptions = {
  // Additional config options for the Sentry Webpack plugin. Keep in mind that
  // the following options are set automatically, and overriding them is not
  // recommended:
  //   release, url, org, project, authToken, configFile, stripPrefix,
  //   urlPrefix, include, ignore

  silent: true, // Suppresses all logs
  dryRun: process.env.NODE_ENV !== "production" || Boolean(process.env.CI),
  // For all available options, see:
  // https://github.com/getsentry/sentry-webpack-plugin#options.
};

// Make sure adding Sentry options is the last code to run before exporting, to
// ensure that your source maps include changes from all other Webpack plugins
module.exports = withSentryConfig(config, sentryWebpackPluginOptions);
