import {
  ArrowUpTrayIcon,
  Cog6ToothIcon,
  FolderPlusIcon,
} from "@heroicons/react/24/outline";
import { deleteCookie, getCookie, setCookie } from "cookies-next";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import Popover from "core/components/Popover/Popover";
import Switch from "core/components/Switch/Switch";
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
  WorkspaceFilesPageDocument,
  WorkspaceFilesPageQuery,
  WorkspaceFilesPageQueryVariables,
  useWorkspaceFilesPageQuery,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
  prefix: string;
  workspaceSlug: string;
  ignoreHiddenFiles: boolean;
};

export const WorkspaceFilesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { page, prefix, workspaceSlug, perPage, ignoreHiddenFiles } = props;
  const [isUploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [isCreateFolderDialogOpen, setCreateFolderDialogOpen] = useState(false);
  const router = useRouter();

  const { data, refetch } = useWorkspaceFilesPageQuery({
    variables: {
      workspaceSlug,
      page,
      prefix,
      perPage,
      ignoreHiddenFiles,
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
        workspace.slug,
      )}/files/${prefix}?page=${page}`,
    );
  };

  const onChangeHiddenFiles = (checked: boolean, onClose: () => void) => {
    if (checked) {
      // We don't want to show hidden files
      deleteCookie("show-hidden-files");
    } else {
      setCookie("show-hidden-files", true);
    }

    window.location.reload();
    onClose();
  };

  return (
    <Page title={workspace.name}>
      <WorkspaceLayout
        workspace={workspace}
        helpLinks={[
          {
            label: t("About the workspace's filesystem"),
            href: "https://github.com/BLSQ/openhexa/wiki/User-manual#file-management-in-workspaces",
          },
          {
            label: t("Using the filesystem in notebooks"),
            href: "https://github.com/BLSQ/openhexa/wiki/Using-notebooks-in-OpenHEXA#using-the-workspace-filesystem",
          },
          {
            label: t("Using the filesystem in pipelines"),
            href: "https://github.com/BLSQ/openhexa/wiki/Writing-OpenHEXA-pipelines#reading-and-writing-files",
          },
        ]}
      >
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
                  workspace.slug,
                )}/files/${crumbs.slice(0, idx + 1).join("/")}`}
              >
                {directory}
              </Breadcrumbs.Part>
            ))}
          </Breadcrumbs>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="space-y-4">
          <div className="flex items-center justify-end gap-3">
            <Popover
              as="div"
              trigger={
                <Button variant="secondary">
                  <Cog6ToothIcon className="h-4 w-4" />
                </Button>
              }
              className="flex flex-col items-center justify-between"
            >
              {({ close }) => (
                <div>
                  <Switch
                    checked={ignoreHiddenFiles}
                    onChange={(checked) => onChangeHiddenFiles(checked, close)}
                    labelClassName="whitespace-nowrap"
                    label={t("Hide hidden files")}
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    {t(
                      'This will hide files and directories starting by a "." (dot)',
                    )}
                  </p>
                </div>
              )}
            </Popover>
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
    await WorkspaceLayout.prefetch(ctx, client);
    const prefixArr = (ctx.params?.prefix as string[]) ?? [];
    const prefix = prefixArr.length > 0 ? prefixArr.join("/") + "/" : "";
    const page = ctx.query?.page ? parseInt(ctx.query.page as string, 10) : 1;
    const ignoreHiddenFiles = getCookie("show-hidden-files", ctx) === undefined;
    const perPage = 10;
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
        ignoreHiddenFiles,
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
        ignoreHiddenFiles,
        workspaceSlug: ctx.params?.workspaceSlug,
      },
    };
  },
});

export default WorkspaceFilesPage;
