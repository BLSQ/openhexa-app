import { ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { SavedQueryVisibility } from "graphql/types";
import { getMe } from "identity/helpers/auth";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import Image from "next/legacy/image";
import Link from "next/link";
import { useRouter } from "next/router";
import logo from "public/images/logo.svg";
import { useCallback, useEffect, useState } from "react";
import { toast } from "react-toastify";
import DataStudioResults from "workspaces/features/DataStudioEditor/DataStudioResults";
import { downloadSavedQueryCsv } from "workspaces/features/DataStudioEditor/downloadQueryCsv";
import { GHOST } from "workspaces/features/DataStudioEditor/toolbarStyles";
import SavedQueryVisibilityBadge from "workspaces/features/SavedQueries/SavedQueryVisibilityBadge";
import {
  PublicSavedQueryPageDocument,
  PublicSavedQueryPageQuery,
  PublicSavedQueryPageQueryVariables,
  useExecuteSavedQueryLazyQuery,
  usePublicSavedQueryPageQuery,
} from "workspaces/graphql/queries.generated";
import {
  dataStudioRoutes,
  MAX_ROWS_OPTIONS,
} from "workspaces/helpers/dataStudio";

type PublicSavedQueryPageProps = {
  querySlug: string;
};

// Landing page of a saved query permalink. It works without an account, so it
// stands on its own instead of using the workspace layout, which needs a
// workspace the visitor can open. The query runs as soon as the page loads:
// there is nothing to edit here, so there is nothing to wait for either.
const PublicSavedQueryPage: NextPageWithLayout = ({
  querySlug,
}: PublicSavedQueryPageProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const me = useMe();
  const { data } = usePublicSavedQueryPageQuery({
    variables: { slug: querySlug },
  });
  const [maxRows, setMaxRows] = useState(MAX_ROWS_OPTIONS[0]);
  const [exporting, setExporting] = useState(false);
  // Results are large and never read from the cache elsewhere; skip
  // normalisation so big result sets are not retained for the page lifetime.
  const [execute, { data: runData, loading, error }] =
    useExecuteSavedQueryLazyQuery({ fetchPolicy: "no-cache" });

  const run = useCallback(
    () => execute({ variables: { slug: querySlug, maxRows } }),
    [execute, querySlug, maxRows],
  );

  // On load, and again whenever the row cap changes: the cap is the only
  // control a visitor has over the run.
  useEffect(() => {
    run();
  }, [run]);

  const result = runData?.executeSavedQuery;
  const canExport = Boolean(result?.success && (result.rows?.length ?? 0) > 0);

  const exportCsv = async () => {
    if (exporting) {
      return;
    }
    setExporting(true);
    try {
      await downloadSavedQueryCsv(querySlug);
    } catch {
      toast.error(t("Could not export the query results. Please try again."));
    } finally {
      setExporting(false);
    }
  };

  if (!data?.savedQueryBySlug) {
    return null;
  }
  const savedQuery = data.savedQueryBySlug;

  return (
    <Page title={savedQuery.name}>
      <div className="min-h-screen bg-gray-50">
        <header className="border-b border-gray-200 bg-white">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
            <Link href="/" className="relative block h-8 w-24">
              <Image src={logo} layout="fill" alt="OpenHEXA" />
            </Link>
            {me?.user ? (
              <Link
                href="/workspaces"
                className="text-sm text-blue-600 hover:underline"
              >
                {t("Go to my workspaces")}
              </Link>
            ) : (
              <Link
                href={`/login?next=${encodeURIComponent(router.asPath)}`}
                className="text-sm text-blue-600 hover:underline"
              >
                {t("Log in")}
              </Link>
            )}
          </div>
        </header>

        <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-semibold text-gray-900">
                {savedQuery.name}
              </h1>
              <SavedQueryVisibilityBadge
                visibility={savedQuery.visibility}
                size="sm"
              />
            </div>
            <p className="mt-1 text-sm text-gray-500">
              {savedQuery.workspace.organization
                ? t("Published by {{workspace}} ({{organization}})", {
                    workspace: savedQuery.workspace.name,
                    organization: savedQuery.workspace.organization.name,
                  })
                : t("Published by {{workspace}}", {
                    workspace: savedQuery.workspace.name,
                  })}
            </p>
          </div>

          <Block>
            <Block.Content>
              {savedQuery.description ? (
                <p className="text-sm whitespace-pre-line text-gray-700">
                  {savedQuery.description}
                </p>
              ) : (
                <p className="text-sm text-gray-500 italic">
                  {t("No description")}
                </p>
              )}
            </Block.Content>
          </Block>

          <div className="flex h-[70vh] min-h-[420px] flex-col overflow-hidden rounded-md border bg-white shadow-xs">
            <div className="flex h-11 shrink-0 items-center justify-end gap-2 border-b border-gray-200 px-3">
              <label className="flex items-center gap-1.5 text-xs text-gray-500">
                {t("Max rows")}
                <select
                  value={maxRows}
                  disabled={loading}
                  onChange={(event) => setMaxRows(Number(event.target.value))}
                  className="h-8 rounded-md border border-gray-200 pr-7 pl-2 text-xs text-gray-700 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                >
                  {MAX_ROWS_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option.toLocaleString()}
                    </option>
                  ))}
                </select>
              </label>
              {/* The server re-run can take a while; reassure the visitor
                  right where they clicked. */}
              {exporting && (
                <span className="text-xs text-gray-400">
                  {t("This may take a while")}
                </span>
              )}
              <button
                type="button"
                onClick={exportCsv}
                disabled={!canExport || exporting}
                className={GHOST}
              >
                {exporting ? (
                  <>
                    <Spinner size="xs" />
                    {t("Exporting…")}
                  </>
                ) : (
                  <>
                    <ArrowDownTrayIcon className="h-4 w-4" />
                    {t("Export CSV")}
                  </>
                )}
              </button>
            </div>
            <div className="min-h-0 flex-1">
              <DataStudioResults
                loading={loading}
                result={result}
                error={error}
                onRetry={run}
                widgetHint={false}
              />
            </div>
          </div>
        </main>
      </div>
    </Page>
  );
};

PublicSavedQueryPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  async getServerSideProps(ctx, client) {
    const querySlug = ctx.params!.querySlug as string;
    const [{ data }, me] = await Promise.all([
      client.query<
        PublicSavedQueryPageQuery,
        PublicSavedQueryPageQueryVariables
      >({
        query: PublicSavedQueryPageDocument,
        variables: { slug: querySlug },
      }),
      getMe(ctx),
    ]);

    const savedQuery = data.savedQueryBySlug;
    if (!savedQuery) {
      // The query may exist but not be public: give anonymous visitors a chance
      // to log in before concluding it is not there.
      if (!me?.user) {
        return {
          redirect: {
            permanent: false,
            destination: `/login?next=${encodeURIComponent(ctx.resolvedUrl)}`,
          },
        };
      }
      return { notFound: true };
    }

    // Only public queries have a permalink. Anyone who can see another one is a
    // member of its workspace, and the Data Studio is where they work with it.
    if (savedQuery.visibility !== SavedQueryVisibility.Public) {
      return {
        redirect: {
          permanent: false,
          destination: dataStudioRoutes(savedQuery.workspace.slug).query(
            savedQuery.slug,
          ),
        },
      };
    }

    return { props: { querySlug: savedQuery.slug } };
  },
});

export default PublicSavedQueryPage;
