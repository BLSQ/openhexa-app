// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT,
  tracePropagationTargets: ["localhost"],
  // Adjust this value in production, or use tracesSampler for greater control
  tracesSampler({ transactionContext }) {
    if (transactionContext.metadata?.requestPath?.startsWith("/ready")) {
      return 0;
    }
    if (process.env.SENTRY_TRACES_SAMPLE_RATE) {
      return parseFloat(process.env.SENTRY_TRACES_SAMPLE_RATE);
    }
    return 1;
  },
  // ...
  // Note: if you want to override the automatic release value, do not set a
  // `release` value here - use the environment variable `SENTRY_RELEASE`, so
  // that it will also get attached to your source maps
});
