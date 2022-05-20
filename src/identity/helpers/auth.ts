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

export type AuthenticatedUser = {
  id: string;
  email: string;
  firstName: string | null | undefined;
  lastName: string | null | undefined;
  avatar: { initials: string; color: string };
};

export async function getUser(
  ctx?: GetServerSidePropsContext
): Promise<AuthenticatedUser | null> {
  const client = getApolloClient({ headers: ctx?.req.headers });
  const payload = await client.query<GetUserQuery>({
    query: GetUserDocument,
  });

  const user = payload?.data.me?.user;
  if (!user) {
    return null;
  }
  return {
    id: user.id,
    email: user.email,
    firstName: user.firstName,
    lastName: user.lastName,
    avatar: user.avatar,
  };
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
