import { getCookie } from "cookies-next";
import { getPublicEnv } from "./runtimeConfig";

/** Reads Django's CSRF token from the browser's cookies. */
export function getCsrfToken(): string | undefined {
  const token = getCookie(getPublicEnv().CSRF_COOKIE_NAME);
  return typeof token === "string" ? token : undefined;
}
