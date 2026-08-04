import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Spinner from "core/components/Spinner";
import useForm from "core/hooks/useForm";
import { useEffect } from "react";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { CreateOrganizationError } from "graphql/types";
import { useCreateSelfHostedOrganizationMutation } from "organizations/graphql/mutations.generated";

type CreateOrganizationDialogProps = {
  open: boolean;
  onClose(): void;
};

type Form = {
  name: string;
  shortName: string;
};

const CreateOrganizationDialog = ({
  open,
  onClose,
}: CreateOrganizationDialogProps) => {
  const router = useRouter();
  const { t } = useTranslation();
  const [mutate] = useCreateSelfHostedOrganizationMutation({
    refetchQueries: ["Organizations"],
  });

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const { data } = await mutate({
        variables: {
          input: {
            name: values.name,
            shortName: values.shortName || undefined,
          },
        },
      });

      const result = data?.createSelfHostedOrganization;
      if (!result) {
        throw new Error("Unknown error.");
      }

      if (result.errors.includes(CreateOrganizationError.PermissionDenied)) {
        throw new Error(t("You are not authorized to perform this action"));
      }
      if (result.errors.includes(CreateOrganizationError.NameDuplicate)) {
        throw new Error(t("An organization with this name already exists"));
      }
      if (result.errors.includes(CreateOrganizationError.InvalidShortName)) {
        throw new Error(
          t("The short name must be at most 5 uppercase letters"),
        );
      }
      if (!result.success || !result.organization) {
        throw new Error(t("Failed to create the organization"));
      }

      onClose();
      await router.push({
        pathname: "/organizations/[organizationId]",
        query: { organizationId: result.organization.id },
      });
    },
    validate: (values) => {
      const errors = {} as any;
      if (!values.name) {
        errors.name = t("Type an organization name");
      }
      if (values.shortName && !/^[A-Z]{1,5}$/.test(values.shortName)) {
        errors.shortName = t(
          "The short name must be at most 5 uppercase letters",
        );
      }
      return errors;
    },
    initialState: {
      name: "",
      shortName: "",
    },
  });

  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  return (
    <Dialog onSubmit={form.handleSubmit} open={open} onClose={onClose}>
      <Dialog.Title>{t("Create an organization")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Field
          name="name"
          required
          data-testid="name"
          label={t("Organization Name")}
          value={form.formData.name}
          onChange={form.handleInputChange}
          error={form.touched.name && form.errors.name}
          autoComplete="off"
          fullWidth
        />
        <Field
          name="shortName"
          label={t("Short Name")}
          help={t(
            "Optional. Up to 5 uppercase letters. Auto-generated if left empty.",
          )}
          value={form.formData.shortName}
          onChange={form.handleInputChange}
          error={form.touched.shortName && form.errors.shortName}
          autoComplete="off"
          fullWidth
        />

        {form.submitError && (
          <div className="text-danger mt-3 text-sm">{form.submitError}</div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button disabled={form.isSubmitting} type="submit">
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Create")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default CreateOrganizationDialog;
