/**
 * @type {import('next').NextConfig}
 */
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

const { i18n } = require("./next-i18next.config");

let config = {
  experimental: {
    optimizePackageImports: ["luxon"],
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

  // Next.js in pages mode seems to choke on the ESM format of the editor and one of its dependencies.
  // https://mdxeditor.dev/editor/docs/getting-started#nextjs-pages-router
  transpilePackages: ["@mdweditor/editor", "@uiw/react-codemirror"],
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

    // this will just update topLevelAwait property of config.experiments
    config.experiments = { ...config.experiments, topLevelAwait: true };

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

module.exports = config;

// Injected content via Sentry wizard below

const { withSentryConfig } = require("@sentry/nextjs");

module.exports = withSentryConfig(module.exports, {
  // For all available options, see:
  // https://github.com/getsentry/sentry-webpack-plugin#options

  org: "bluesquareorg",
  project: "openhexa",

  // Pass the auth token
  authToken: process.env.SENTRY_AUTH_TOKEN,

  // Only print logs for uploading source maps in CI
  silent: !process.env.CI,

  // For all available options, see:
  // https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/

  // Upload a larger set of source maps for prettier stack traces (increases build time)
  widenClientFileUpload: true,

  // Automatically annotate React components to show their full name in breadcrumbs and session replay
  reactComponentAnnotation: {
    enabled: true,
  },

  // Route browser requests to Sentry through a Next.js rewrite to circumvent ad-blockers.
  // This can increase your server load as well as your hosting bill.
  // Note: Check that the configured route will not match with your Next.js middleware, otherwise reporting of client-
  // side errors will fail.
  //tunnelRoute: "/monitoring",

  // Hides source maps from generated client bundles
  hideSourceMaps: true,

  // Automatically tree-shake Sentry logger statements to reduce bundle size
  disableLogger: true,

  // Enables automatic instrumentation of Vercel Cron Monitors. (Does not yet work with App Router route handlers.)
  // See the following for more information:
  // https://docs.sentry.io/product/crons/
  // https://vercel.com/docs/cron-jobs
  automaticVercelMonitors: true,
});
