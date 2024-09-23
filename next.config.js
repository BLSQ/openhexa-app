/**
 * @type {import('next').NextConfig}
 */
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

const { withSentryConfig } = require("@sentry/nextjs");
const { i18n } = require("./next-i18next.config");

let config = {
  output: "standalone",
  experimental: {
    optimizePackageImports: ["next-i18next", "luxon"],
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

if (process.env.ANALYZE) {
  // @ts-ignore
  config = withBundleAnalyzer(config);
}

if (process.env.SENTRY_DSN) {
  config = withSentryConfig(config, {
    // Additional config options for the Sentry Webpack plugin. Keep in mind that
    // the following options are set automatically, and overriding them is not
    // recommended:
    //   release, url, org, project, authToken, configFile, stripPrefix,
    //   urlPrefix, include, ignore
    org: "bluesquareorg",
    project: "openhexa",
    silent: true, // Suppresses all logs
    // For all available options, see:
    // https://github.com/getsentry/sentry-webpack-plugin#options.

    widenClientFileUpload: true,
    automaticVercelMonitors: false, // Disable automatic Vercel monitors
  });
}

module.exports = config;
