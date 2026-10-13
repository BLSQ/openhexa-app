import { gql } from "@apollo/client";
import {
  ArrowDownTrayIcon,
  GlobeAltIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import { BucketObject, BucketObjectType } from "graphql/types";
import { useTranslation } from "next-i18next";
import DeleteBucketObject from "../DeleteBucketObject";
import DownloadBucketObject from "../DownloadBucketObject";
import {
  BucketExplorer_ObjectsFragment,
  BucketExplorer_WorkspaceFragment,
} from "./BucketExplorer.generated";
import FileSystemDataGrid from "workspaces/components/FileSystemDataGrid";
import {
  getPublicFileUrl,
  isInPublicFolder,
  isPublicFolder,
  PublicFileLinkButton,
  PublicFolderBadge,
} from "workspaces/features/PublicFiles";
import { useUploadFiles } from "workspaces/hooks/useUploadFiles";

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

  const isPublicFile = (item: BucketObject) =>
    workspace.publicFilesEnabled &&
    item.type === BucketObjectType.File &&
    isInPublicFolder(item.key);

  const nameBadgeRenderer = (item: BucketObject) =>
    workspace.publicFilesEnabled &&
    item.type === BucketObjectType.Directory &&
    isPublicFolder(item.key) ? (
      <PublicFolderBadge className="ml-1" />
    ) : null;

  const actionsRenderer = (item: BucketObject) => (
    <div className="flex flex-1 justify-end gap-2">
      {isPublicFile(item) && (
        <PublicFileLinkButton
          url={getPublicFileUrl(workspace.publicFilesUrl, item.key)}
        />
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
    <>
      {workspace.publicFilesEnabled && prefix && isInPublicFolder(prefix) && (
        <p className="flex items-center gap-2 px-4 py-3 text-sm text-blue-800 bg-blue-50">
          <GlobeAltIcon className="h-4 w-4 shrink-0" />
          {t(
            "The files in this folder can be read by anyone who has their link, without an OpenHEXA account.",
          )}
        </p>
      )}
      <FileSystemDataGrid
        data={objects.items as BucketObject[]}
        fixedLayout={false}
        pagination={objects}
        perPage={perPage}
        actionsRenderer={actionsRenderer}
        directoryLinkGenerator={directoryLinkGenerator}
        nameBadgeRenderer={nameBadgeRenderer}
        onDroppingFiles={uploadFiles}
        onChangePage={onChangePage}
      />
    </>
  );
};

BucketExplorer.fragments = {
  workspace: gql`
    fragment BucketExplorer_workspace on Workspace {
      slug
      publicFilesEnabled
      publicFilesUrl
      ...DownloadBucketObject_workspace
      ...DeleteBucketObject_workspace
    }

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
