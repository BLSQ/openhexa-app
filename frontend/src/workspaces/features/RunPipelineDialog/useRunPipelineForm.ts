import { ensureArray } from "core/helpers/array";
import useForm from "core/hooks/useForm";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo, useState } from "react";
import {
  convertParametersToPipelineInput,
  getDisabledParameterCodes,
  getParameterDisablers,
  isConnectionParameter,
} from "workspaces/helpers/pipelines";
import {
  RunPipelineDialog_PipelineFragment,
  RunPipelineDialog_RunFragment,
  RunPipelineDialog_VersionFragment,
} from "./RunPipelineDialog.generated";

export type RunPipelineInput = {
  config: { [key: string]: any };
  versionId: string;
  sendMailNotifications: boolean;
  enableDebugLogs: boolean;
};

type UseRunPipelineFormOptions = {
  pipeline: RunPipelineDialog_PipelineFragment;
  run?: RunPipelineDialog_RunFragment;
  // Resets the selected version each time the form is (re)opened.
  open: boolean;
  onSubmit(input: RunPipelineInput): Promise<void>;
};

const useRunPipelineForm = ({
  pipeline,
  run,
  open,
  onSubmit,
}: UseRunPipelineFormOptions) => {
  const { t } = useTranslation();
  const [activeVersion, setActiveVersion] =
    useState<RunPipelineDialog_VersionFragment | null>(
      run?.version ?? pipeline.currentVersion ?? null,
    );

  useEffect(() => {
    if (open) {
      setActiveVersion(run?.version ?? pipeline.currentVersion ?? null);
    }
  }, [open]);

  const form = useForm<{ [key: string]: any }>({
    async onSubmit(values) {
      const { sendMailNotifications, enableDebugLogs, ...params } = values;
      if (!activeVersion) {
        throw new Error("No active version found");
      }
      await onSubmit({
        config: convertParametersToPipelineInput(activeVersion, params),
        versionId: activeVersion.id,
        sendMailNotifications,
        enableDebugLogs,
      });
    },
    getInitialState() {
      if (run) {
        return {
          sendMailNotifications: true,
          enableDebugLogs: false,
          ...run.config,
        };
      } else if (activeVersion) {
        return {
          sendMailNotifications: true,
          enableDebugLogs: false,
          ...activeVersion.config,
        };
      }
    },
    validate(values) {
      const errors = {} as any;
      if (!activeVersion) {
        return errors;
      }
      const disabledCodes = getDisabledParameterCodes(
        activeVersion.parameters,
        values,
      );
      const normalizedValues = convertParametersToPipelineInput(
        activeVersion,
        values,
        disabledCodes,
      );
      for (const parameter of activeVersion.parameters) {
        if (disabledCodes.has(parameter.code)) {
          continue;
        }
        const val = normalizedValues[parameter.code];
        if (parameter.type === "int" || parameter.type === "float") {
          if (ensureArray(val).length === 0 && parameter.required) {
            errors[parameter.code] = t("This field is required");
          } else if (ensureArray(val).some((v) => isNaN(v))) {
            errors[parameter.code] = t("This field must contain only numbers");
          }
        }

        if (
          ["str", "dataset", "file"].includes(parameter.type) &&
          parameter.required &&
          ensureArray(val).length === 0
        ) {
          errors[parameter.code] = t("This field is required");
        }
        if (
          isConnectionParameter(parameter.type) &&
          parameter.required &&
          !val
        ) {
          errors[parameter.code] = t("This field is required");
        }
      }
      return errors;
    },
  });

  useEffect(() => {
    form.resetForm();
  }, [form, activeVersion]);

  const parameterDisablers = useMemo(
    () => getParameterDisablers(activeVersion?.parameters ?? [], form.formData),
    [activeVersion, form.formData],
  );

  const parameterNameByCode = useMemo(() => {
    const map: { [code: string]: string } = {};
    for (const param of activeVersion?.parameters ?? []) {
      map[param.code] = param.name;
    }
    return map;
  }, [activeVersion]);

  return {
    form,
    activeVersion,
    setActiveVersion,
    parameterDisablers,
    parameterNameByCode,
  };
};

export type RunPipelineFormState = ReturnType<typeof useRunPipelineForm>;

export default useRunPipelineForm;
