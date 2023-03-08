import { ArrowUpTrayIcon, FolderPlusIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useMemo, useState } from "react";
import BucketExplorer from "workspaces/features/BucketExplorer";
import CreateBucketFolderDialog from "workspaces/features/CreateBucketFolderDialog";
import UploadObjectDialog from "workspaces/features/UploadObjectDialog";
import {
  useWorkspaceFilesPageQuery,
  WorkspaceFilesPageDocument,
  WorkspaceFilesPageQuery,
  WorkspaceFilesPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
  prefix: string;
  workspaceSlug: string;
};

export const WorkspaceFilesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { page, prefix, workspaceSlug, perPage } = props;
  const [isUploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [isCreateFolderDialogOpen, setCreateFolderDialogOpen] = useState(false);
  const router = useRouter();

  const { data, refetch } = useWorkspaceFilesPageQuery({
    variables: {
      workspaceSlug,
      page,
      prefix,
      perPage,
    },
  });
  useCacheKey(["workspace", "files", prefix], () => refetch());

  const crumbs = useMemo(() => {
    return prefix ? prefix.split("/") : [];
  }, [prefix]);

  if (!data?.workspace) {
    return null;
  }

  const { workspace } = data;

  const onChangePage = (page: number) => {
    router.push(
      `/workspaces/${encodeURIComponent(
        workspace.slug
      )}/files/${prefix}?page=${page}`
    );
  };

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout workspace={workspace}>
        <WorkspaceLayout.Header className="flex items-center justify-between">
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/files`}
              isLast={crumbs.length === 0}
            >
              {t("Files")}
            </Breadcrumbs.Part>
            {crumbs.map((directory, idx) => (
              <Breadcrumbs.Part
                key={idx}
                isLast={idx === crumbs.length}
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug
                )}/files/${crumbs.slice(0, idx + 1).join("/")}`}
              >
                {directory}
              </Breadcrumbs.Part>
            ))}
          </Breadcrumbs>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="space-y-4">
          <div className="flex items-center justify-end gap-3">
            <Button
              variant="secondary"
              leadingIcon={<FolderPlusIcon className="h-4 w-4" />}
              onClick={() => setCreateFolderDialogOpen(true)}
            >
              {t("Create a folder")}
            </Button>
            <Button
              variant="primary"
              leadingIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
              onClick={() => setUploadDialogOpen(true)}
            >
              {t("Upload files")}
            </Button>
          </div>
          <Block className="divide divide-y divide-gray-100">
            <BucketExplorer
              workspace={workspace}
              objects={workspace.bucket.objects}
              onChangePage={onChangePage}
              perPage={perPage}
            />
            <UploadObjectDialog
              open={isUploadDialogOpen}
              onClose={() => setUploadDialogOpen(false)}
              prefix={prefix}
              workspace={workspace}
            />
            <CreateBucketFolderDialog
              workspace={workspace}
              open={isCreateFolderDialogOpen}
              onClose={() => setCreateFolderDialogOpen(false)}
              prefix={prefix}
            />
          </Block>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceFilesPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    WorkspaceLayout.prefetch(client);

    const prefixArr = (ctx.params?.prefix as string[]) ?? [];
    const prefix = prefixArr.length > 0 ? prefixArr.join("/") + "/" : "";
    const page = ctx.query?.page ? parseInt(ctx.query.page as string, 10) : 1;

    const perPage = 25;
    const { data } = await client.query<
      WorkspaceFilesPageQuery,
      WorkspaceFilesPageQueryVariables
    >({
      query: WorkspaceFilesPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug as string,
        page,
        prefix,
        perPage,
      },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }

    return {
      props: {
        page,
        perPage,
        prefix,
        workspaceSlug: ctx.params?.workspaceSlug,
      },
    };
  },
});

export default WorkspaceFilesPage;
