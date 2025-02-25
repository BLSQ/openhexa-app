import { gql } from "@apollo/client";
import { Trans, useTranslation } from "react-i18next";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import React, { useEffect, useState } from "react";
import Dialog from "core/components/Dialog";
import { useRouter } from "next/router";
import { toast } from "react-toastify";
import useForm from "core/hooks/useForm";
import { isEmpty } from "lodash";
import Field from "core/components/forms/Field";
import Textarea from "core/components/forms/Textarea";
import Checkbox from "core/components/forms/Checkbox";
import { useCreatePipelineTemplateVersionMutation } from "pipelines/graphql/mutations.generated";
import { CreatePipelineTemplateVersionError } from "graphql/types";
import {
  PipelinePublish_PipelineFragment,
  PipelinePublish_WorkspaceFragment,
} from "./PublishPipelineDialog.generated";

type PublishPipelineDialogProps = {
  open: boolean;
  onClose: () => void;
  pipeline: PipelinePublish_PipelineFragment;
  workspace: PipelinePublish_WorkspaceFragment;
};

const PublishPipelineDialog = ({
  open,
  onClose,
  pipeline,
  workspace,
}: PublishPipelineDialogProps) => {
  const { t } = useTranslation();
  const templateAlreadyExists = !!pipeline.template;
  const router = useRouter();
  const [isFormValid, setIsFormValid] = useState(false);
  const [createPipelineTemplateVersion] =
    useCreatePipelineTemplateVersionMutation();

  const form = useForm<{
    name: string;
    description: string;
    confirmPublishing: boolean;
    changelog: string;
  }>({
    initialState: {
      name: pipeline.name ?? "",
      description: pipeline.description ?? "",
      confirmPublishing: false,
      changelog: "",
    },
    async onSubmit(values) {
      const pipelineVersionId = pipeline.currentVersion?.id;
      if (!pipelineVersionId) {
        toast.error(t("The pipeline version is not available."));
        return;
      }
      const { data } = await createPipelineTemplateVersion({
        variables: {
          input: {
            name: values.name,
            code: values.name,
            description: values.description,
            changelog: values.changelog,
            workspaceSlug: workspace.slug,
            pipelineId: pipeline.id,
            pipelineVersionId: pipelineVersionId,
          },
        },
      });

      if (!data?.createPipelineTemplateVersion) {
        toast.error(t("Unknown error."));
        return;
      }

      if (data.createPipelineTemplateVersion.success) {
        toast.success(successMessage);
        onClose();
        await router.push(
          `/workspaces/${workspace.slug}/templates/${data.createPipelineTemplateVersion.pipelineTemplate?.code}`,
        );
      } else if (
        data.createPipelineTemplateVersion.errors?.includes(
          CreatePipelineTemplateVersionError.PermissionDenied,
        )
      ) {
        toast.error(t("You are not allowed to create a Template."));
      } else if (
        data.createPipelineTemplateVersion.errors?.includes(
          CreatePipelineTemplateVersionError.DuplicateTemplateNameOrCode,
        )
      ) {
        toast.error(t("A template with the same name already exists."));
      } else {
        toast.error(t("Unknown error."));
      }
    },
    validate(values) {
      const errors: any = {};
      if (!templateAlreadyExists && isEmpty(values.name)) {
        errors.name = t("Name is required");
      }
      if (!templateAlreadyExists && isEmpty(values.description)) {
        errors.description = t("Description is required");
      }
      if (!values.confirmPublishing) {
        errors.confirmPublishing = t("You must confirm publishing");
      }
      setIsFormValid(isEmpty(errors));
      return errors;
    },
  });

  useEffect(() => {
    form.validate();
  }, [form.formData]);

  useEffect(() => {
    form.resetForm();
  }, [open, form]);

  const successMessage = templateAlreadyExists
    ? t("New Template Version for '{{templateName}}' created successfully.", {
        templateName: pipeline.template?.name,
      })
    : t("New Template '{{name}}' created successfully.", {
        name: form.formData.name,
      });
  const actionMessage = templateAlreadyExists
    ? t("Add a new version to Template '{{templateName}}'", {
        templateName: pipeline.template?.name,
      })
    : t("Create a new Template");

  return (
    <Dialog open={open} onClose={onClose} className={"w-140"}>
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title>{actionMessage}</Dialog.Title>
        <Dialog.Content>
          {templateAlreadyExists ? (
            <Field name="changelog" label={t("Changelog")}>
              <Textarea
                id="changelog"
                name="changelog"
                value={form.formData.changelog}
                onChange={form.handleInputChange}
                rows={10}
              />
            </Field>
          ) : (
            <>
              <Field
                name="name"
                label={t("Template name")}
                required
                fullWidth
                className="mb-3"
                value={form.formData.name}
                onChange={form.handleInputChange}
                maxLength={255}
              />
              <Field
                name="description"
                label={t("Template description")}
                required
              >
                <Textarea
                  id="description"
                  name="description"
                  required
                  rows={10}
                  value={form.formData.description}
                  onChange={form.handleInputChange}
                />
              </Field>
            </>
          )}
          <Field
            name="confirmPublishing"
            label={t("Confirm publishing")}
            required
            className="mt-3 mb-3"
          >
            <Checkbox
              id="confirmPublishing"
              name="confirmPublishing"
              checked={form.formData.confirmPublishing}
              onChange={form.handleInputChange}
              label={
                <Trans>
                  I confirm that I want to publish this code and make it
                  available <b>to all users of the OpenHEXA platform</b>
                </Trans>
              }
            />
          </Field>
          {form.submitError && (
            <div className="mt-3 text-sm text-red-600">{form.submitError}</div>
          )}
        </Dialog.Content>
        <Dialog.Actions>
          <Button variant="white" onClick={onClose}>
            {t("Cancel")}
          </Button>
          <Button disabled={form.isSubmitting || !isFormValid} type={"submit"}>
            {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
            {actionMessage}
          </Button>
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

PublishPipelineDialog.fragment = {
  pipeline: gql`
    fragment PipelinePublish_pipeline on Pipeline {
      id
      name
      description
      currentVersion {
        id
        versionName
      }
      template {
        id
        name
      }
    }
  `,
  workspace: gql`
    fragment PipelinePublish_workspace on Workspace {
      slug
    }
  `,
};

export default PublishPipelineDialog;
