import { getApolloClient } from "core/helpers/apollo";
import {
  GetUserDocument,
  GetUserQuery,
} from "identity/graphql/queries.generated";
import { GetServerSidePropsContext } from "next";
import Router from "next/router";

export async function getMe(ctx?: GetServerSidePropsContext) {
  const client = getApolloClient({ headers: ctx?.req.headers });
  const payload = await client.query<GetUserQuery>({
    query: GetUserDocument,
  });

  const me = payload?.data.me;
  if (!me) return null;
  return me;
}

export async function logout() {
  return Router.push("/auth/logout");
}
