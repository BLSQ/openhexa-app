/** @type {import('next').NextConfig} */

const { withSentryConfig } = require("@sentry/nextjs");
const { i18n } = require("./next-i18next.config");

const config = {
  reactStrictMode: true,
  i18n,
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
