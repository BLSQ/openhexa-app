import { gql, useMutation } from "@apollo/client";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { GeneratePipelineWebhookUrlError } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import {
  GeneratePipelineWebhookUrlDialog_PipelineFragment,
  GenerateWebhookPipelineWebhookUrlMutation,
  GenerateWebhookPipelineWebhookUrlMutationVariables,
} from "./GeneratePipelineWebhookUrlDialog.generated";

type GeneratePipelineWebhookUrlDialogProps = {
  onClose(): void;
  open: boolean;
  pipeline: GeneratePipelineWebhookUrlDialog_PipelineFragment;
};

const GeneratePipelineWebhookUrlDialog = (
  props: GeneratePipelineWebhookUrlDialogProps,
) => {
  const { open, onClose, pipeline } = props;
  const { t } = useTranslation();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [generateWebhookUrl] = useMutation<
    GenerateWebhookPipelineWebhookUrlMutation,
    GenerateWebhookPipelineWebhookUrlMutationVariables
  >(gql`
    mutation generateWebhookPipelineWebhookUrl(
      $input: GeneratePipelineWebhookUrlInput!
    ) {
      generatePipelineWebhookUrl(input: $input) {
        success
        errors
        pipeline {
          id
          code
          webhookUrl
        }
      }
    }
  `);
  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await generateWebhookUrl({
      variables: {
        input: {
          id: pipeline.id,
        },
      },
    });

    if (!data?.generatePipelineWebhookUrl) {
      throw new Error("Unknown error.");
    }

    if (data.generatePipelineWebhookUrl.success) {
      onClose();
      setIsSubmitting(false);
    }
    if (
      data.generatePipelineWebhookUrl.errors.includes(
        GeneratePipelineWebhookUrlError.PermissionDenied,
      )
    ) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>{t("Generate new webhook URL")}</Dialog.Title>
      <Dialog.Content className="space-y-2 py-2">
        <p>{t("You are about to replace the pipeline webhook URL.")}</p>
        <p>
          {t(
            "After creating a new URL, you will have to update all the services/applications that are using the current webhook URK.",
          )}
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Generate")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

GeneratePipelineWebhookUrlDialog.fragments = {
  pipeline: gql`
    fragment GeneratePipelineWebhookUrlDialog_pipeline on Pipeline {
      id
      code
    }
  `,
};

export default GeneratePipelineWebhookUrlDialog;
