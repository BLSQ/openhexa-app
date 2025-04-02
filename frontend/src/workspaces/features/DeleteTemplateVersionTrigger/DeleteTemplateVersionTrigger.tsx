import { gql } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { ReactElement } from "react";
import { DeleteTemplateVersionTrigger_VersionFragment } from "./DeleteTemplateVersionTrigger.generated";
import { deleteTemplateVersion } from "workspaces/helpers/templates";

type DeletePipelineVersionTriggerProps = {
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  confirmMessage?: string;
  version: DeleteTemplateVersionTrigger_VersionFragment;
};

const DeleteTemplateVersionTrigger = (
  props: DeletePipelineVersionTriggerProps,
) => {
  const { t } = useTranslation();
  const {
    children,
    version,
    confirmMessage = t(
      'Are you sure you want to delete the version "{{versionNumber}}"?',
      {
        versionNumber: version.versionNumber,
      },
    ),
  } = props;

  const clearCache = useCacheKey(["templates", version.template.id]);

  const onClick = async () => {
    if (window.confirm(confirmMessage)) {
      await deleteTemplateVersion(version.id);
      clearCache();
    }
  };
  if (!version.permissions.delete) {
    return null;
  }
  return children({ onClick });
};

DeleteTemplateVersionTrigger.fragments = {
  version: gql`
    fragment DeleteTemplateVersionTrigger_version on PipelineTemplateVersion {
      id
      versionNumber
      template {
        id
      }
      permissions {
        delete
      }
    }
  `,
};

export default DeleteTemplateVersionTrigger;
