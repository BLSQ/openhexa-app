// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from "@sentry/nextjs";
import getConfig from "next/config";

const { publicRuntimeConfig } = getConfig();

Sentry.init({
  dsn: publicRuntimeConfig.SENTRY_DSN,

  // Define how likely traces are sampled. Adjust this value in production, or use tracesSampler for greater control.
  tracesSampleRate: 1,

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: false,

  tracePropagationTargets: ["localhost"],
  // Adjust this value in production, or use tracesSampler for greater control
  tracesSampler({ request }) {
    if (request?.requestPath?.startsWith("/ready")) {
      return 0;
    }
    return publicRuntimeConfig.SENTRY_TRACES_SAMPLE_RATE;
  },
});
