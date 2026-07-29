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

export async function getMe(ctx?: GetServerSidePropsContext) {
  const client = getApolloClient({ headers: ctx?.req.headers });
  const payload = await client.query<GetUserQuery>({
    query: GetUserDocument,
  });
  const me = payload?.data.me ?? {};
  if (!me) return null;
  return { ...me };
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
