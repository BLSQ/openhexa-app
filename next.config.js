/**
 * @type {import('next').NextConfig}
 */
const { withSentryConfig } = require("@sentry/nextjs");
const { i18n } = require("./next-i18next.config");

const config = {
  publicRuntimeConfig: {
    GRAPHQL_ENDPOINT: process.env.GRAPHQL_ENDPOINT,
    SENTRY_DSN: process.env.SENTRY_DSN,
    SENTRY_ENVIRONMENT: process.env.SENTRY_ENVIRONMENT,
  },

  async redirects() {
    return [
      {
        source: "/airflow/dag/:path*",
        destination: "/pipelines/:path*",
        permanent: false,
      },
    ];
  },

  sentry: {
    hideSourceMaps: true,
  },

  poweredByHeader: false, // Disable 'x-powered-by' header
  reactStrictMode: true,
  trailingSlash: false,
  i18n,
  swcMinify: true,
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
