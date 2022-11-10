import { GetServerSidePropsContext, GetServerSidePropsResult } from "next";
import { getMe } from "identity/helpers/auth";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { addApolloState, CustomApolloClient, getApolloClient } from "./apollo";

interface GetServerSidePropsContextWithUser extends GetServerSidePropsContext {
  me: Awaited<ReturnType<typeof getMe>>;
}

interface CreateGetServerSideProps {
  i18n?: string[];
  requireAuth?: boolean;
  getServerSideProps?: (
    ctx: GetServerSidePropsContextWithUser,
    client: CustomApolloClient
  ) =>
    | Promise<GetServerSidePropsResult<any> | void>
    | GetServerSidePropsResult<any>
    | void;
}

interface ServerSideProps {
  me: Awaited<ReturnType<typeof getMe>>;
  [key: string]: any;
}

export function createGetServerSideProps(options: CreateGetServerSideProps) {
  const {
    i18n = ["messages"],
    requireAuth = false,
    getServerSideProps,
  } = options;

  return async function (
    ctx: GetServerSidePropsContextWithUser
  ): Promise<GetServerSidePropsResult<ServerSideProps>> {
    const me = await getMe(ctx);
    ctx.me = me;
    const res = {
      props: {
        me,
        // Replace ctx.locale by user.lang when implemented
        ...(await serverSideTranslations(ctx.locale ?? "en", i18n)),
      },
    };

    if (requireAuth && !res.props.me?.user) {
      return {
        ...res,
        redirect: {
          destination: `/?next=${encodeURIComponent(ctx.resolvedUrl)}`,
          permanent: false,
        },
      };
    }

    if (getServerSideProps) {
      const client = getApolloClient(ctx.req);
      const nextRes = await getServerSideProps(ctx, client);
      return {
        ...res,
        ...(nextRes ?? {}),
        props: {
          ...res.props,
          ...addApolloState(client).props,
          ...(nextRes && "props" in nextRes ? nextRes.props : {}),
        },
      };
    }

    return res;
  };
}
