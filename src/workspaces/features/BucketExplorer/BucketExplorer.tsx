import { gql } from "@apollo/client";
import {
  ArrowDownTrayIcon,
  DocumentIcon,
  FolderIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import Filesize from "core/components/Filesize";
import Link from "core/components/Link";
import SimplePagination from "core/components/Pagination/SimplePagination";
import Spinner from "core/components/Spinner";
import { BucketObjectType } from "graphql-types";
import { useTranslation } from "react-i18next";
import DeleteBucketObject from "../DeleteBucketObject";
import DownloadBucketObject from "../DownloadBucketObject";
import {
  BucketExplorer_ObjectsFragment,
  BucketExplorer_WorkspaceFragment,
} from "./BucketExplorer.generated";

type BucketExplorerProps = {
  workspace: BucketExplorer_WorkspaceFragment;
  objects: BucketExplorer_ObjectsFragment;
  prefix?: string | null;
  perPage: number;
  onChangePage(page: number): void;
};

const BucketExplorer = (props: BucketExplorerProps) => {
  const { t } = useTranslation();
  const { workspace, objects, perPage, onChangePage } = props;
  return (
    <>
      <DataGrid
        data={objects.items}
        defaultPageSize={perPage}
        fixedLayout={false}
      >
        <BaseColumn id="name" label={t("Name")}>
          {(value) =>
            value.type === BucketObjectType.Directory ? (
              <Link
                noStyle
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug
                )}/files/${value.key}`}
                className="flex items-center gap-1.5 font-medium text-gray-700 hover:text-gray-800"
              >
                <FolderIcon className="h-5 w-5" />
                {value.name}
              </Link>
            ) : (
              <div className="flex items-center gap-1.5 font-medium  text-gray-700">
                <DocumentIcon className="h-5 w-5" />
                {value.name}
              </div>
            )
          }
        </BaseColumn>
        <BaseColumn id="size" label={t("Size")}>
          {(value) =>
            value.type === BucketObjectType.Directory ? (
              <span>-</span>
            ) : (
              <Filesize size={value.size} />
            )
          }
        </BaseColumn>
        <DateColumn accessor={"updatedAt"} label={t("Last updated")} relative />
        <BaseColumn id="actions">
          {(value) => (
            <div className="flex flex-1 justify-end gap-2">
              {
                <DeleteBucketObject workspace={workspace} object={value}>
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
              }
              {value.type === BucketObjectType.File && (
                <DownloadBucketObject object={value} workspace={workspace}>
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
          )}
        </BaseColumn>
      </DataGrid>
      {objects.items.length ? (
        <SimplePagination
          className="px-4"
          hasNextPage={objects.hasNextPage}
          hasPreviousPage={objects.hasPreviousPage}
          page={objects.pageNumber}
          onChange={onChangePage}
        />
      ) : null}
    </>
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
