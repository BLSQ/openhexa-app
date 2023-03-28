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

  const form = useForm<{ version: any; [key: string]: any }>({
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
      onClose();
    },
    getInitialState() {
      return {
        version:
          (("version" in props && props.version) ||
            ("run" in props && props.run.version) ||
            pipeline.currentVersion) ??
          null,
        ...("run" in props ? props.run.config : {}),
      };
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
      form.resetForm();
      form.setFieldValue("version", version);
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

  const parameters = (form.formData.version?.parameters ?? []) as Parameter[];
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={parameters.length > 4 ? "max-w-3xl" : "max-w-xl"}
    >
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title>{t("Run pipeline")}</Dialog.Title>
        <Dialog.Content>
          <Field name="version" label={t("Version")} required className="mb-6">
            <PipelineVersionPicker
              required
              pipeline={pipeline}
              value={form.formData.version ?? null}
              onChange={(value) => form.setFieldValue("version", value)}
            />
          </Field>
          {parameters.length === 0 && (
            <p>{t("This pipeline has no parameter")}</p>
          )}
          <div
            className={clsx(
              "grid gap-3",
              parameters.length > 4 && "grid-cols-2 gap-x-5"
            )}
          >
            {parameters.map((param, i) => (
              <Field
                required={param.required ?? true} // We also support parameters where required is not set
                key={i}
                name={param.name}
                label={param.help}
              >
                {param.type === "bool" && (
                  <Switch
                    name={param.name}
                    checked={form.formData[param.name] ?? false}
                    onChange={(checked) =>
                      form.setFieldValue(param.name, checked)
                    }
                  />
                )}
                {param.choices?.length ? (
                  <SimpleSelect
                    name={param.name}
                    value={form.formData[param.name]}
                    required={param.required}
                    onChange={form.handleInputChange}
                  >
                    {param.choices.map((opt, idx) => (
                      <option key={idx} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </SimpleSelect>
                ) : (
                  <Input
                    type={
                      ["int", "float"].includes(param.type) ? "number" : "text"
                    }
                    name={param.name}
                    required={param.required ?? true}
                    onChange={form.handleInputChange}
                    value={form.formData[param.name] || ""}
                  />
                )}
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
      currentVersion {
        id
        number
        createdAt
        parameters
        user {
          displayName
        }
      }

      ...PipelineVersionPicker_pipeline
    }
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
      parameters
    }
  `,
  run: gql`
    fragment RunPipelineDialog_run on PipelineRun {
      id
      config
      version {
        id
        number
        createdAt
        parameters
        user {
          displayName
        }
      }
    }
  `,
};

export default RunPipelineDialog;
