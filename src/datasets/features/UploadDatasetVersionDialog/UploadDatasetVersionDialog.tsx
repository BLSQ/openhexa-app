import { gql } from "@apollo/client";
import Dialog from "core/components/Dialog";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button";
import Tabs from "core/components/Tabs";
import { UploadDatasetVersionDialog_DatasetLinkFragment } from "./UploadDatasetVersionDialog.generated";
import Dropzone from "core/components/Dropzone";
import { useEffect, useState } from "react";
import useForm from "core/hooks/useForm";
import Field from "core/components/forms/Field";
import { uploader } from "core/helpers/files";
import {
  createDatasetVersion,
  createVersionFile,
  generateDatasetUploadUrl,
} from "datasets/helpers/dataset";
import Spinner from "core/components/Spinner";
import { useRouter } from "next/router";
import CodeEditor from "core/components/CodeEditor";
import Textarea from "core/components/forms/Textarea";

type UploadDatasetVersionDialogProps = {
  open: boolean;
  onClose: () => void;
  datasetLink: UploadDatasetVersionDialog_DatasetLinkFragment;
};

const UploadDatasetVersionDialog = ({
  open,
  onClose,
  datasetLink,
}: UploadDatasetVersionDialogProps) => {
  const { t } = useTranslation();
  const [tabIndex, setTabIndex] = useState<number | null>(null);
  const [progress, setProgress] = useState(0);
  const router = useRouter();
  const form = useForm<{ name: string; files: any[]; changelog: string }>({
    initialState: {
      name: "",
      files: [],
      changelog: "",
    },
    async onSubmit(values) {
      const version = await createDatasetVersion(
        datasetLink.dataset.id,
        values.name,
        values.changelog,
      );
      await uploader.createUploadJob({
        files: values.files,
        async getXHROptions(file) {
          const contentType = file.type || "application/octet-stream";
          const url = await generateDatasetUploadUrl(
            version.id,
            file.name,
            contentType,
          );

          return {
            url,
            method: "PUT",
            headers: { "Content-Type": contentType },
          };
        },
        onProgress: setProgress,
      });
      for (const file of values.files) {
        await createVersionFile(
          version.id,
          file.type || "application/octet-stream",
          file.name,
        );
      }
      if (datasetLink.workspace) {
        await router.push({
          pathname: "/workspaces/[workspaceSlug]/datasets/[datasetSlug]",
          query: {
            workspaceSlug: datasetLink.workspace.slug,
            datasetSlug: datasetLink.dataset.slug,
            version: version.id,
          },
        });
      }
      onClose();
    },
    validate(values) {
      const errors: any = {};
      if (!values.name) {
        errors.name = t("Name is required");
      }
      if (!values.files?.length) {
        errors.files = t("Select files");
      }

      return errors;
    },
  });

  useEffect(() => {
    form.resetForm();
    setProgress(0);
  }, [open, form, tabIndex]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={"max-w-3xl"}
      centered={false}
    >
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title onClose={onClose}>
          {t("Upload a new version")}
        </Dialog.Title>
        <Dialog.Content>
          <Tabs onChange={(index) => setTabIndex(index)}>
            <Tabs.Tab label={t("Using SDK")} className={"space-y-2 pt-2"}>
              <p>
                You can upload a new version of your dataset from Pipelines &
                Jupyter using the following snippet.
              </p>
              <CodeEditor
                lang={"python"}
                readonly
                value={`from pathlib import Path
from openhexa.sdk import workspace

# Get the dataset
dataset = workspace.get_dataset("${datasetLink.dataset.slug}")

# Create a new version
version = dataset.create_version("v2", changelog="This is a changelog in markdown")

# Upload a single file
version.add_file("/path/to/file.csv")`}
              />
            </Tabs.Tab>
            <Tabs.Tab label={t("Upload files")} className={"space-y-4 pt-2"}>
              <Field
                name={"name"}
                label={t("Name")}
                required
                fullWidth
                value={form.formData.name}
                placeholder={t("Version name. ex: v2")}
                onChange={form.handleInputChange}
              />
              <Field
                name="changelog"
                label={t("Changelog")}
                fullWidth
                placeholder={t("Changelog")}
              >
                <Textarea
                  name={"changelog"}
                  onChange={form.handleInputChange}
                  rows={5}
                >
                  {form.formData.changelog}
                </Textarea>
              </Field>
              <Field name={"files"} label={t("Files")} required>
                <Dropzone
                  onChange={(files) => form.setFieldValue("files", files)}
                  className={"bg-slate-100 h-48"}
                  label={t(
                    "Drag & drop the files from your desktop to create a new version manually.",
                  )}
                />
              </Field>
            </Tabs.Tab>
          </Tabs>
          {form.submitError && (
            <p className={"my-2 text-sm text-red-600"}>{form.submitError}</p>
          )}
        </Dialog.Content>
        <Dialog.Actions>
          <Button
            variant={"outlined"}
            onClick={onClose}
            disabled={form.isSubmitting}
          >
            {t("Close")}
          </Button>
          {tabIndex === 1 && (
            <Button disabled={form.isSubmitting} type={"submit"}>
              {form.isSubmitting ? (
                <>
                  <Spinner className={"mr-2"} size={"xs"} />
                  {t("Creating ({{progress}}%)", { progress })}
                </>
              ) : (
                t("Create")
              )}
            </Button>
          )}
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

UploadDatasetVersionDialog.fragments = {
  datasetLink: gql`
    fragment UploadDatasetVersionDialog_datasetLink on DatasetLink {
      id
      dataset {
        id
        name
        slug
        workspace {
          slug
        }
      }
      workspace {
        slug
      }
    }
  `,
};

export default UploadDatasetVersionDialog;
