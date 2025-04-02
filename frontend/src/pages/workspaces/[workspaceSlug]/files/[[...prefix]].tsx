import {
  ArrowUpTrayIcon,
  Cog6ToothIcon,
  FolderPlusIcon,
} from "@heroicons/react/24/outline";
import SearchInput from "core/features/SearchInput";
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
import { FormEventHandler, useEffect, useMemo, useRef, useState } from "react";
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
  searchQuery: string;
  showHiddenFiles: boolean;
};

const ENTRIES_PER_PAGE = 20;

export const WorkspaceFilesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { page, prefix, searchQuery, workspaceSlug, perPage, showHiddenFiles } =
    props;
  const [isUploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [isCreateFolderDialogOpen, setCreateFolderDialogOpen] = useState(false);
  const router = useRouter();
  const [searchQueryState, setSearchQueryState] = useState(searchQuery);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const { data, refetch } = useWorkspaceFilesPageQuery({
    variables: {
      workspaceSlug,
      page,
      prefix,
      query: searchQuery,
      perPage,
      ignoreHiddenFiles: showHiddenFiles,
    },
  });

  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();

      // Move the caret to the end of the input value
      searchInputRef.current.setSelectionRange(
        searchInputRef.current.value.length,
        searchInputRef.current.value.length,
      );
    }
  }, []);

  useCacheKey(["workspace", "files", prefix], () => refetch());
  const crumbs = useMemo(() => {
    return prefix ? prefix.split("/") : [];
  }, [prefix]);

  if (!data?.workspace) {
    return null;
  }

  const { workspace } = data;

  const onChangePage = (page: number, perPage: number) => {
    router.push(
      `/workspaces/${encodeURIComponent(
        workspace.slug,
      )}/files/${prefix}?page=${page}&perPage=${perPage}&q=${searchQueryState}`,
    );
  };
  const onSubmitSearchQuery: FormEventHandler = (event) => {
    event.preventDefault();
    const path = router.asPath.split("?")[0];
    router.push(`${path}?q=${searchQueryState}`, undefined);
  };

  const onChangeHiddenFiles = (checked: boolean, onClose: () => void) => {
    if (checked) {
      setCookie("show-hidden-files", true);
    } else {
      // We don't want to show hidden files
      deleteCookie("show-hidden-files");
    }
    window.location.reload();
    onClose();
  };

  return (
    <Page title={workspace.name}>
      <WorkspaceLayout
        workspace={workspace}
        header={
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
        }
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
        <WorkspaceLayout.PageContent className="space-y-4">
          <div className="flex items-center justify-end gap-3">
            <SearchInput
              ref={searchInputRef}
              onSubmit={onSubmitSearchQuery}
              value={searchQueryState}
              onChange={(event) =>
                setSearchQueryState(event.target.value ?? "")
              }
              className="shadow-xs border-gray-50"
            />
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
                    checked={!showHiddenFiles}
                    onChange={(checked) => onChangeHiddenFiles(checked, close)}
                    labelClassName="whitespace-nowrap"
                    label={t("Show hidden files")}
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    {t(
                      'This will show files and directories starting with a "." (dot)',
                    )}
                  </p>
                </div>
              )}
            </Popover>
            {workspace.permissions.createObject && (
              <>
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
              </>
            )}
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
    const searchQuery = (ctx.query?.q as string) ?? "";
    const perPage = ctx.query?.perPage
      ? parseInt(ctx.query.perPage as string, 10)
      : ENTRIES_PER_PAGE;
    const showHiddenFiles =
      (await getCookie("show-hidden-files", ctx)) === undefined;
    const { data } = await client.query<
      WorkspaceFilesPageQuery,
      WorkspaceFilesPageQueryVariables
    >({
      query: WorkspaceFilesPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug as string,
        page,
        prefix,
        query: searchQuery,
        perPage,
        ignoreHiddenFiles: showHiddenFiles,
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
        searchQuery,
        showHiddenFiles,
        workspaceSlug: ctx.params?.workspaceSlug,
      },
    };
  },
});

export default WorkspaceFilesPage;
