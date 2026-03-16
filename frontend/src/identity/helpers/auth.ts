import { getApolloClient } from "core/helpers/apollo";
import {
  DisableTwoFactorDocument,
  DisableTwoFactorMutation,
  DisableTwoFactorMutationVariables,
  EnableTwoFactorDocument,
  EnableTwoFactorMutation,
  GenerateChallengeDocument,
  GenerateChallengeMutation,
  VerifyDeviceDocument,
  VerifyDeviceMutation,
  VerifyDeviceMutationVariables,
} from "identity/graphql/mutations.generated";
import {
  GetUserDocument,
  GetUserQuery,
} from "identity/graphql/queries.generated";
import { GetServerSidePropsContext } from "next";
import { getCookie } from "cookies-next";
import Router from "next/router";

const ME_CACHE_TTL_MS = 30_000;

type MeResult = Awaited<ReturnType<typeof fetchMe>>;
const meCache = new Map<string, { value: MeResult; expiresAt: number }>();

function getSessionKey(cookieHeader: string): string | null {
  const match = cookieHeader.match(/(?:^|;\s*)sessionid=([^;]+)/);
  return match ? match[1] : null;
}

async function fetchMe(ctx?: GetServerSidePropsContext) {
  const client = getApolloClient({ headers: ctx?.req.headers });
  const payload = await client.query<GetUserQuery>({
    query: GetUserDocument,
  });
  const me = payload?.data.me ?? {};
  if (!me) return null;
  return { ...me };
}

export async function getMe(ctx?: GetServerSidePropsContext) {
  const cookieHeader = ctx?.req.headers.cookie ?? "";
  const sessionKey = getSessionKey(cookieHeader);

  if (sessionKey) {
    const cached = meCache.get(sessionKey);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.value;
    }
  }

  const value = await fetchMe(ctx);

  if (sessionKey) {
    meCache.set(sessionKey, { value, expiresAt: Date.now() + ME_CACHE_TTL_MS });
  }

  return value;
}

/**
 * Invalidates the me cache.
 * Django invalidates the sessionid on the backend,
 * so any subsequent requests use a new/empty session cookie —
 * the stale cache entry simply never gets matched again.
 * `invalidateMeCache` is here for any future server-side logout route if needed.
 */
export function invalidateMeCache(cookieHeader: string) {
  const sessionKey = getSessionKey(cookieHeader);
  if (sessionKey) meCache.delete(sessionKey);
}

export async function logout() {
  let csrfToken = getCookie("csrftoken");
  if (typeof csrfToken !== "string") {
    throw new Error("Could not find CSRF token in cookies.");
  }
  fetch("/auth/logout/", {
    method: "POST",
    redirect: "follow",
    headers: { "X-CSRFToken": csrfToken },
  }).then((response) => {
    return Router.replace(response.url);
  });
}

export async function generateChallenge(ctx?: GetServerSidePropsContext) {
  const client = getApolloClient({ headers: ctx?.req.headers });

  const payload = await client.mutate<GenerateChallengeMutation>({
    mutation: GenerateChallengeDocument,
  });

  return payload.data?.generateChallenge.success ?? false;
}

export async function disableTwoFactor(token: string) {
  const client = getApolloClient();

  const payload = await client.mutate<
    DisableTwoFactorMutation,
    DisableTwoFactorMutationVariables
  >({
    mutation: DisableTwoFactorDocument,
    variables: { input: { token } },
  });

  return payload.data?.disableTwoFactor.success ?? false;
}

export async function enableTwoFactor() {
  const client = getApolloClient();

  const payload = await client.mutate<EnableTwoFactorMutation>({
    mutation: EnableTwoFactorDocument,
  });

  if (!payload.data) {
    throw new Error("Unable to enable two factor authentication");
  }

  return payload.data.enableTwoFactor;
}

export async function verifyDevice(token?: string) {
  const client = getApolloClient();

  const payload = await client.mutate<
    VerifyDeviceMutation,
    VerifyDeviceMutationVariables
  >({
    mutation: VerifyDeviceDocument,
    variables: { input: { token } },
  });

  if (!payload.data) {
    throw new Error("Unable to enable two factor authentication");
  }

  return payload.data.verifyDevice.success;
}
