import {
  LogoutDocument,
  LogoutMutation,
} from "identity/graphql/mutations.generated";
import {
  GetUserDocument,
  GetUserQuery,
} from "identity/graphql/queries.generated";
import { GetServerSidePropsContext } from "next";
import Router from "next/router";
import { getApolloClient } from "core/helpers/apollo";

export async function getMe(ctx?: GetServerSidePropsContext) {
  const client = getApolloClient({ headers: ctx?.req.headers });
  const payload = await client.query<GetUserQuery>({
    query: GetUserDocument,
  });

  const me = payload?.data.me;
  if (!me) return null;
  return me;
}

export async function logout(redirectTo: string = "/") {
  const client = getApolloClient();
  const res: any = await client.mutate<LogoutMutation>({
    mutation: LogoutDocument,
  });
  if (res?.data?.logout?.success) {
    Router.push(redirectTo);
  }
}
