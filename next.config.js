/**
 * @type {import('next').NextConfig}
 */
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

const { withSentryConfig } = require("@sentry/nextjs");
const { i18n } = require("./next-i18next.config");

const config = {
  experimental: {
    optimizePackageImports: ["next-i18next", "luxon"],
  },
  publicRuntimeConfig: {
    GRAPHQL_ENDPOINT: process.env.GRAPHQL_ENDPOINT,
    SENTRY_TRACES_SAMPLE_RATE: process.env.SENTRY_TRACES_SAMPLE_RATE
      ? parseFloat(process.env.SENTRY_TRACES_SAMPLE_RATE)
      : 1,
    SENTRY_DSN: process.env.SENTRY_DSN,
    SENTRY_ENVIRONMENT: process.env.SENTRY_ENVIRONMENT,
  },

  // Sentry tree shaking configuration
  webpack: (config, { webpack }) => {
    config.plugins.push(
      new webpack.DefinePlugin({
        __SENTRY_DEBUG__: false,
        __SENTRY_TRACING__: false,
        __RRWEB_EXCLUDE_IFRAME__: true,
        __RRWEB_EXCLUDE_SHADOW_DOM__: true,
        __SENTRY_EXCLUDE_REPLAY_WORKER__: true,
      }),
    );

    // return the modified config
    return config;
  },

  async redirects() {
    return [
      {
        source: "/airflow/dag/:path*",
        destination: "/pipelines/:path*",
        permanent: false,
      },
      {
        source: "/",
        destination: "/workspaces",
        permanent: false,
      },
    ];
  },

  sentry: {
    hideSourceMaps: true,
  },

  poweredByHeader: false, // Disable 'x-powered-by' header
  reactStrictMode: true,
  trailingSlash: true,
  i18n,
};

const sentryWebpackPluginOptions = {
  // Additional config options for the Sentry Webpack plugin. Keep in mind that
  // the following options are set automatically, and overriding them is not
  // recommended:
  //   release, url, org, project, authToken, configFile, stripPrefix,
  //   urlPrefix, include, ignore
  org: "bluesquareorg",
  project: "openhexa",
  silent: true, // Suppresses all logs
  dryRun: process.env.NODE_ENV !== "production" || Boolean(process.env.CI),
  // For all available options, see:
  // https://github.com/getsentry/sentry-webpack-plugin#options.

  widenClientFileUpload: true,
  automaticVercelMonitors: false, // Disable automatic Vercel monitors
};

// Make sure adding Sentry options is the last code to run before exporting, to
// ensure that your source maps include changes from all other Webpack plugins
module.exports = withBundleAnalyzer(
  withSentryConfig(config, sentryWebpackPluginOptions),
);
