import { gql } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { ReactElement } from "react";
import { deletePipelineVersion } from "workspaces/helpers/pipelines";
import { DeletePipelineVersionTrigger_VersionFragment } from "./DeletePipelineVersionTrigger.generated";

type DeletePipelineVersionTriggerProps = {
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  confirmMessage?: string;
  version: DeletePipelineVersionTrigger_VersionFragment;
};

const DeletePipelineVersionTrigger = (
  props: DeletePipelineVersionTriggerProps,
) => {
  const { t } = useTranslation();
  const {
    children,
    version,
    confirmMessage = t(
      'Are you sure you want to delete the version "{{name}}"?',
      {
        name: version.name,
      },
    ),
  } = props;

  const clearCache = useCacheKey(["pipelines", version.pipeline.id]);

  const onClick = async () => {
    if (window.confirm(confirmMessage)) {
      await deletePipelineVersion(version.id);
      clearCache();
    }
  };
  if (!version.permissions.delete) {
    return null;
  }
  return children({ onClick });
};

DeletePipelineVersionTrigger.fragments = {
  version: gql`
    fragment DeletePipelineVersionTrigger_version on PipelineVersion {
      id
      name
      pipeline {
        id
      }
      permissions {
        delete
      }
    }
  `,
};

export default DeletePipelineVersionTrigger;
