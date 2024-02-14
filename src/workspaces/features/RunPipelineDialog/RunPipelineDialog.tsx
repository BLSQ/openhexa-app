import { gql, useLazyQuery } from "@apollo/client";
import { PlayIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Alert from "core/components/Alert";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import useCacheKey from "core/hooks/useCacheKey";
import useForm from "core/hooks/useForm";
import { PipelineVersion } from "graphql-types";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import {
  convertParametersToPipelineInput,
  isConnectionParameter,
  runPipeline,
} from "workspaces/helpers/pipelines";
import PipelineVersionPicker from "../PipelineVersionPicker";
import ParameterField from "./ParameterField";
import {
  PipelineCurrentVersionQuery,
  RunPipelineDialog_PipelineFragment,
  RunPipelineDialog_RunFragment,
} from "./RunPipelineDialog.generated";
import Spinner from "core/components/Spinner";
import { ensureArray } from "core/helpers/array";
import Checkbox from "core/components/forms/Checkbox/Checkbox";

type RunPipelineDialogProps = {
  open: boolean;
  onClose: () => void;
  pipeline: RunPipelineDialog_PipelineFragment;
} & (
  | {}
  | { run: RunPipelineDialog_RunFragment }
  | { version: PipelineVersion }
);

const RunPipelineDialog = (props: RunPipelineDialogProps) => {
  const router = useRouter();
  const { open, onClose, pipeline } = props;
  const [showVersionPicker, setShowVersionPicker] = useState(false);
  const clearCache = useCacheKey(["pipelines", pipeline.code]);
  const { t } = useTranslation();

  const [fetch, { data }] = useLazyQuery<PipelineCurrentVersionQuery>(
    gql`
      query PipelineCurrentVersion(
        $workspaceSlug: String!
        $pipelineCode: String!
      ) {
        pipelineByCode(workspaceSlug: $workspaceSlug, code: $pipelineCode) {
          currentVersion {
            number
            createdAt
            user {
              displayName
            }
            parameters {
              ...ParameterField_parameter
            }
          }
        }
      }
      ${ParameterField.fragments.parameter}
    `,
    { fetchPolicy: "no-cache" },
  );

  const form = useForm<{ version: PipelineVersion; [key: string]: any }>({
    async onSubmit(values) {
      const { version, sendMailNotifications, ...params } = values;
      const run = await runPipeline(
        pipeline.id,
        convertParametersToPipelineInput(version, params),
        version?.number,
        sendMailNotifications,
      );
      await router.push(
        `/workspaces/${encodeURIComponent(
          router.query.workspaceSlug as string,
        )}/pipelines/${encodeURIComponent(
          pipeline.id,
        )}/runs/${encodeURIComponent(run.id)}`,
      );
      clearCache();
      onClose();
    },
    getInitialState() {
      let state: any = {
        version: null,
        sendMailNotifications: false,
      };
      if ("run" in props && props.run.version) {
        state = {
          ...state,
          ...props.run.config,
          version: props.run.version,
        };
      } else if ("version" in props) {
        state.version = props.version;
      }

      return state;
    },
    validate(values) {
      const errors = {} as any;
      const { version, ...fields } = values;
      if (!version) {
        return { version: t("The version is required") };
      }
      const normalizedValues = convertParametersToPipelineInput(
        version,
        fields,
      );
      for (const parameter of version.parameters) {
        const val = normalizedValues[parameter.code];
        if (parameter.type === "int" || parameter.type === "float") {
          if (ensureArray(val).length === 0 && parameter.required) {
            errors[parameter.code] = t("This field is required");
          } else if (ensureArray(val).some((v) => isNaN(v))) {
            errors[parameter.code] = t("This field must contain only numbers");
          }
        }

        if (
          ["str", "dataset"].includes(parameter.type) &&
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
    if (open) {
      form.resetForm();
      setShowVersionPicker(false);
    }
    if (!("run" in props)) {
      fetch({
        variables: {
          workspaceSlug: pipeline.workspace?.slug,
          pipelineCode: pipeline.code,
        },
      });
    }
  }, [open, form, fetch, props, pipeline.code, pipeline.workspace]);

  useEffect(() => {
    if (!form.formData.version && open) {
      form.setFieldValue("version", data?.pipelineByCode?.currentVersion);
    }
  }, [open, form, data]);

  useEffect(() => {
    const version = form.formData.version;
    if (version) {
      form.resetForm();
      form.setFieldValue("version", version);
      version.parameters.map((param) => {
        if ("run" in props && props.run?.config[param.code] !== null) {
          form.setFieldValue(param.code, props.run.config[param.code], false);
        } else {
          form.setFieldValue(param.code, param.default, false);
        }
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      centered={false}
      onSubmit={form.handleSubmit}
      maxWidth={parameters.length > 4 ? "max-w-3xl" : "max-w-2xl"}
    >
      <Dialog.Title>{t("Run pipeline")}</Dialog.Title>
      {!form.formData.version ? (
        <Dialog.Content className="flex  items-center justify-center">
          <Spinner size="lg" />
        </Dialog.Content>
      ) : (
        <>
          <Dialog.Content>
            {form.errors.version && (
              <div className="mt-3 text-sm text-red-600">
                {form.errors.version}
              </div>
            )}
            {!showVersionPicker ? (
              <div className="mb-6 flex justify-start gap-x-1">
                <p>
                  {!("run" in props)
                    ? t("This pipeline will run using the latest version")
                    : t("This pipeline will run using the same version")}
                </p>
                <button
                  className="text-sm text-blue-600 hover:text-blue-500"
                  role="link"
                  onClick={() => {
                    setShowVersionPicker(true);
                  }}
                >
                  {t("(select specific version)")}
                </button>
              </div>
            ) : (
              <Field
                name="version"
                label={t("Version")}
                required
                className="mb-6"
              >
                <PipelineVersionPicker
                  required
                  pipeline={pipeline}
                  value={form.formData.version ?? null}
                  onChange={(value) => form.setFieldValue("version", value)}
                />
              </Field>
            )}

            {parameters.length === 0 && (
              <p>{t("This pipeline has no parameter")}</p>
            )}
            <div
              className={clsx(
                "grid gap-x-3 gap-y-4",
                parameters.length > 4 && "grid-cols-2 gap-x-5",
              )}
            >
              {parameters.map((param, i) => (
                <Field
                  required={param.required || param.type === "bool"}
                  key={i}
                  name={param.code}
                  label={param.name}
                  help={param.help}
                  error={form.touched[param.code] && form.errors[param.code]}
                >
                  <ParameterField
                    parameter={param}
                    value={form.formData[param.code]}
                    onChange={(value: any) => {
                      form.setFieldValue(param.code, value);
                    }}
                    workspaceSlug={pipeline.workspace?.slug}
                  />
                </Field>
              ))}
            </div>
            {form.submitError && (
              <div className="mt-3 text-sm text-red-600">
                {form.submitError}
              </div>
            )}
          </Dialog.Content>
          <Dialog.Actions className="flex-1 items-center">
            <div className="flex flex-1 items-center">
              <Checkbox
                checked={form.formData.sendMailNotifications}
                name="sendMailNotifications"
                onChange={form.handleInputChange}
                label={t("Receive mail notification")}
                help={t("You will receive an email when the pipeline is done")}
              />
            </div>
            <Button type="button" variant="white" onClick={onClose}>
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
  );
};

RunPipelineDialog.fragments = {
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
  version: gql`
    fragment RunPipelineDialog_version on PipelineVersion {
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
    ${ParameterField.fragments.parameter}
  `,
};

export default RunPipelineDialog;
