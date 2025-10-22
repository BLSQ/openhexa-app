import { Trans, useTranslation } from "react-i18next";
import Button from "core/components/Button";
import { PipelineTemplateError } from "graphql/types";
import Dialog from "core/components/Dialog";
import { toast } from "react-toastify";
import useCacheKey from "core/hooks/useCacheKey";
import { gql } from "@apollo/client";
import { PipelineTemplateDialog_PipelineTemplateFragment } from "./DeleteTemplateDialog.generated";
import { useState } from "react";
import { useMutation } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const DeletePipelineTemplateDoc = graphql(`
mutation deletePipelineTemplate($input: DeletePipelineTemplateInput!) {
  deletePipelineTemplate(input: $input) {
    success
    errors
  }
}
`);

type DeleteTemplateDialogProps = {
  open: boolean;
  pipelineTemplate: PipelineTemplateDialog_PipelineTemplateFragment;
  onDelete?: () => void;
  onClose: () => void;
};

const DeleteTemplateDialog = (props: DeleteTemplateDialogProps) => {
  const { t } = useTranslation();
  const {
    open,
    pipelineTemplate: { id, name },
    onDelete,
    onClose,
  } = props;

  const [confirmationInput, setConfirmationInput] = useState("");

  const clearTemplateCache = useCacheKey(["templates"]);

  const [deletePipelineTemplate] = useMutation(DeletePipelineTemplateDoc);

  const deleteTemplate = async () => {
    const { data } = await deletePipelineTemplate({
      variables: {
        input: {
          id,
        },
      },
    });

    if (!data?.deletePipelineTemplate) {
      throw new Error("Unknown error.");
    }

    if (data.deletePipelineTemplate.success) {
      clearTemplateCache();
      onClose();
      toast.success(t("Successfully deleted template {{ name }}", { name }));
    }
    if (
      data.deletePipelineTemplate.errors.includes(
        PipelineTemplateError.PermissionDenied,
      )
    ) {
      toast.error(
        t("You are not allowed to delete the template {{ name }}", { name }),
      );
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>{t("Delete template")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Trans>
          <p>Are you sure that you want to delete the template {name}?</p>
          <p>It will not be available anymore in other workspaces.</p>
          <p>Please enter the template name to confirm deletion:</p>
        </Trans>
        <input
          type="text"
          value={confirmationInput}
          placeholder={name}
          onChange={(e) => setConfirmationInput(e.target.value)}
          className="w-full border border-gray-300 rounded-sm px-2 py-1"
        />
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button
          onClick={() => {
            deleteTemplate().then(() => onDelete && onDelete());
          }}
          disabled={confirmationInput.toLowerCase() !== name.toLowerCase()}
        >
          {t("Delete")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

DeleteTemplateDialog.fragment = {
  pipelineTemplate: gql`
    fragment PipelineTemplateDialog_pipelineTemplate on PipelineTemplate {
      id
      name
    }
  `,
};

export default DeleteTemplateDialog;
