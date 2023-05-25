import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useDeletePipelineVersionMutation } from "workspaces/graphql/mutations.generated";
import { gql } from "@apollo/client";
import {
  DeletePipelineVersion_PipelineFragment,
  DeletePipelineVersion_VersionFragment,
} from "./DeletePipelineVersionDialog.generated";
import { DeletePipelineVersionError } from "graphql-types";
import useCacheKey from "core/hooks/useCacheKey";
import { useRouter } from "next/router";

type DeletePipelineVersionDialogProps = {
  onClose(): void;
  open: boolean;
  pipeline: DeletePipelineVersion_PipelineFragment;
  version: DeletePipelineVersion_VersionFragment;
};

const DeletePipelineVersionDialog = (
  props: DeletePipelineVersionDialogProps
) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { open, onClose, pipeline, version } = props;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const clearCache = useCacheKey(["pipelines", pipeline.code]);

  const [deletePipelineVersion] = useDeletePipelineVersionMutation();

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await deletePipelineVersion({
      variables: {
        input: {
          pipelineId: pipeline.id,
          versionId: version.id,
        },
      },
    });

    if (!data?.deletePipelineVersion) {
      throw new Error("Unknown error.");
    }

    if (data.deletePipelineVersion.success) {
      setIsSubmitting(false);
      router.reload();
      clearCache();
      onClose();
    }
    if (
      data.deletePipelineVersion.errors.includes(
        DeletePipelineVersionError.PermissionDenied
      )
    ) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>{t("Delete version")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          {t(
            "You're about to delete version {{number}} of pipeline {{name}}.",
            {
              number: version.number,
              name: pipeline.name,
            }
          )}
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" type="button" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Delete")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

DeletePipelineVersionDialog.fragments = {
  pipeline: gql`
    fragment DeletePipelineVersion_pipeline on Pipeline {
      id
      code
      name
    }
  `,
  version: gql`
    fragment DeletePipelineVersion_version on PipelineVersion {
      id
      number
    }
  `,
};

export default DeletePipelineVersionDialog;
