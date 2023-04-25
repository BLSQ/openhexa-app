import { gql } from "@apollo/client";
import { PlayIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Alert from "core/components/Alert";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Input from "core/components/forms/Input";
import SimpleSelect from "core/components/forms/SimpleSelect";
import Switch from "core/components/Switch";
import useForm from "core/hooks/useForm";
import { useRouter } from "next/router";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Parameter, runPipeline } from "workspaces/helpers/pipelines";
import PipelineVersionPicker from "../PipelineVersionPicker";
import {
  RunPipelineDialog_PipelineFragment,
  RunPipelineDialog_RunFragment,
  RunPipelineDialog_VersionFragment,
} from "./RunPipelineDialog.generated";
import { PipelineVersion } from "graphql-types";
import ParameterField from "./ParameterField";
import useCacheKey from "core/hooks/useCacheKey";

type RunPipelineDialogProps = {
  open: boolean;
  onClose: () => void;
  pipeline: RunPipelineDialog_PipelineFragment;
} & (
  | {}
  | { run: RunPipelineDialog_RunFragment }
  | { version: RunPipelineDialog_VersionFragment }
);

const RunPipelineDialog = (props: RunPipelineDialogProps) => {
  const router = useRouter();
  const { open, onClose, pipeline } = props;
  const clearCache = useCacheKey(["pipelines", pipeline.code]);

  const form = useForm<{ version: PipelineVersion; [key: string]: any }>({
    async onSubmit(values) {
      const { version, ...params } = values;
      const run = await runPipeline(pipeline.id, params, version?.number);
      router.push(
        `/workspaces/${encodeURIComponent(
          router.query.workspaceSlug as string
        )}/pipelines/${encodeURIComponent(
          pipeline.id
        )}/runs/${encodeURIComponent(run.id)}`
      );
      clearCache();
      onClose();
    },
    getInitialState() {
      const version =
        ("version" in props && props.version) ||
        ("run" in props && props.run.version) ||
        pipeline.currentVersion ||
        null;

      let state: any = {
        version,
      };

      if ("run" in props && props.run) {
        state = { ...state, ...props.run.config };
      }

      return state;
    },
  });
  const { t } = useTranslation();

  useEffect(() => {
    if (!open) {
      form.resetForm();
    }
  }, [open, form]);

  useEffect(() => {
    const version = form.formData.version;
    if (version) {
      console.log("version changed", version);
      form.resetForm();

      form.setFieldValue("version", version);
      if (version) {
        version.parameters.map((param) => {
          form.setFieldValue(param.code, param.default);
        });
      }
    }
  }, [form, form.formData.version]);

  if (!pipeline.permissions.run && open) {
    return (
      <Alert onClose={onClose} icon="error">
        {t("You don't have permission to run this pipeline")}
      </Alert>
    );
  }

  if (!pipeline.currentVersion && open) {
    return (
      <Alert onClose={onClose} icon="error">
        {t("This pipeline has not been uploaded yet")}
      </Alert>
    );
  }

  const parameters = form.formData.version?.parameters ?? [];
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={parameters.length > 4 ? "max-w-3xl" : "max-w-xl"}
    >
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title>{t("Run pipeline")}</Dialog.Title>
        <Dialog.Content className="-mx-0.5 -mb-0.5 max-h-[450px] overflow-y-auto px-0.5 pb-0.5">
          <Field name="version" label={t("Version")} required className="mb-6">
            <PipelineVersionPicker
              required
              pipeline={pipeline}
              value={form.formData.version ?? null}
              onChange={(value) => form.setFieldValue("version", value)}
            />
          </Field>
          {form.formData.version && parameters.length === 0 && (
            <p>{t("This pipeline has no parameter")}</p>
          )}
          <div
            className={clsx(
              "grid gap-x-3 gap-y-4",
              parameters.length > 4 && "grid-cols-2 gap-x-5"
            )}
          >
            {parameters.map((param, i) => (
              <Field
                required={param.required ?? true} // We also support parameters where required is not set
                key={i}
                name={param.code}
                label={param.name}
                help={param.help}
              >
                <ParameterField
                  parameter={param}
                  value={form.formData[param.code]}
                  onChange={(value: any) =>
                    form.setFieldValue(param.code, value)
                  }
                />
              </Field>
            ))}
          </div>
          {form.submitError && (
            <div className="mt-3 text-sm text-red-600">{form.submitError}</div>
          )}
        </Dialog.Content>
        <Dialog.Actions>
          <Button type="button" variant="white" onClick={onClose}>
            {t("Cancel")}
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={form.isSubmitting || !form.isValid}
            leadingIcon={<PlayIcon className="h-4 w-4" />}
          >
            {t("Run")}
          </Button>
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

RunPipelineDialog.fragments = {
  pipeline: gql`
    fragment RunPipelineDialog_pipeline on Pipeline {
      id
      permissions {
        run
      }
      code
      currentVersion {
        id
        number
        createdAt
        parameters {
          name
          code
          required
          ...ParameterField_parameter
        }
        user {
          displayName
        }
      }

      ...PipelineVersionPicker_pipeline
    }
    ${ParameterField.fragments.parameter}
    ${PipelineVersionPicker.fragments.pipeline}
  `,
  version: gql`
    fragment RunPipelineDialog_version on PipelineVersion {
      id
      number
      createdAt
      user {
        displayName
      }
      parameters {
        ...ParameterField_parameter
      }
    }
    ${ParameterField.fragments.parameter}
  `,
  run: gql`
    fragment RunPipelineDialog_run on PipelineRun {
      id
      config
      version {
        id
        number
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
