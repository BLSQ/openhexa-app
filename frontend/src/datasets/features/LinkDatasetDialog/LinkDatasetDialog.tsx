import { gql, useMutation } from "@apollo/client";
import Dialog from "core/components/Dialog";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button";
import WorkspacePicker from "workspaces/features/WorkspacePicker";
import { useEffect } from "react";
import useForm from "core/hooks/useForm";
import {
  LinkDatasetDialogMutation,
  LinkDatasetDialogMutationVariables,
} from "datasets/features/LinkDatasetDialog/LinkDatasetDialog.generated";
import { LinkDatasetError } from "graphql/types";
import Field from "core/components/forms/Field";
import useCacheKey from "core/hooks/useCacheKey";

type LinkDatasetDialogProps = {
  dataset: any;
  open: boolean;
  onClose: () => void;
};

const LinkDatasetDialog = ({
  dataset,
  open,
  onClose,
}: LinkDatasetDialogProps) => {
  const { t } = useTranslation();
  const [linkDataset] = useMutation<
    LinkDatasetDialogMutation,
    LinkDatasetDialogMutationVariables
  >(gql`
    mutation LinkDatasetDialog($input: LinkDatasetInput!) {
      linkDataset(input: $input) {
        success
        errors
        link {
          workspace {
            slug
          }
          id
        }
      }
    }
  `);
  const clearCache = useCacheKey(["datasets"]);
  const form = useForm<{ workspace: any }>({
    async onSubmit(values) {
      const { data } = await linkDataset({
        variables: {
          input: {
            datasetId: dataset.id,
            workspaceSlug: values.workspace.slug,
          },
        },
      });
      if (data?.linkDataset.success && data.linkDataset.link) {
        clearCache();
        onClose();
      } else if (
        data?.linkDataset.errors.includes(LinkDatasetError.AlreadyLinked)
      ) {
        throw new Error(
          t("This dataset is already shared with this workspace"),
        );
      } else if (
        data?.linkDataset.errors.includes(LinkDatasetError.PermissionDenied)
      ) {
        throw new Error(t("You don't have permission to share this dataset"));
      } else {
        throw new Error(t("An error occurred while sharing this dataset"));
      }
    },
    validate(values) {
      const errors: any = {};
      if (!values.workspace) {
        errors.workspace = t("You have to select a workspace");
      }
      return errors;
    },
  });

  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  return (
    <Dialog open={open} onClose={onClose} centered={false}>
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title>
          {t("Share '{{name}}' with a workspace", { name: dataset.name })}
        </Dialog.Title>
        <Dialog.Content className={"space-y-4"}>
          <p>
            {t(
              "The members of the workspace will be able to view and download this dataset.",
            )}
          </p>
          <Field
            name={"workspace"}
            label={t("Workspace")}
            required
            error={form.touched.workspace && form.errors.workspace}
          >
            <WorkspacePicker
              value={form.formData.workspace}
              onChange={(value) => form.setFieldValue("workspace", value)}
            />
          </Field>
          {form.submitError && (
            <p className={"text-sm text-red-500"}>{form.submitError}</p>
          )}
        </Dialog.Content>
        <Dialog.Actions>
          <Button variant={"outlined"} onClick={onClose}>
            {t("Cancel")}
          </Button>
          <Button disabled={form.isSubmitting} type="submit">
            {t("Share")}
          </Button>
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

LinkDatasetDialog.fragments = {
  dataset: gql`
    fragment LinkDatasetDialog_dataset on Dataset {
      id
      name
    }
  `,
};

export default LinkDatasetDialog;
