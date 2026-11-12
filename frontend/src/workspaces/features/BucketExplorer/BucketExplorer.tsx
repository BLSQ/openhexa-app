import { gql } from "@apollo/client";
import {
  ArrowDownTrayIcon,
  GlobeAltIcon,
  LinkIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import Tooltip from "core/components/Tooltip";
import { BucketObject, BucketObjectType } from "graphql/types";
import { useTranslation } from "next-i18next";
import DeleteBucketObject from "../DeleteBucketObject";
import DownloadBucketObject from "../DownloadBucketObject";
import {
  BucketExplorer_ObjectsFragment,
  BucketExplorer_WorkspaceFragment,
} from "./BucketExplorer.generated";
import FileSystemDataGrid from "workspaces/components/FileSystemDataGrid";
import { useUploadFiles } from "workspaces/hooks/useUploadFiles";
import { toast } from "react-toastify";
import PublicFolderPlaceholder from "./PublicFolderPlaceholder";

const PUBLIC_FOLDER = "public/";

const isPublicFolder = (item: BucketObject) =>
  item.type === BucketObjectType.Directory &&
  item.key.replace(/\/$/, "") === PUBLIC_FOLDER.slice(0, -1);

// The workspace slug is part of the public URL, the path is relative to the public folder.
export const getPublicFileUrl = (publicFilesUrl: string, key: string) =>
  publicFilesUrl +
  key.slice(PUBLIC_FOLDER.length).split("/").map(encodeURIComponent).join("/");

type BucketExplorerProps = {
  workspace: BucketExplorer_WorkspaceFragment;
  objects: BucketExplorer_ObjectsFragment;
  prefix: string | null;
  perPage: number;
  onChangePage(page: number, perPage: number): void;
};

const BucketExplorer = (props: BucketExplorerProps) => {
  const { t } = useTranslation();
  const { workspace, objects, prefix, perPage, onChangePage } = props;
  const uploadFiles = useUploadFiles({ workspaceSlug: workspace.slug, prefix });

  const directoryLinkGenerator = (item: BucketObject) =>
    `/workspaces/${encodeURIComponent(workspace.slug)}/files/${item.key}`;

  const publicFilesUrl = workspace.publicFiles?.url;

  const copyPublicLink = async (item: BucketObject) => {
    try {
      await navigator.clipboard.writeText(
        getPublicFileUrl(publicFilesUrl!, item.key),
      );
      toast.success(t("Public link copied to the clipboard"));
    } catch {
      // The clipboard API is unavailable outside secure contexts (plain http) or when denied
      toast.error(t("The public link could not be copied to the clipboard"));
    }
  };

  // A span, not the default button: the suffix is rendered inside the folder link
  const nameSuffixRenderer = (item: BucketObject) =>
    publicFilesUrl && isPublicFolder(item) ? (
      <Tooltip
        as="span"
        label={t(
          "Shared publicly: anyone with the link of a file in this folder can download it, without signing in.",
        )}
      >
        <GlobeAltIcon
          className="ml-1 h-4 w-4 text-green-600"
          aria-label={t("Shared publicly")}
        />
      </Tooltip>
    ) : null;

  const actionsRenderer = (item: BucketObject) => (
    <div className="flex flex-1 justify-end gap-2">
      {publicFilesUrl &&
        item.type === BucketObjectType.File &&
        item.key.startsWith(PUBLIC_FOLDER) && (
          <Button
            onClick={() => copyPublicLink(item)}
            variant="secondary"
            size="sm"
            title={t("Copy public link")}
          >
            <LinkIcon className="h-4 w-4" />
          </Button>
        )}
      <DeleteBucketObject workspace={workspace} object={item}>
        {({ onClick }) => (
          <Button
            onClick={onClick}
            variant="outlined"
            size="sm"
            title={t("Delete")}
            className="hover:bg-red-600 hover:text-white"
          >
            <TrashIcon className="h-4 w-4" />
          </Button>
        )}
      </DeleteBucketObject>
      {item.type === BucketObjectType.File && (
        <DownloadBucketObject object={item} workspace={workspace}>
          {({ onClick, isPreparing }) => (
            <Button
              onClick={onClick}
              disabled={isPreparing}
              variant="secondary"
              size="sm"
              title={t("Download")}
            >
              {isPreparing ? (
                <div className="flex h-4 w-4 items-center justify-center">
                  <Spinner size="xs" />
                </div>
              ) : (
                <ArrowDownTrayIcon className="h-4 w-4" />
              )}
            </Button>
          )}
        </DownloadBucketObject>
      )}
    </div>
  );

  return (
    <FileSystemDataGrid
      data={objects.items as BucketObject[]}
      fixedLayout={false}
      pagination={objects}
      perPage={perPage}
      actionsRenderer={actionsRenderer}
      directoryLinkGenerator={directoryLinkGenerator}
      nameSuffixRenderer={nameSuffixRenderer}
      leadingRow={
        !prefix && objects.pageNumber === 1 ? (
          <PublicFolderPlaceholder workspace={workspace} />
        ) : null
      }
      onDroppingFiles={uploadFiles}
      onChangePage={onChangePage}
    />
  );
};

BucketExplorer.fragments = {
  workspace: gql`
    fragment BucketExplorer_workspace on Workspace {
      slug
      publicFiles {
        url
      }
      ...DownloadBucketObject_workspace
      ...DeleteBucketObject_workspace
      ...PublicFolderPlaceholder_workspace
    }

    ${PublicFolderPlaceholder.fragments.workspace}
    ${DeleteBucketObject.fragments.workspace}
    ${DownloadBucketObject.fragments.workspace}
  `,

  objects: gql`
    fragment BucketExplorer_objects on BucketObjectPage {
      hasNextPage
      hasPreviousPage
      pageNumber
      items {
        key
        name
        path
        size
        updatedAt
        type
        ...DownloadBucketObject_object
        ...DeleteBucketObject_object
      }
    }
    ${DownloadBucketObject.fragments.object}
    ${DeleteBucketObject.fragments.object}
  `,
};

export default BucketExplorer;
