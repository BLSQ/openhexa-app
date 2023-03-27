import { gql, useQuery } from "@apollo/client";
import { CheckIcon } from "@heroicons/react/24/outline";
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

type PipelineVersionsDialogProps = {
  open: boolean;
  onClose: () => void;
  pipeline: PipelineVersionsDialog_PipelineFragment;
};

const PipelineVersionsDialog = (props: PipelineVersionsDialogProps) => {
  const { open, onClose, pipeline } = props;
  const { t } = useTranslation();
  const { data, loading } = useQuery<
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
              entrypoint
            }
          }
        }
      }
      ${User.fragments.user}
    `,
    {
      variables: { pipelineId: pipeline.id },
    }
  );
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
            <TextColumn
              id="entrypoint"
              accessor={"entrypoint"}
              label={t("Entrypoint")}
            />
            <BaseColumn id="default" label={t("Default")}>
              {(item) => <CheckIcon className="h-4 w-4" />}
            </BaseColumn>
            <BaseColumn id="actions">
              {({ row }) => (
                <Button variant="white" size="sm" disabled>
                  {t("Set as default")}
                </Button>
              )}
            </BaseColumn>
          </DataGrid>
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
    }
  `,
};

export default PipelineVersionsDialog;
