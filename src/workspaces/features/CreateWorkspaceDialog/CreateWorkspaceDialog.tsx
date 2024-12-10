import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Spinner from "core/components/Spinner";
import CountryPicker from "core/features/CountryPicker";
import { CountryPicker_CountryFragment } from "core/features/CountryPicker/CountryPicker.generated";
import useForm from "core/hooks/useForm";
import { useEffect } from "react";
import { useTranslation } from "next-i18next";
import { useCreateWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import { useRouter } from "next/router";
import { CreateWorkspaceError } from "graphql/types";
import Checkbox from "core/components/forms/Checkbox/Checkbox";
import useCacheKey from "core/hooks/useCacheKey";

type CreateWorkspaceDialogProps = {
  onClose(): void;
  showCancel?: boolean;
  open: boolean;
};

type Form = {
  name: string;
  country: CountryPicker_CountryFragment;
  loadSampleData: boolean;
};

const CreateWorkspaceDialog = (props: CreateWorkspaceDialogProps) => {
  const router = useRouter();
  const [mutate] = useCreateWorkspaceMutation();
  const clearCache = useCacheKey(["workspaces"]);

  const { t } = useTranslation();
  const { open, onClose, showCancel = true } = props;
  const form = useForm<Form>({
    onSubmit: async (values) => {
      const { data } = await mutate({
        variables: {
          input: {
            name: values.name,
            countries: values.country
              ? [{ code: values.country.code }]
              : undefined,
            loadSampleData: values.loadSampleData,
          },
        },
      });

      if (!data?.createWorkspace) {
        throw new Error("Unknown error.");
      }

      if (
        data.createWorkspace.errors.includes(
          CreateWorkspaceError.PermissionDenied,
        )
      ) {
        throw new Error("You are not authorized to perform this action");
      } else {
        clearCache();
        onClose();
        await router.push({
          pathname: "/workspaces/[workspaceSlug]",
          query: { workspaceSlug: data?.createWorkspace.workspace?.slug },
        });
      }
    },
    validate: (values) => {
      const errors = {} as any;

      if (!values.name) {
        errors.name = t("Type a workspace name");
      }
      return errors;
    },
    initialState: {
      name: "",
      loadSampleData: false,
    },
  });

  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  return (
    <Dialog onSubmit={form.handleSubmit} open={open} onClose={onClose}>
      <Dialog.Title>{t("Create a workspace")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Field
          name="name"
          required
          data-testid="name"
          label={t("Workspace name")}
          value={form.formData.name}
          onChange={form.handleInputChange}
          autoComplete="off"
          fullWidth
        />

        <Field
          name="country"
          label={t("Country")}
          help={t("Add the country flag to the workspace")}
        >
          <CountryPicker
            withPortal
            value={form.formData.country}
            onChange={(value) => form.setFieldValue("country", value)}
          />
        </Field>

        {form.submitError && (
          <div className="text-danger mt-3 text-sm">{form.submitError}</div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <div className="flex flex-1 items-center">
          <Checkbox
            checked={form.formData.loadSampleData}
            name="loadSampleData"
            onChange={form.handleInputChange}
            label={t("Add tutorial content")}
            help={t(
              "Enabling this option will import tutorial content in your new workspace",
            )}
          />
        </div>
        {showCancel && (
          <Button variant="white" onClick={onClose}>
            {t("Cancel")}
          </Button>
        )}
        <Button disabled={form.isSubmitting} type="submit">
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Create")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default CreateWorkspaceDialog;
