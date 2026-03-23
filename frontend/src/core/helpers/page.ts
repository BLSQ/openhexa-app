import { getMe } from "identity/helpers/auth";
import { GetServerSidePropsContext, GetServerSidePropsResult } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { addApolloState, CustomApolloClient, getApolloClient } from "./apollo";
import { getAcceptPreferredLocale } from "./i18n";

interface GetServerSidePropsContextWithUser extends GetServerSidePropsContext {
  me: Awaited<ReturnType<typeof getMe>>;
}

interface CreateGetServerSideProps {
  i18n?: string[];
  requireAuth?: boolean;
  redirectIfLoggedIn?: string | ((ctx: GetServerSidePropsContextWithUser) => string);
  getServerSideProps?: (
    ctx: GetServerSidePropsContextWithUser,
    client: CustomApolloClient,
  ) =>
    | Promise<GetServerSidePropsResult<any> | void>
    | GetServerSidePropsResult<any>
    | void;
}

interface ServerSideProps {
  me: Awaited<ReturnType<typeof getMe>>;
  cookieHeader?: string;

  [key: string]: any;
}

export function createGetServerSideProps(options: CreateGetServerSideProps) {
  const {
    i18n = ["messages"],
    requireAuth = false,
    redirectIfLoggedIn,
    getServerSideProps,
  } = options;

  return async function (
    ctx: GetServerSidePropsContextWithUser,
  ): Promise<GetServerSidePropsResult<ServerSideProps>> {
    // TODO: remove all performance logs after analysis
    const perfLogs = !!process.env.PERFORMANCE_LOGS;
    const t0 = perfLogs ? performance.now() : 0;
    const client = getApolloClient(ctx.req);

    // getMe and page queries run in parallel. We eagerly set ctx.me via .then so
    // that async page callbacks find it populated after their first suspension point.
    const t1 = perfLogs ? performance.now() : 0;
    const getMePromise = getMe(ctx).then((me) => {
      ctx.me = me;
      if (perfLogs) console.log(`[page] getMe: ${(performance.now() - t1).toFixed(1)}ms`);
      return me;
    });

    const [me, nextRes] = await Promise.all([
      getMePromise,
      getServerSideProps ? getServerSideProps(ctx, client) : Promise.resolve(undefined),
    ]);

    const t2 = perfLogs ? performance.now() : 0;
    const translations = await serverSideTranslations(
      me?.user?.language ?? getAcceptPreferredLocale(ctx.req.headers) ?? "en",
      i18n,
    );
    if (perfLogs) console.log(`[page] translations: ${(performance.now() - t2).toFixed(1)}ms`);

    if (redirectIfLoggedIn && ctx.me?.user) {
      return {
        redirect: {
          permanent: false,
          destination:
            typeof redirectIfLoggedIn === "function"
              ? redirectIfLoggedIn(ctx)
              : redirectIfLoggedIn,
        },
      };
    }

    if (!ctx.me?.user && requireAuth) {
      return {
        redirect: {
          permanent: false,
          destination: `/login?next=${encodeURIComponent(ctx.resolvedUrl)}`,
        },
      };
    }

    if (ctx.me?.user) {
      const { features } = ctx.me;

      // If the user doesn't have the legacy feature, redirect to workspaces page if the user
      // tries to access a page that is not /workspaces or /user or /register or /organizations
      if (
        !features.some((f) => f.code === "openhexa_legacy") &&
        !["/workspaces", "/user", "/register", "/organizations", "/mcp"].some(
          (path) => ctx.resolvedUrl.startsWith(path),
        )
      ) {
        return {
          redirect: {
            permanent: false,
            destination: "/workspaces",
          },
        };
      }
    }

    const result = {
      props: {
        ...translations,
        me: ctx.me,
        cookieHeader: ctx.req.headers.cookie ?? "",
      },
    } as any;

    if (perfLogs) console.log(`[page] everything: ${(performance.now() - t0).toFixed(1)}ms`);
    if (getServerSideProps) {
      return {
        ...result,
        ...(nextRes ?? {}),
        props: {
          ...(result.props ?? {}),
          ...addApolloState(client).props,
          ...(nextRes && "props" in nextRes ? nextRes.props : {}),
        },
      };
    }

    return result;
  };
}
