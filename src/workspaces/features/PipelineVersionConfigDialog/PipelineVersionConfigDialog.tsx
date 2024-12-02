import { gql, useMutation } from "@apollo/client";
import { Trans, useTranslation } from "next-i18next";
import { useEffect } from "react";
import { convertParametersToPipelineInput } from "workspaces/helpers/pipelines";

import clsx from "clsx";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import useForm from "core/hooks/useForm";
import { PipelineParameter, UpdatePipelineVersionError } from "graphql/types";
import ParameterField from "../RunPipelineDialog/ParameterField";
import { PipelineVersionConfigDialog_VersionFragment } from "./PipelineVersionConfigDialog.generated";

type PipelineVersionConfigProps = {
  version: PipelineVersionConfigDialog_VersionFragment;
  onClose(): void;
  open: boolean;
};

const PipelineVersionConfigDialog = (props: PipelineVersionConfigProps) => {
  const { version, onClose, open } = props;
  const { t } = useTranslation();

  const [updateConfig] = useMutation(gql`
    mutation UpdatePipelineVersionConfig($input: UpdatePipelineVersionInput!) {
      updatePipelineVersion(input: $input) {
        success
        errors
        pipelineVersion {
          id
          config
        }
      }
    }
  `);
  const isParameterRequired = (param: PipelineParameter) => {
    // We only consider a parameter required if it is required and the pipeline has a schedule.
    // Users can still run the pipeline manually without by filling in the required parameters.
    return Boolean(version.pipeline.schedule && param.required);
  };

  const form = useForm<{ [key: string]: any }>({
    validate(values) {
      const errors = {} as any;
      for (const param of version.parameters) {
        if (
          isParameterRequired(param) &&
          (values[param.code] === null ||
            values[param.code] === "" ||
            values[param.code] === undefined ||
            values[param.code] === false) // Required boolean parameter has to be set to true...
        ) {
          errors[param.code] = t(
            "This parameter is required for scheduling the pipeline.",
          );
        }
      }
      return errors;
    },
    async onSubmit(values) {
      const { data } = await updateConfig({
        variables: {
          input: {
            id: version.id,
            config: convertParametersToPipelineInput(version, values),
          },
        },
      });
      if (data?.errors?.includes(UpdatePipelineVersionError.PermissionDenied)) {
        throw new Error("You cannot update this version's configuration.");
      } else if (!data?.updatePipelineVersion.success) {
        throw new Error("An error occurred while updating the version.");
      }
      onClose();
    },
    getInitialState() {
      let initialValues: any = {};
      for (const param of version.parameters) {
        initialValues[param.code] = version.config[param.code] ?? param.default;
      }
      return initialValues;
    },
  });

  useEffect(() => {
    form.resetForm();
  }, [form, version, open]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      onSubmit={form.handleSubmit}
      maxWidth={"max-w-3xl"}
    >
      <Dialog.Title onClose={onClose}>
        {t("Set default configuration")}
      </Dialog.Title>
      <Dialog.Content className="space-y-4 flex flex-col">
        <p className="text-sm">
          <Trans>
            Set the default configuration for this version. These values will be
            used when running the pipeline manually or via a schedule.
            <br />
            Users are able to change the values when running the pipeline
            manually.
            <br />
          </Trans>
        </p>
        {version.pipeline.schedule && (
          <p className="text-sm">
            <Trans>
              Fill in the required parameters to keep the scheduling of your
              pipeline active.
            </Trans>
          </p>
        )}

        <div
          className={clsx(
            "grid gap-x-3 gap-y-4",
            version.parameters.length > 4 && "grid-cols-2 gap-x-5",
          )}
        >
          {version.parameters.map((param, i) => (
            <Field
              showOptional={Boolean(version.pipeline.schedule)}
              key={i}
              name={param.code}
              label={param.name}
              help={param.help}
              required={isParameterRequired(param)}
              error={form.touched[param.code] && form.errors[param.code]}
            >
              <ParameterField
                parameter={param}
                value={form.formData[param.code]}
                onChange={(value: any) => {
                  form.setFieldValue(param.code, value);
                }}
                workspaceSlug={version.pipeline.workspace.slug}
              />
            </Field>
          ))}
        </div>
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant={"outlined"}>
          {t("Cancel")}
        </Button>
        <Button disabled={form.isSubmitting} type="submit">
          {t("Save")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

PipelineVersionConfigDialog.fragments = {
  version: gql`
    fragment PipelineVersionConfigDialog_version on PipelineVersion {
      id
      name
      description
      externalLink
      isLatestVersion
      createdAt
      config
      pipeline {
        id
        schedule
        workspace {
          slug
        }
      }
      parameters {
        ...ParameterField_parameter
      }
    }
    ${ParameterField.fragments.parameter}
  `,
};

export default PipelineVersionConfigDialog;
