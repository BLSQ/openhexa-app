import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import router from "next/router";
import Button from "core/components/Button";
import { ButtonProps } from "core/components/Button/Button";
import useCacheKey from "core/hooks/useCacheKey";
import { useCreatePipelineFromTemplateVersionMutation } from "pipelines/graphql/mutations.generated";
import { CreatePipelineFromTemplateVersionError } from "graphql/types";
import { MouseEvent } from "react";

type PipelineCreateButtonProps = Omit<ButtonProps, "disabled"> & {
  workspaceSlug: string;
  pipelineTemplateVersionId: string;
};

const PipelineCreateFromTemplateButton = ({
  workspaceSlug,
  pipelineTemplateVersionId,
  children,
  onClick,
  ...buttonProps
}: PipelineCreateButtonProps) => {
  const { t } = useTranslation();
  const clearCache = useCacheKey(["pipelines"]);
  const [createPipelineFromTemplateVersion, { loading }] =
    useCreatePipelineFromTemplateVersionMutation();

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    onClick?.(event);
    createPipelineFromTemplateVersion({
      variables: {
        input: {
          pipelineTemplateVersionId,
          workspaceSlug,
        },
      },
    })
      .then((result) => {
        const success = result.data?.createPipelineFromTemplateVersion?.success;
        const errors = result.data?.createPipelineFromTemplateVersion?.errors;
        const pipeline =
          result.data?.createPipelineFromTemplateVersion?.pipeline;

        if (success && pipeline) {
          clearCache();
          toast.success(
            t("Successfully created pipeline {{pipelineName}}", {
              pipelineName: pipeline.name,
            }),
          );
          router
            .push(
              `/workspaces/${encodeURIComponent(
                workspaceSlug,
              )}/pipelines/${encodeURIComponent(pipeline.code)}`,
            )
            .then();
        } else if (
          errors?.includes(
            CreatePipelineFromTemplateVersionError.PermissionDenied,
          )
        ) {
          toast.error(t("You are not allowed to create a pipeline."));
        } else {
          toast.error(t("Failed to create pipeline"));
        }
      })
      .catch(() => {
        toast.error(t("Failed to create pipeline"));
      });
  };

  return (
    <Button {...buttonProps} onClick={handleClick} disabled={loading}>
      {children ?? t("Create pipeline")}
    </Button>
  );
};

export default PipelineCreateFromTemplateButton;
