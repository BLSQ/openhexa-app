import { gql, useMutation } from "@apollo/client";
import Button from "core/components/Button/Button";
import Dialog from "core/components/Dialog";
import Link from "core/components/Link";
import Tabs from "core/components/Tabs";
import Field from "core/components/forms/Field/Field";
import Textarea from "core/components/forms/Textarea/Textarea";
import useForm from "core/hooks/useForm";
import { BucketObjectType, PipelineError } from "graphql/types";
import { Trans, useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { useCreatePipelineMutation } from "workspaces/graphql/mutations.generated";
import { toSpinalCase } from "workspaces/helpers/pipelines";
import BucketObjectPicker from "../BucketObjectPicker";
import {
  CreatePipelineDialog_WorkspaceFragment,
  GenerateWorkspaceTokenMutation,
} from "./CreatePipelineDialog.generated";
import useFeature from "identity/hooks/useFeature";
import PipelineTemplates from "pipelines/features/PipelineTemplates/PipelineTemplates";

type CreatePipelineDialogProps = {
  open: boolean;
  onClose: () => void;
  workspace: CreatePipelineDialog_WorkspaceFragment;
};

const CreatePipelineDialog = (props: CreatePipelineDialogProps) => {
  const { t } = useTranslation();
  const { open, onClose, workspace } = props;
  const router = useRouter();
  const [pipelineTemplateFeatureEnabled] = useFeature("pipeline_templates");
  const tabs = pipelineTemplateFeatureEnabled
    ? ["templates", "notebooks", "cli"]
    : ["notebooks", "cli"];
  const [tabIndex, setTabIndex] = useState<number>(0);

  const [mutate] = useCreatePipelineMutation();

  const form = useForm<{ notebookObject: any; name: string }>({
    onSubmit: async (values) => {
      const { notebookObject } = values;

      const { data } = await mutate({
        variables: {
          input: {
            code: toSpinalCase(values.name.toLowerCase()),
            name: values.name,
            notebookPath: notebookObject.key,
            workspaceSlug: workspace.slug,
          },
        },
      });

      if (data?.createPipeline.success && data.createPipeline.pipeline) {
        const pipeline = data.createPipeline.pipeline;
        await router.push(
          `/workspaces/${encodeURIComponent(
            router.query.workspaceSlug as string,
          )}/pipelines/${encodeURIComponent(pipeline.code)}`,
        );
      } else if (
        data?.createPipeline.errors.includes(
          PipelineError.PipelineAlreadyExists,
        )
      ) {
        throw new Error(
          t("A pipeline with the selected notebook already exist"),
        );
      } else {
        throw new Error(t("An error occurred while creating the pipeline."));
      }
    },
    validate(values) {
      const errors: any = {};
      if (!values.notebookObject) {
        errors.notebookObject = t("You have to select a notebook");
      }
      return errors;
    },
  });

  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  const [token, setToken] = useState<null | string>(null);
  const [generateToken] = useMutation<GenerateWorkspaceTokenMutation>(
    gql`
      mutation GenerateWorkspaceToken($input: GenerateWorkspaceTokenInput!) {
        generateWorkspaceToken(input: $input) {
          token
          success
        }
      }
    `,
    { variables: { input: { slug: workspace.slug } } },
  );

  const onTokenClick = async () => {
    if (!token) {
      const { data } = await generateToken();
      setToken(data?.generateWorkspaceToken?.token ?? null);
    }
  };

  useEffect(() => {
    if (open) {
      setToken(null);
    }
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-4xl">
      <Dialog.Title>{t("How to create a pipeline")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Tabs onChange={(index) => setTabIndex(index)} defaultIndex={tabIndex}>
          {pipelineTemplateFeatureEnabled && (
            <Tabs.Tab label={t("From Template")} className={"space-y-2 pt-2"}>
              <PipelineTemplates workspace={workspace} showCard={false} />
            </Tabs.Tab>
          )}
          <Tabs.Tab label={t("From Notebook")} className={"space-y-2 pt-2"}>
            <form>
              <p className="mb-6">
                <Trans>
                  You can use a Notebook from the workspace file system to be
                  run as a pipeline. This is the easiest way to create a
                  pipeline. Keep in my mind that Notebooks are not versioned. If
                  a user changes the notebook, the pipeline will be updated.
                </Trans>
              </p>
              <div className="grid gap-6">
                <Field
                  name="name"
                  label={t("Pipeline Name")}
                  required
                  placeholder={t("My Pipeline")}
                  error={form.touched.name && form.errors.name}
                  value={form.formData.name}
                  onChange={form.handleInputChange}
                />
                <Field
                  name={"notebookObject"}
                  label={t("Notebook")}
                  required
                  error={
                    form.touched.notebookObject && form.errors.notebookObject
                  }
                  className={"max-w-[230px]"}
                >
                  <BucketObjectPicker
                    onChange={(value) =>
                      form.setFieldValue("notebookObject", value)
                    }
                    value={form.formData.notebookObject?.key}
                    exclude={(item) =>
                      item.type === BucketObjectType.File &&
                      !item.name.endsWith(".ipynb")
                    }
                    placeholder={t("Select a Jupyter notebook")}
                    workspace={workspace}
                  />
                </Field>
                {form.submitError && (
                  <p className={"text-sm text-red-500"}>{form.submitError}</p>
                )}
              </div>
            </form>
          </Tabs.Tab>
          <Tabs.Tab label={t("From OpenHEXA CLI")} className={"space-y-2 pt-2"}>
            <p className="mb-6">
              <Trans>
                In order to create pipelines, you need to setup the{" "}
                <code>openhexa</code> CLI using the{" "}
                <Link
                  target="_blank"
                  href="https://github.com/BLSQ/openhexa/wiki/Writing-OpenHexa-pipelines"
                >
                  guide
                </Link>{" "}
                on Github.
              </Trans>
            </p>
            <p>
              {t(
                "Configure the workspace in your terminal using the following commands:",
              )}
            </p>

            <pre className=" bg-slate-100 p-2 font-mono text-sm leading-6">
              <div>
                <span className="select-none text-gray-400">$ </span>pip install
                openhexa.sdk
                <span className="select-none text-gray-400">
                  {t("# if not installed")}
                </span>
              </div>
              <div>
                <span className="select-none text-gray-400">$ </span>
                <span className="whitespace-normal">
                  openhexa workspaces add <b>{workspace.slug}</b>
                </span>
              </div>
            </pre>
            <Field name="token" label={t("Access Token")} required>
              <div className="flex w-full flex-1 items-center gap-1">
                {token ? (
                  <Textarea className="font-mono" value={token} readOnly />
                ) : (
                  <Button variant="secondary" onClick={onTokenClick}>
                    {t("Show")}
                  </Button>
                )}
              </div>
            </Field>
          </Tabs.Tab>
        </Tabs>
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="outlined">
          {t("Close")}
        </Button>
        {tabs[tabIndex] === "notebooks" && (
          <Button disabled={form.isSubmitting} onClick={form.handleSubmit}>
            {t("Create")}
          </Button>
        )}
      </Dialog.Actions>
    </Dialog>
  );
};

CreatePipelineDialog.fragments = {
  workspace: gql`
    fragment CreatePipelineDialog_workspace on Workspace {
      slug
      ...BucketObjectPicker_workspace
    }
    ${BucketObjectPicker.fragments.workspace}
  `,
};

export default CreatePipelineDialog;
