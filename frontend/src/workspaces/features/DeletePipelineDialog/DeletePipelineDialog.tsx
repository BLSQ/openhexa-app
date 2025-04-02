import { gql } from "@apollo/client";
import {
  PipelineDelete_PipelineFragment,
  PipelineDelete_WorkspaceFragment,
} from "./DeletePipelineDialog.generated";
import { Trans, useTranslation } from "react-i18next";
import { useRouter } from "next/router";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import useCacheKey from "core/hooks/useCacheKey";
import { PipelineError } from "graphql/types";
import { useState } from "react";
import { useDeletePipelineMutation } from "workspaces/graphql/mutations.generated";
import Dialog from "core/components/Dialog";

type DeletePipelineDialogProps = {
  open: boolean;
  onClose: () => void;
  pipeline: PipelineDelete_PipelineFragment;
  workspace: PipelineDelete_WorkspaceFragment;
};

const DeletePipelineDialog = (props: DeletePipelineDialogProps) => {
  const { t } = useTranslation();
  const { open, onClose, pipeline, workspace } = props;
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const clearCache = useCacheKey(["pipelines", pipeline.code]);

  const [deletePipeline] = useDeletePipelineMutation();

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await deletePipeline({
      variables: {
        input: {
          id: pipeline.id,
        },
      },
    });

    if (!data?.deletePipeline) {
      throw new Error("Unknown error.");
    }

    if (data.deletePipeline.success) {
      setIsSubmitting(false);
      router.push({
        pathname: "/workspaces/[workspaceSlug]/pipelines",
        query: { workspaceSlug: workspace.slug },
      });
      clearCache();
    }
    if (data.deletePipeline.errors.includes(PipelineError.PermissionDenied)) {
      setIsSubmitting(false);
      window.alert(t("Cannot delete a running or queued pipeline."));
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>{t("Delete pipeline")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          <Trans>
            Are you sure you want to delete pipeline <b>{pipeline.name}</b> ?
          </Trans>
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
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

DeletePipelineDialog.fragment = {
  pipeline: gql`
    fragment PipelineDelete_pipeline on Pipeline {
      id
      name
      code
    }
  `,
  workspace: gql`
    fragment PipelineDelete_workspace on Workspace {
      slug
    }
  `,
};

export default DeletePipelineDialog;
