export interface RuntimeEnv {
  OPENHEXA_BACKEND_URL: string;
  SENTRY_DSN: string;
  SENTRY_ENVIRONMENT: string;
  SENTRY_TRACES_SAMPLE_RATE: string;
  DISABLE_ANALYTICS: string;
  CONSOLE_URL: string;
}

declare global {
  interface Window {
    __ENV__?: RuntimeEnv;
  }
}

export function getPublicEnv(): RuntimeEnv {
  if (typeof window !== "undefined" && window.__ENV__) {
    return window.__ENV__;
  }
  return {
    OPENHEXA_BACKEND_URL: process.env.OPENHEXA_BACKEND_URL ?? "",
    SENTRY_DSN: process.env.SENTRY_DSN ?? "",
    SENTRY_ENVIRONMENT: process.env.SENTRY_ENVIRONMENT ?? "",
    SENTRY_TRACES_SAMPLE_RATE: process.env.SENTRY_TRACES_SAMPLE_RATE ?? "1",
    DISABLE_ANALYTICS: process.env.DISABLE_ANALYTICS ?? "",
    CONSOLE_URL: process.env.CONSOLE_URL ?? "",
  };
}

export const usePublicEnv = getPublicEnv;
