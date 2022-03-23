import Router from "next/router";
import { getApolloClient } from "./apollo";
import { gql } from "@apollo/client";
import { GetServerSidePropsContext } from "next";
import { MeQueryQuery } from "./graphql";

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
  const payload = await client.query<MeQueryQuery>({
    query: gql`
      query MeQuery {
        me {
          email
          id
          firstName
          lastName
          avatar {
            initials
            color
          }
        }
      }
    `,
  });

  const user = payload?.data.me;
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

export async function logout(redirectTo: string = "/login") {
  const client = getApolloClient();
  const res: any = await client.mutate({
    mutation: gql`
      mutation Logout {
        logout {
          success
        }
      }
    `,
  });
  if (res?.data?.logout?.success) {
    Router.push(redirectTo);
  }
}
