import Block from "core/components/Block";
import MarkdownViewer from "core/components/MarkdownViewer";
import Page from "core/components/Page";
import Time from "core/components/Time";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import DatasetExplorer from "datasets/features/DatasetExplorer";
import { DatasetVisibilityBadge } from "datasets/features/DatasetVisibility";
import DatasetVersionPicker from "datasets/features/DatasetVersionPicker";
import {
  PublicDatasetPageDocument,
  PublicDatasetPageQuery,
  PublicDatasetPageQueryVariables,
  usePublicDatasetPageQuery,
} from "datasets/graphql/queries.generated";
import { getMe } from "identity/helpers/auth";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import Image from "next/legacy/image";
import Link from "next/link";
import { useRouter } from "next/router";
import logo from "public/images/logo.svg";

type PublicDatasetPageProps = {
  datasetId: string;
  versionId: string;
  isSpecificVersion: boolean;
  page: number;
  perPage: number;
  currentFileId: string | null;
};

const DEFAULT_PAGE = 1;
const DEFAULT_PAGE_SIZE = 20;

const getVersion = (dataset: NonNullable<PublicDatasetPageQuery["dataset"]>) =>
  dataset.version ?? dataset.latestVersion ?? null;

// Landing page of a dataset permalink. It works without an account, so it
// stands on its own instead of using the workspace layout, which needs a
// workspace the visitor can open.
const PublicDatasetPage: NextPageWithLayout = (
  props: PublicDatasetPageProps,
) => {
  const { t } = useTranslation();
  const router = useRouter();
  const me = useMe();
  const { currentFileId, ...variables } = props;
  const { data } = usePublicDatasetPageQuery({ variables });

  if (!data?.dataset) {
    return null;
  }
  const { dataset } = data;
  const version = getVersion(dataset);
  const currentFile =
    version?.files.items.find((file) => file.id === currentFileId) ??
    version?.files.items[0] ??
    null;

  const navigate = (query: Record<string, string | number | undefined>) =>
    router.push({
      pathname: router.pathname,
      query: { ...router.query, ...query },
    });

  return (
    <Page title={dataset.name}>
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
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-semibold text-gray-900">
                  {dataset.name}
                </h1>
                <DatasetVisibilityBadge
                  visibility={dataset.visibility}
                  size="sm"
                />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                {dataset.workspace?.organization
                  ? t("Published by {{workspace}} ({{organization}})", {
                      workspace: dataset.workspace.name,
                      organization: dataset.workspace.organization.name,
                    })
                  : t("Published by {{workspace}}", {
                      workspace: dataset.workspace?.name,
                    })}
              </p>
            </div>
            {version && (
              <DatasetVersionPicker
                onChange={(next) =>
                  navigate({ version: next?.id, fileId: undefined, page: 1 })
                }
                dataset={dataset}
                version={version}
                className="min-w-40"
              />
            )}
          </div>

          <Block>
            <Block.Content className="space-y-4">
              {dataset.description ? (
                <MarkdownViewer sm markdown={dataset.description} />
              ) : (
                <p className="text-sm italic text-gray-500">
                  {t("No description")}
                </p>
              )}
              {version && (
                <dl className="grid grid-cols-1 gap-x-6 gap-y-2 text-sm sm:grid-cols-3">
                  <div>
                    <dt className="text-gray-500">{t("Version")}</dt>
                    <dd className="font-medium text-gray-900">
                      {version.name}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">{t("Created at")}</dt>
                    <dd className="font-medium text-gray-900">
                      <Time datetime={version.createdAt} />
                    </dd>
                  </div>
                  {version.changelog && (
                    <div className="sm:col-span-3">
                      <dt className="text-gray-500">{t("Changelog")}</dt>
                      <dd>
                        <MarkdownViewer sm markdown={version.changelog} />
                      </dd>
                    </div>
                  )}
                </dl>
              )}
            </Block.Content>
          </Block>

          <Block>
            {version && currentFile ? (
              <DatasetExplorer
                version={version}
                currentFile={currentFile}
                onClickFile={(file) => navigate({ fileId: file.id })}
                perPage={DEFAULT_PAGE_SIZE}
                onPageChange={(newPage) =>
                  navigate({ page: newPage, fileId: undefined })
                }
              />
            ) : (
              <Block.Content>
                <p className="text-sm italic text-gray-500">
                  {version
                    ? t("This version has no files.")
                    : t("This dataset has no version yet.")}
                </p>
              </Block.Content>
            )}
          </Block>
        </main>
      </div>
    </Page>
  );
};

PublicDatasetPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  async getServerSideProps(ctx, client) {
    const versionId = (ctx.query.version as string) ?? "";
    const variables: PublicDatasetPageQueryVariables = {
      datasetId: ctx.params!.datasetId as string,
      versionId,
      isSpecificVersion: Boolean(versionId),
      page: Number(ctx.query.page) || DEFAULT_PAGE,
      perPage: DEFAULT_PAGE_SIZE,
    };

    const [{ data }, me] = await Promise.all([
      client.query<PublicDatasetPageQuery, PublicDatasetPageQueryVariables>({
        query: PublicDatasetPageDocument,
        variables,
      }),
      getMe(ctx),
    ]);

    if (!data.dataset) {
      // The dataset may exist but not be public: give anonymous visitors a
      // chance to log in before concluding it is not there.
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

    const version = getVersion(data.dataset);
    const requestedFileId = ctx.query.fileId as string | undefined;
    const currentFileId =
      version?.files.items.find((file) => file.id === requestedFileId)?.id ??
      version?.files.items[0]?.id ??
      null;

    return {
      props: { ...variables, currentFileId },
    };
  },
});

export default PublicDatasetPage;
