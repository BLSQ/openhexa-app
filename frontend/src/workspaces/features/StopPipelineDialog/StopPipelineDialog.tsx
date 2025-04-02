import { Trans, useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import useCacheKey from "core/hooks/useCacheKey";
import { PipelineError } from "graphql/types";
import { useState } from "react";

import Dialog from "core/components/Dialog";
import { useStopPipelineMutation } from "workspaces/graphql/mutations.generated";
import { gql } from "@apollo/client";
import {
  StopPipelineDialog_PipelineFragment,
  StopPipelineDialog_RunFragment,
} from "./StopPipelineDialog.generated";

type StopPipelineDialogProps = {
  open: boolean;
  onClose: () => void;
  run: StopPipelineDialog_RunFragment;
  pipeline: StopPipelineDialog_PipelineFragment;
};

const StopPipelineDialog = (props: StopPipelineDialogProps) => {
  const { t } = useTranslation();
  const { open, run, pipeline, onClose } = props;
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const clearCache = useCacheKey(["pipelines", pipeline.code]);

  const [stopPipeline] = useStopPipelineMutation();

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await stopPipeline({
      variables: {
        input: {
          runId: run.id,
        },
      },
    });

    if (!data?.stopPipeline) {
      throw new Error("Unknown error.");
    }

    if (data.stopPipeline.success) {
      setIsSubmitting(false);
      clearCache();
      onClose();
    }
    if (data.stopPipeline.errors.includes(PipelineError.PermissionDenied)) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>
        {t("Stop {{name}} execution", { name: pipeline.code })}
      </Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          <Trans>
            Be aware that this action is irreversible and the execution cannot
            be resumed. It can lead to an inconsistent state if there was any
            database or filesystem operation.
          </Trans>
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Stop")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

StopPipelineDialog.fragments = {
  run: gql`
    fragment StopPipelineDialog_run on PipelineRun {
      id
    }
  `,
  pipeline: gql`
    fragment StopPipelineDialog_pipeline on Pipeline {
      code
    }
  `,
};

export default StopPipelineDialog;
