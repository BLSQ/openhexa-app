import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import { GeneratePipelineWebhookUrlError } from "graphql/types";
import { AlertType, displayAlert } from "core/helpers/alert";
import { ExclamationCircleIcon } from "@heroicons/react/24/outline";
import { GeneratePipelineWebhookUrlDialog_PipelineFragment } from "./GeneratePipelineWebhookUrlDialog.generated";
import { useGenerateWebhookPipelineWebhookUrlMutation } from "workspaces/graphql/mutations.generated";

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

  const [generateWebhookUrl] = useGenerateWebhookPipelineWebhookUrlMutation();
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
      displayAlert(t("New url successfully created"), AlertType.info);
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
      <Dialog.Title>{t("Generate new webhook url")}</Dialog.Title>
      <Dialog.Content className="space-y-2 py-2">
        <p>{t("You are about to replace the pipeline webhook url.")}</p>
        <p>
          {t(
            "After creating a new url, you will have to update all the services/applications that are using the current webhook url.",
          )}
        </p>
        <p className="flex items-center gap-1 font-medium">
          <ExclamationCircleIcon className="inline-block h-6 w-6 text-amber-400" />
          {t("This action cannot be undone.")}
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" type="button" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Generate new url")}
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
