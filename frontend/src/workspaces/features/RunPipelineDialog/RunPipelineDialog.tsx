import { gql } from "@apollo/client";
import { PlayIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import useCacheKey from "core/hooks/useCacheKey";
import { PipelineType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import React, { useState } from "react";
import { runPipeline } from "workspaces/helpers/pipelines";
import PipelineVersionPicker from "../PipelineVersionPicker";
import ParameterField from "./ParameterField";
import {
  RunPipelineDialog_PipelineFragment,
  RunPipelineDialog_RunFragment,
} from "./RunPipelineDialog.generated";
import { ErrorAlert } from "core/components/Alert";
import RunPipelineFormFields from "./RunPipelineFormFields";
import useRunPipelineForm from "./useRunPipelineForm";

type RunPipelineDialogProps = {
  children(onClick: () => void): React.ReactNode;
  pipeline: RunPipelineDialog_PipelineFragment;
  run?: RunPipelineDialog_RunFragment;
};

const RunPipelineDialog = (props: RunPipelineDialogProps) => {
  const router = useRouter();
  const { pipeline, run, children } = props;
  const clearCache = useCacheKey(["pipelines", pipeline.code]);
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const onClose = () => setOpen(false);

  const goToRun = (runId: string) =>
    router.push(
      `/workspaces/${encodeURIComponent(
        pipeline.workspace!.slug,
      )}/pipelines/${encodeURIComponent(pipeline.code)}/runs/${encodeURIComponent(
        runId,
      )}`,
    );

  const onClick = () => {
    if (pipeline.type === PipelineType.ZipFile) {
      setOpen(true);
    } else {
      runPipeline(pipeline.id).then((run) => {
        goToRun(run.id);
        clearCache();
      });
    }
  };

  const formState = useRunPipelineForm({
    pipeline,
    run,
    open,
    async onSubmit(input) {
      const run = await runPipeline(
        pipeline.id,
        input.config,
        input.versionId,
        input.sendMailNotifications,
        input.enableDebugLogs,
      );
      await goToRun(run.id);
      clearCache();
      onClose();
    },
  });
  const { form, activeVersion } = formState;

  if (!pipeline.permissions.run) {
    return null;
  }

  if (!pipeline.currentVersion && open) {
    return (
      <ErrorAlert onClose={onClose}>
        {t("This pipeline has not been uploaded yet")}
      </ErrorAlert>
    );
  }
  return (
    <>
      {children(onClick)}

      {pipeline.type === PipelineType.ZipFile && (
        <Dialog
          open={open}
          onClose={onClose}
          centered={false}
          onSubmit={form.handleSubmit}
          maxWidth={"max-w-2xl"}
        >
          <Dialog.Title>{t("Run pipeline")}</Dialog.Title>
          {!activeVersion ? (
            <Dialog.Content className="flex items-center justify-center">
              <Spinner size="lg" />
            </Dialog.Content>
          ) : (
            <>
              <Dialog.Content>
                <RunPipelineFormFields pipeline={pipeline} state={formState} />
              </Dialog.Content>
              <Dialog.Actions className="flex-1 items-center">
                <Button variant="white" onClick={onClose}>
                  {t("Cancel")}
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={form.isSubmitting}
                  leadingIcon={<PlayIcon className="h-4 w-4" />}
                >
                  {t("Run")}
                </Button>
              </Dialog.Actions>
            </>
          )}
        </Dialog>
      )}
    </>
  );
};

RunPipelineDialog.fragments = {
  version: gql`
    fragment RunPipelineDialog_version on PipelineVersion {
      id
      versionName
      createdAt
      config
      user {
        displayName
      }
      parameters {
        ...ParameterField_parameter
      }
    }
    ${ParameterField.fragments.parameter}
  `,
  pipeline: gql`
    fragment RunPipelineDialog_pipeline on Pipeline {
      id
      workspace {
        slug
      }
      permissions {
        run
      }
      code
      type
      currentVersion {
        id
        versionName
        createdAt
        config
        user {
          displayName
        }
        parameters {
          ...ParameterField_parameter
        }
      }
      ...PipelineVersionPicker_pipeline
    }
    ${ParameterField.fragments.parameter}
    ${PipelineVersionPicker.fragments.pipeline}
  `,
  run: gql`
    fragment RunPipelineDialog_run on PipelineRun {
      id
      config
      version {
        id
        versionName
        createdAt
        parameters {
          ...ParameterField_parameter
        }
        user {
          displayName
        }
      }
    }
    ${ParameterField.fragments.parameter}
  `,
};

export default RunPipelineDialog;
