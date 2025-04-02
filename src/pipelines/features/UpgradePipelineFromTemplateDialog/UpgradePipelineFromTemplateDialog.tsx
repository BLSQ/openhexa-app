import { useTranslation } from "react-i18next";
import Button from "core/components/Button";
import React, { useState } from "react";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { gql } from "@apollo/client";
import MarkdownViewer from "core/components/MarkdownViewer";
import Time from "core/components/Time";
import { toast } from "react-toastify";
import { UpgradePipelineFromTemplateDialog_PipelineFragment } from "./UpgradePipelineFromTemplateDialog.generated";
import { useUpgradePipelineVersionFromTemplateMutation } from "../../graphql/mutations.generated";

type UpgradePipelineFromTemplateDialogProps = {
  pipeline: UpgradePipelineFromTemplateDialog_PipelineFragment;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
};

const UpgradePipelineFromTemplateDialog = ({
  pipeline: { id: pipelineId, newTemplateVersions },
  open,
  onClose,
  onSuccess,
}: UpgradePipelineFromTemplateDialogProps) => {
  const { t } = useTranslation();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [upgradePipeline] = useUpgradePipelineVersionFromTemplateMutation();

  if (!open) return null;

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await upgradePipeline({
      variables: {
        input: {
          pipelineId,
        },
      },
    });
    if (!data?.upgradePipelineVersionFromTemplate) {
      toast.error(t("Unknown error upgrading pipeline"));
    }
    if (data?.upgradePipelineVersionFromTemplate.success) {
      onSuccess();
      toast.success(t("Pipeline upgraded successfully"));
      onClose();
    } else {
      toast.error(t("Error upgrading pipeline"));
    }
    setIsSubmitting(false);
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>{t("Upgrade to latest template version")}</Dialog.Title>
      <Dialog.Content>
        {newTemplateVersions?.map((version) => (
          <div
            key={version.id}
            className="mb-2 border rounded-md shadow-sm p-4"
          >
            <div className="flex justify-start">
              <div className="font-bold text-lg">
                {t("Version")} {version.versionNumber}
              </div>
              <div className="text-gray-500 ml-1 mt-1 text-sm">
                ({t("published")} <Time relative datetime={version.createdAt} />
                )
              </div>
            </div>
            {version.changelog && (
              <div className="text-sm">
                <MarkdownViewer sm={true} markdown={version.changelog} />
              </div>
            )}
          </div>
        ))}
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button
          disabled={isSubmitting}
          type={"submit"}
          onClick={onSubmit}
          leadingIcon={isSubmitting ? <Spinner size="xs" /> : undefined}
        >
          {t("Upgrade")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

UpgradePipelineFromTemplateDialog.fragments = {
  pipeline: gql`
    fragment UpgradePipelineFromTemplateDialog_pipeline on Pipeline {
      id
      code
      newTemplateVersions {
        id
        versionNumber
        changelog
        createdAt
      }
    }
  `,
};

export default UpgradePipelineFromTemplateDialog;
