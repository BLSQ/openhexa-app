import { ApolloError } from "@apollo/client";
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

    // Because getMe and the page's getServerSideProps run in parallel, an unauthenticated
    // user will cause page queries to fail with UNAUTHENTICATED before getMe resolves and
    // the redirect logic below has a chance to run. We hold the error here so Promise.all
    // can complete, then let the redirect checks handle it. If no redirect fires (meaning
    // the page didn't require auth but a query still demanded it), we re-throw.
    let unauthenticatedError: ApolloError | undefined;
    const pagePropsPromise = getServerSideProps
      ? Promise.resolve(getServerSideProps(ctx, client)).catch((err) => {
          if (
            err instanceof ApolloError &&
            err.graphQLErrors.some((e) => e.extensions?.code === "UNAUTHENTICATED")
          ) {
            unauthenticatedError = err;
            return undefined;
          }
          throw err;
        })
      : Promise.resolve(undefined);

    const [me, nextRes] = await Promise.all([getMePromise, pagePropsPromise]);

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

    if (unauthenticatedError) {
      throw unauthenticatedError;
    }

    const t2 = perfLogs ? performance.now() : 0;
    const translations = await serverSideTranslations(
      me?.user?.language ?? getAcceptPreferredLocale(ctx.req.headers) ?? "en",
      i18n,
    );
    if (perfLogs) console.log(`[page] translations: ${(performance.now() - t2).toFixed(1)}ms`);

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
