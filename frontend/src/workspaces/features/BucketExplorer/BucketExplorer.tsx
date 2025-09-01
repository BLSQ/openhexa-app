import { gql } from "@apollo/client";
import { ArrowDownTrayIcon, TrashIcon } from "@heroicons/react/24/outline";
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
import { useUploadFiles } from "workspaces/hooks/useUploadFiles";
import FileSystemDataGrid from "../../components/FileSystemDataGrid";

type BucketExplorerProps = {
  workspace: BucketExplorer_WorkspaceFragment;
  objects: BucketExplorer_ObjectsFragment;
  prefix?: string | null;
  perPage: number;
  onChangePage(page: number, perPage: number): void;
};

const BucketExplorer = (props: BucketExplorerProps) => {
  const { t } = useTranslation();
  const { workspace, objects, prefix, perPage, onChangePage } = props;
  const uploadFiles = useUploadFiles({ workspace, prefix });

  const directoryLinkGenerator = (item: BucketObject) =>
    `/workspaces/${encodeURIComponent(workspace.slug)}/files/${item.key}`;

  const actionsRenderer = (item: BucketObject) => (
    <div className="flex flex-1 justify-end gap-2">
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
      data={objects.items}
      fixedLayout={false}
      onDroppingFiles={uploadFiles}
      directoryLinkGenerator={directoryLinkGenerator}
      actionsRenderer={actionsRenderer}
      pagination={objects}
      perPage={perPage}
      onChangePage={onChangePage}
    />
  );
};

BucketExplorer.fragments = {
  workspace: gql`
    fragment BucketExplorer_workspace on Workspace {
      slug
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
