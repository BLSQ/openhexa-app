import { Trans, useTranslation } from "react-i18next";
import Button from "core/components/Button";
import { PipelineTemplateError } from "graphql/types";
import Dialog from "core/components/Dialog";
import { toast } from "react-toastify";
import { useDeletePipelineTemplateMutation } from "workspaces/graphql/mutations.generated";
import useCacheKey from "core/hooks/useCacheKey";
import { gql } from "@apollo/client";
import { PipelineTemplateDialog_PipelineTemplateFragment } from "./DeleteTemplateDialog.generated";

type DeleteTemplateDialogProps = {
  open: boolean;
  pipelineTemplate: PipelineTemplateDialog_PipelineTemplateFragment;
  onClose: () => void;
};

const DeleteTemplateDialog = (props: DeleteTemplateDialogProps) => {
  const { t } = useTranslation();
  const {
    open,
    pipelineTemplate: { id, name },
    onClose,
  } = props;

  const clearTemplateCache = useCacheKey(["templates"]);

  const [deletePipelineTemplate] = useDeletePipelineTemplateMutation();

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
        <p>
          <Trans>Are you sure you want to delete the template {name}?</Trans>
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button
          onClick={() => {
            deleteTemplate().then(() => onClose());
          }}
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
