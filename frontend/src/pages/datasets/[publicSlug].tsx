import Block from "core/components/Block";
import DescriptionList from "core/components/DescriptionList";
import MarkdownViewer from "core/components/MarkdownViewer";
import Time from "core/components/Time";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import PublicPageLayout from "core/layouts/public";
import DatasetExplorer from "datasets/features/DatasetExplorer";
import DatasetVisibilityBadge from "datasets/features/DatasetSharing/DatasetVisibilityBadge";
import DatasetVersionPicker from "datasets/features/DatasetVersionPicker";
import {
  PublicDatasetPageDocument,
  PublicDatasetPageQuery,
  PublicDatasetPageQueryVariables,
  usePublicDatasetPageQuery,
} from "datasets/graphql/queries.generated";
import { useTranslation } from "next-i18next";
import { useState } from "react";

type PublicDatasetPageProps = {
  publicSlug: string;
};

const PER_PAGE = 20;

// Landing page of a dataset permalink.
const PublicDatasetPage: NextPageWithLayout = ({
  publicSlug,
}: PublicDatasetPageProps) => {
  const { t } = useTranslation();
  const [versionId, setVersionId] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [fileId, setFileId] = useState<string | null>(null);
  const { data, previousData } = usePublicDatasetPageQuery({
    variables: {
      slug: publicSlug,
      versionId: versionId ?? "",
      isSpecificVersion: Boolean(versionId),
      page,
      perPage: PER_PAGE,
    },
  });

  // Keeps the page in place while another version or page of files loads.
  const dataset = (data ?? previousData)?.publicDataset;
  if (!dataset) {
    return null;
  }
  const version = dataset.version ?? dataset.latestVersion;
  const files = version?.files.items ?? [];
  const currentFile = files.find((file) => file.id === fileId) ?? files[0];

  return (
    <PublicPageLayout title={dataset.name}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-gray-900">
              {dataset.name}
            </h1>
            <DatasetVisibilityBadge visibility={dataset.visibility} />
          </div>
          {dataset.workspaceName && (
            <p className="mt-1 text-sm text-gray-500">
              {dataset.organizationName
                ? t("Published by {{workspace}} ({{organization}})", {
                    workspace: dataset.workspaceName,
                    organization: dataset.organizationName,
                  })
                : t("Published by {{workspace}}", {
                    workspace: dataset.workspaceName,
                  })}
            </p>
          )}
        </div>
        {version && (
          <DatasetVersionPicker
            className="w-64"
            dataset={dataset}
            version={version}
            onChange={(next) => {
              if (next) {
                setVersionId(next.id);
                setPage(1);
                setFileId(null);
              }
            }}
          />
        )}
      </div>

      <Block>
        <Block.Content className="space-y-6">
          {dataset.description ? (
            <MarkdownViewer sm markdown={dataset.description} />
          ) : (
            <p className="text-sm text-gray-500 italic">
              {t("No description")}
            </p>
          )}
          {version && (
            <DescriptionList columns={2}>
              <DescriptionList.Item label={t("Version")}>
                {version.name}
              </DescriptionList.Item>
              <DescriptionList.Item label={t("Created at")}>
                <Time datetime={version.createdAt} />
              </DescriptionList.Item>
              {version.changelog && (
                <DescriptionList.Item label={t("Changelog")} fullWidth>
                  <MarkdownViewer sm markdown={version.changelog} />
                </DescriptionList.Item>
              )}
            </DescriptionList>
          )}
        </Block.Content>
      </Block>

      {version && currentFile ? (
        <Block>
          <DatasetExplorer
            version={version}
            currentFile={currentFile}
            onClickFile={(file) => setFileId(file.id)}
            perPage={PER_PAGE}
            onPageChange={(next) => {
              setPage(next);
              setFileId(null);
            }}
          />
        </Block>
      ) : (
        <p className="text-center text-sm text-gray-500 italic">
          {version
            ? t("This version has no files.")
            : t("This dataset has no versions yet.")}
        </p>
      )}
    </PublicPageLayout>
  );
};

PublicDatasetPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  async getServerSideProps(ctx, client) {
    const publicSlug = ctx.params!.publicSlug as string;
    const { data } = await client.query<
      PublicDatasetPageQuery,
      PublicDatasetPageQueryVariables
    >({
      query: PublicDatasetPageDocument,
      variables: {
        slug: publicSlug,
        versionId: "",
        isSpecificVersion: false,
        perPage: PER_PAGE,
      },
    });
    return data.publicDataset ? { props: { publicSlug } } : { notFound: true };
  },
});

export default PublicDatasetPage;
