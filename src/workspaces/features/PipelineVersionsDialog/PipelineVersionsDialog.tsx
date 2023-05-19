import { gql, useLazyQuery } from "@apollo/client";
import { CheckIcon, TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import User from "core/features/User";
import { useTranslation } from "react-i18next";
import {
  PipelineVersionsDialogQuery,
  PipelineVersionsDialogQueryVariables,
  PipelineVersionsDialog_PipelineFragment,
} from "./PipelineVersionsDialog.generated";
import { useEffect, useMemo, useState } from "react";
import DeletePipelineVersionDialog from "../DeletePipelineVersionDialog";
import useCacheKey from "core/hooks/useCacheKey";
import { useRouter } from "next/router";
import useMe from "identity/hooks/useMe";

type PipelineVersionsDialogProps = {
  open: boolean;
  onClose: () => void;
  pipeline: PipelineVersionsDialog_PipelineFragment;
};

const PipelineVersionsDialog = (props: PipelineVersionsDialogProps) => {
  const { open, onClose, pipeline } = props;
  const me = useMe();
  const { t } = useTranslation();
  const router = useRouter();
  const [selectedPipelineVersion, setSelectedPipelineVersion] = useState<{
    id: string;
    number: number;
  } | null>();

  const [refetch, { data, loading }] = useLazyQuery<
    PipelineVersionsDialogQuery,
    PipelineVersionsDialogQueryVariables
  >(
    gql`
      query PipelineVersionsDialog($pipelineId: UUID!) {
        pipeline(id: $pipelineId) {
          id
          versions {
            totalItems
            items {
              id
              number
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
      },
    }
  );

  useCacheKey(["pipelines", pipeline.code], () => router.reload());
  useEffect(() => {
    if (open) {
      refetch({ variables: { pipelineId: pipeline.id } });
    }
  }, [open, pipeline.id, refetch]);

  const canDeletePipeline = useMemo(() => {
    return (
      pipeline.permissions.deleteVersion &&
      data?.pipeline?.versions.items &&
      data.pipeline?.versions.items.length > 1
    );
  }, [data, pipeline]);

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
            defaultPageSize={10}
            totalItems={data.pipeline?.versions.totalItems ?? 0}
            data={data.pipeline?.versions.items ?? []}
            fixedLayout={false}
          >
            <TextColumn
              className="font-bold"
              id="number"
              accessor={"number"}
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
                          number: item.number,
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
