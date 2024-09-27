/**
 * @type {import('next').NextConfig}
 */
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

const { withSentryConfig } = require("@sentry/nextjs");
const { i18n } = require("./next-i18next.config");

let config = {
  experimental: {
    optimizePackageImports: ["next-i18next", "luxon"],
  },

  publicRuntimeConfig: {
    OPENHEXA_BACKEND_URL: process.env.OPENHEXA_BACKEND_URL,
    SENTRY_TRACES_SAMPLE_RATE: parseFloat(
      process.env.SENTRY_TRACES_SAMPLE_RATE || "1",
    ),
    SENTRY_DSN: process.env.SENTRY_DSN,
    SENTRY_ENVIRONMENT: process.env.SENTRY_ENVIRONMENT,
    DISABLE_ANALYTICS: process.env.DISABLE_ANALYTICS === "true",
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

  poweredByHeader: false, // Disable 'x-powered-by' header
  reactStrictMode: true,
  trailingSlash: true,
  i18n,
};

const SENTRY_CONFIG = {
  org: "bluesquareorg",
  project: "openhexa",
  silent: true,
  widenClientFileUpload: true,
  automaticVercelMonitors: false,
};

if (process.env.ANALYZE) {
  // @ts-ignore
  config = withBundleAnalyzer(config);
}

if (process.env.SENTRY_DSN) {
  config = withSentryConfig(config, SENTRY_CONFIG);
}

module.exports = config;
