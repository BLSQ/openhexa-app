import { gql, useLazyQuery } from "@apollo/client";
import { ChevronDownIcon, PlayIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import Field from "core/components/forms/Field";
import { ensureArray } from "core/helpers/array";
import useCacheKey from "core/hooks/useCacheKey";
import useForm from "core/hooks/useForm";
import { PipelineType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";
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
import Checkbox from "core/components/forms/Checkbox";
import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
} from "@headlessui/react";

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
      const { sendMailNotifications, enableDebugLogs, ...params } = values;
      if (!activeVersion) {
        throw new Error("No active version found");
      }
      const run = await runPipeline(
        pipeline.id,
        convertParametersToPipelineInput(activeVersion!, params),
        activeVersion!.id,
        sendMailNotifications,
        enableDebugLogs,
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
                <Disclosure as="div" className={"mt-5"}>
                  {({ open }) => (
                    <>
                      <DisclosureButton className="group flex w-full justify-between text-left">
                        <div className="flex flex-col">
                          <span
                            className={
                              "font-bold text-sm group-data-hover:text-black/80"
                            }
                          >
                            {t("Advanced settings")}
                          </span>
                          {!open && (
                            <span className="text-gray-500 text-sm mt-1">
                              {t("Pipeline version, notifications and logs")}
                            </span>
                          )}
                        </div>
                        <ChevronDownIcon
                          className={`size-5 mt-1 ml-5 group-data-hover:text-black/80 ${
                            open ? "rotate-180" : ""
                          }`}
                        />
                      </DisclosureButton>
                      <DisclosurePanel>
                        <Field
                          name="version"
                          label={t("Version")}
                          required
                          className="mb-3"
                        >
                          <PipelineVersionPicker
                            required
                            pipeline={pipeline}
                            value={activeVersion}
                            onChange={(value) => setActiveVersion(value)}
                          />
                        </Field>
                        <Field
                          name="notification"
                          label={t("Notifications")}
                          required
                          className="mb-4"
                        >
                          <Checkbox
                            checked={form.formData.sendMailNotifications}
                            name="sendMailNotifications"
                            onChange={(event) =>
                              form.setFieldValue(
                                "sendMailNotifications",
                                event.target.checked,
                              )
                            }
                            label={t("Send notifications")}
                            help={t("Notifications will be sent for this run.")}
                          />
                        </Field>
                        <Field name="logs" label={t("Logs")} required>
                          <Checkbox
                            checked={form.formData.enableDebugLogs}
                            name="enableDebugLogs"
                            onChange={(event) =>
                              form.setFieldValue(
                                "enableDebugLogs",
                                event.target.checked,
                              )
                            }
                            label={t("Show debug messages")}
                            help={t(
                              "Debug messages will be shown for this run.",
                            )}
                          />
                        </Field>
                      </DisclosurePanel>
                    </>
                  )}
                </Disclosure>
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
