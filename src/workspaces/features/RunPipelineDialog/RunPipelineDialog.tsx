import { gql, useLazyQuery } from "@apollo/client";
import { PlayIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import Checkbox from "core/components/forms/Checkbox/Checkbox";
import Field from "core/components/forms/Field";
import { ensureArray } from "core/helpers/array";
import useCacheKey from "core/hooks/useCacheKey";
import useForm from "core/hooks/useForm";
import { PipelineType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
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
  RunPipelineDialog_VersionFragment,
} from "./RunPipelineDialog.generated";
import { ErrorAlert } from "core/components/Alert";

type RunPipelineDialogProps = {
  children(onClick: () => void): React.ReactNode;
  pipeline: RunPipelineDialog_PipelineFragment;
  run?: RunPipelineDialog_RunFragment;
};

const VERSION_FRAGMENT = gql`
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
`;

const RunPipelineDialog = (props: RunPipelineDialogProps) => {
  const router = useRouter();
  const { pipeline, run, children } = props;
  const [showVersionPicker, setShowVersionPicker] = useState(false);
  const clearCache = useCacheKey(["pipelines", pipeline.code]);
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const onClose = () => setOpen(false);

  const [activeVersion, setActiveVersion] =
    useState<RunPipelineDialog_VersionFragment | null>(run?.version ?? null);
  const onClick = () => {
    if (pipeline.type === PipelineType.ZipFile) {
      setOpen(true);
    } else {
      runPipeline(pipeline.id).then((run) => {
        router.push(
          `/workspaces/${encodeURIComponent(
            pipeline.workspace!.slug,
          )}/pipelines/${encodeURIComponent(pipeline.id)}/runs/${encodeURIComponent(
            run.id,
          )}`,
        );
        clearCache();
      });
    }
  };

  const [fetch] = useLazyQuery<PipelineCurrentVersionQuery>(
    gql`
      query PipelineCurrentVersion(
        $workspaceSlug: String!
        $pipelineCode: String!
      ) {
        pipelineByCode(workspaceSlug: $workspaceSlug, code: $pipelineCode) {
          currentVersion {
            id
            versionName
            createdAt
            user {
              displayName
            }
            config
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

  const form = useForm<{ [key: string]: any }>({
    async onSubmit(values) {
      const { sendMailNotifications, ...params } = values;
      if (!activeVersion) {
        throw new Error("No active version found");
      }
      const run = await runPipeline(
        pipeline.id,
        convertParametersToPipelineInput(activeVersion!, params),
        activeVersion!.id,
        sendMailNotifications,
      );
      await router.push(
        `/workspaces/${encodeURIComponent(
          pipeline.workspace!.slug,
        )}/pipelines/${encodeURIComponent(
          pipeline.id,
        )}/runs/${encodeURIComponent(run.id)}`,
      );
      clearCache();
      onClose();
    },
    getInitialState() {
      if (run) {
        return {
          sendMailNotifications: true,
          ...run.config,
        };
      } else if (activeVersion) {
        return {
          sendMailNotifications: true,
          ...activeVersion.config,
        };
      }
    },
    validate(values) {
      const errors = {} as any;
      if (!activeVersion) {
        return errors;
      }
      const normalizedValues = convertParametersToPipelineInput(
        activeVersion,
        values,
      );
      for (const parameter of activeVersion.parameters) {
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
    setShowVersionPicker(false);
    if (!open) {
      setActiveVersion(null);
    } else if (run?.version) {
      setActiveVersion(run.version);
    } else {
      fetch({
        variables: {
          workspaceSlug: pipeline.workspace?.slug,
          pipelineCode: pipeline.code,
        },
      }).then(({ data }) => {
        if (data?.pipelineByCode?.currentVersion) {
          setActiveVersion(data.pipelineByCode.currentVersion);
        }
      });
    }
  }, [open, form, fetch, run, pipeline.code, pipeline.workspace]);

  useEffect(() => {
    form.resetForm();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form, activeVersion]);

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
          maxWidth={"max-w-3xl"}
        >
          <Dialog.Title>{t("Run pipeline")}</Dialog.Title>
          {!activeVersion ? (
            <Dialog.Content className="flex items-center justify-center">
              <Spinner size="lg" />
            </Dialog.Content>
          ) : (
            <>
              <Dialog.Content>
                {!showVersionPicker ? (
                  <div className="mb-6 gap-x-1">
                    <p>
                      {!props.run
                        ? t("This pipeline will run using the latest version.")
                        : t("This pipeline will run using the same version.")}
                      &nbsp;
                      <button
                        className="text-sm text-blue-600 hover:text-blue-500 inline"
                        role="link"
                        onClick={() => {
                          setShowVersionPicker(true);
                        }}
                      >
                        {t("Select specific version")}
                      </button>
                    </p>
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
                      value={activeVersion}
                      onChange={(value) => setActiveVersion(value)}
                    />
                  </Field>
                )}

                <div
                  className={clsx(
                    "grid gap-x-3 gap-y-4",
                    activeVersion.parameters.length > 4 &&
                      "grid-cols-2 gap-x-5",
                  )}
                >
                  {activeVersion.parameters.map((param, i) => (
                    <Field
                      required={param.required || param.type === "bool"}
                      key={i}
                      name={param.code}
                      label={param.name}
                      help={param.help}
                      error={
                        form.touched[param.code] && form.errors[param.code]
                      }
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
                    checked={!form.formData.sendMailNotifications}
                    name="sendMailNotifications"
                    onChange={(event) =>
                      form.setFieldValue(
                        "sendMailNotifications",
                        !event.target.checked,
                      )
                    }
                    label={t("Mute notifications")}
                    help={t("Notifications will be disabled for this run.")}
                  />
                </div>
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
