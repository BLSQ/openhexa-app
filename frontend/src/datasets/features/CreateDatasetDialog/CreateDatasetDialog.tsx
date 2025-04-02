import { gql, useMutation } from "@apollo/client";
import { useTranslation } from "next-i18next";
import Dialog from "core/components/Dialog";
import Button from "core/components/Button";
import useForm from "core/hooks/useForm";
import Field from "core/components/forms/Field";
import Textarea from "core/components/forms/Textarea";
import { CreateDatasetDialog_WorkspaceFragment } from "./CreateDatasetDialog.generated";
import { useRouter } from "next/router";
import { CreateDatasetError } from "graphql/types";

type CreateDatasetDialogProps = {
  workspace: CreateDatasetDialog_WorkspaceFragment;
  onClose(): void;
  open: boolean;
};

const CreateDatasetDialog = (props: CreateDatasetDialogProps) => {
  const { open, workspace, onClose } = props;
  const { t } = useTranslation();
  const [createDataset] = useMutation(gql`
    mutation CreateDatasetDialog($input: CreateDatasetInput!) {
      createDataset(input: $input) {
        dataset {
          id
          slug
        }
        link {
          id
        }
        success
        errors
      }
    }
  `);
  const router = useRouter();
  const form = useForm<{ name: string; description: string }>({
    onSubmit: async (values) => {
      const { data } = await createDataset({
        variables: {
          input: {
            name: values.name,
            description: values.description,
            workspaceSlug: workspace.slug,
          },
        },
      });

      if (data?.createDataset.success) {
        await router.push({
          pathname: `/workspaces/[workspaceSlug]/datasets/[datasetSlug]`,
          query: {
            workspaceSlug: workspace.slug,
            datasetSlug: data.createDataset.dataset.slug,
          },
        });
      } else if (
        data?.createDataset.errors.includes(CreateDatasetError.PermissionDenied)
      ) {
        throw new Error(t("You are not authorized to perform this action"));
      } else if (
        data?.createDataset.errors.includes(
          CreateDatasetError.WorkspaceNotFound,
        )
      ) {
        throw new Error(t("Workspace not found"));
      } else {
        throw new Error(t("Unknown error"));
      }
    },
    validate(values) {
      const errors: any = {};
      if (!values.name) {
        errors.name = t("Name is required");
      }
      if (!values.description) {
        errors.description = t("Description is required");
      }
      return errors;
    },
  });

  return (
    <Dialog open={open} onClose={onClose}>
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title onClose={onClose}>{t("Create a dataset")}</Dialog.Title>
        <Dialog.Content className="space-y-4">
          <Field
            name={"name"}
            label={t("Name")}
            value={form.formData.name}
            onChange={form.handleInputChange}
            required
            fullWidth
            error={form.errors.name}
          />
          <Field name={"description"} label={t("Description")} required>
            <Textarea
              value={form.formData.description}
              onChange={form.handleInputChange}
              name={"description"}
              placeholder={t("Description")}
              error={form.errors.description}
            />
          </Field>
        </Dialog.Content>
        <Dialog.Actions>
          <Button onClick={onClose} variant={"outlined"}>
            {t("Cancel")}
          </Button>
          <Button disabled={form.isSubmitting} type="submit">
            {t("Create")}
          </Button>
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

CreateDatasetDialog.fragments = {
  workspace: gql`
    fragment CreateDatasetDialog_workspace on Workspace {
      slug
      name
      permissions {
        createDataset
      }
    }
  `,
};

export default CreateDatasetDialog;
