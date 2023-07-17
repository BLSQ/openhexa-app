import { gql } from "@apollo/client";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Textarea from "core/components/forms/Textarea";
import Switch from "core/components/Switch";
import useForm from "core/hooks/useForm";
import { ConnectionField } from "graphql-types";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { ConnectionFieldDialog_FieldFragment } from "./ConnectionFieldDialog.generated";

type onSaveFn = (
  field: Pick<ConnectionField, "code" | "value" | "secret"> & {
    [key: string]: any;
  }
) => void;

type ConnectionFieldDialogProps = {
  onClose(): void;
  onSave: onSaveFn;
  open: boolean;
  field?: ConnectionFieldDialog_FieldFragment;
};

const ConnectionFieldDialog = (props: ConnectionFieldDialogProps) => {
  const { t } = useTranslation();
  const { open, onClose, onSave, field } = props;
  const form = useForm<{
    code: string;
    value: string;
    secret: boolean;
  }>({
    async onSubmit(values) {
      await onSave({
        code: values.code,
        value: values.value,
        secret: values.secret,
      });
      onClose();
      form.resetForm();
    },
    getInitialState: () => ({
      code: field?.code ?? "",
      value: field?.value ?? "",
      secret: field?.secret ?? false,
    }),
    validate(values) {
      const errors = {} as any;
      if (!values.code) {
        errors.code = t("Type a slug for the field");
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
    <Dialog open={open} onClose={onClose}>
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title>
          {field
            ? t("Update connection's field")
            : t("Create a connection field")}
        </Dialog.Title>
        <Dialog.Content className="space-y-4">
          <Field
            label={t("Name")}
            onChange={form.handleInputChange}
            readOnly={Boolean(field)}
            disabled={Boolean(field)}
            value={form.formData.code}
            placeholder={t("FIELD_SLUG")}
            name="code"
            pattern="^[a-zA-Z0-9-_]*$"
            help={t("Only alphanumerics characters, hyphens and underscores")}
            required
          />
          <Field label={t("Value")} name="value">
            <Textarea
              name="value"
              rows={4}
              className="w-full"
              value={form.formData.value}
              onChange={form.handleInputChange}
            />
          </Field>
          {!field && (
            <Field name="secret" label={t("Secret value")} required>
              <Switch
                checked={Boolean(form.formData.secret)}
                onChange={(checked) => form.setFieldValue("secret", checked)}
              />
            </Field>
          )}
          {form.submitError && (
            <p className={"my-2 text-sm text-red-600"}>{form.submitError}</p>
          )}
        </Dialog.Content>
        <Dialog.Actions>
          <Button type="button" variant="white" onClick={onClose}>
            {t("Cancel")}
          </Button>
          <Button type="submit">{t("Save")}</Button>
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

ConnectionFieldDialog.fragments = {
  field: gql`
    fragment ConnectionFieldDialog_field on ConnectionField {
      code
      value
      secret
    }
  `,
};

export default ConnectionFieldDialog;
