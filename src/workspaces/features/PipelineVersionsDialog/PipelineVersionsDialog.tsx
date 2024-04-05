import { gql, useQuery } from "@apollo/client";
import { CheckIcon, TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import User from "core/features/User";
import { useTranslation } from "next-i18next";
import {
  PipelineVersionsDialogQuery,
  PipelineVersionsDialogQueryVariables,
  PipelineVersionsDialog_PipelineFragment,
} from "./PipelineVersionsDialog.generated";
import { useMemo, useState } from "react";
import DeletePipelineVersionDialog from "../DeletePipelineVersionDialog";
import useMe from "identity/hooks/useMe";

type PipelineVersionsDialogProps = {
  open: boolean;
  onClose: () => void;
  pipeline: PipelineVersionsDialog_PipelineFragment;
};

const DEFAULT_PAGE_SIZE = 5;

const PipelineVersionsDialog = (props: PipelineVersionsDialogProps) => {
  const { open, onClose, pipeline } = props;
  const me = useMe();
  const { t } = useTranslation();
  const [selectedPipelineVersion, setSelectedPipelineVersion] = useState<{
    id: string;
    name: string;
  } | null>();

  const { data, refetch, loading } = useQuery<
    PipelineVersionsDialogQuery,
    PipelineVersionsDialogQueryVariables
  >(
    gql`
      query PipelineVersionsDialog(
        $pipelineId: UUID!
        $page: Int
        $perPage: Int
      ) {
        pipeline(id: $pipelineId) {
          id
          versions(page: $page, perPage: $perPage) {
            totalItems
            items {
              id
              name
              user {
                ...User_user
              }
            }
          }
        }
      }
      ${User.fragments.user}
    `,
    {
      variables: {
        pipelineId: pipeline.id,
        perPage: DEFAULT_PAGE_SIZE,
      },
    },
  );

  const canDeletePipeline = useMemo(() => {
    return (
      pipeline.permissions.deleteVersion &&
      data?.pipeline?.versions.items &&
      data.pipeline?.versions.items.length > 1
    );
  }, [data, pipeline]);

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      pipelineId: pipeline.id,
      page,
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-3xl">
      <Dialog.Title>{t("Pipeline versions")}</Dialog.Title>
      {loading || !data ? (
        <Dialog.Content className="items-center">
          <Spinner />
        </Dialog.Content>
      ) : (
        <Dialog.Content>
          <DataGrid
            defaultPageSize={DEFAULT_PAGE_SIZE}
            totalItems={data.pipeline?.versions.totalItems ?? 0}
            data={data.pipeline?.versions.items ?? []}
            fixedLayout={false}
            fetchData={onChangePage}
          >
            <TextColumn
              className="font-bold"
              id="name"
              accessor={"name"}
              label={t("Version")}
            />
            <UserColumn accessor="user" id="user" label={t("User")} />
            <BaseColumn id="default" label={t("Default")}>
              {(item) => <CheckIcon className="h-4 w-4" />}
            </BaseColumn>
            <BaseColumn id="actions" className="flex justify-end gap-x-2">
              {(item) => (
                <>
                  <Button variant="white" size="sm" disabled>
                    {t("Set as default")}
                  </Button>
                  {canDeletePipeline && me.user?.id === item.user.id && (
                    <Button
                      size="sm"
                      className="bg-red-700 hover:bg-red-700 focus:ring-red-500"
                      onClick={() => {
                        setSelectedPipelineVersion({
                          id: item.id,
                          name: item.name,
                        });
                      }}
                    >
                      <TrashIcon className="w-4" />
                    </Button>
                  )}
                </>
              )}
            </BaseColumn>
          </DataGrid>
          {selectedPipelineVersion && (
            <DeletePipelineVersionDialog
              open
              pipeline={pipeline}
              version={selectedPipelineVersion}
              onClose={() => setSelectedPipelineVersion(null)}
            />
          )}
        </Dialog.Content>
      )}
      <Dialog.Actions>
        <Button onClick={onClose}>{t("Close")}</Button>
      </Dialog.Actions>
    </Dialog>
  );
};

PipelineVersionsDialog.fragments = {
  pipeline: gql`
    fragment PipelineVersionsDialog_pipeline on Pipeline {
      id
      code
      workspace {
        slug
      }
      permissions {
        deleteVersion
      }
    }
  `,
};

export default PipelineVersionsDialog;
