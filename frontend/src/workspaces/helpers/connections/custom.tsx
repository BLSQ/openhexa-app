import { PlusCircleIcon, XMarkIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button/Button";
import Title from "core/components/Title";
import Checkbox from "core/components/forms/Checkbox/Checkbox";
import Field from "core/components/forms/Field/Field";
import { FormInstance } from "core/hooks/useForm";
import { useTranslation } from "next-i18next";
import { ConnectionForm, FieldForm } from "./utils";

function CustomForm(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  const fields: FieldForm[] = form.formData.fields ?? [];

  const updateField = (index: number, field: FieldForm) => {
    const newFields = [...fields];
    newFields.splice(index, 1, field);
    form.setFieldValue("fields", newFields);
  };

  return (
    <div className="col-span-2 space-y-3">
      <Title level={5}>{t("Fields")}</Title>
      <div className="max-h-56 space-y-3 overflow-y-auto px-px py-px">
        {fields.map((field, index) => (
          <div
            key={index}
            className="flex w-full items-center justify-end gap-2"
          >
            <Field
              className="flex-1"
              onChange={(event) =>
                updateField(index, {
                  ...field,
                  code: event.target.value,
                })
              }
              fullWidth
              value={field.code}
              name={`code-${index}`}
              pattern="^[a-zA-Z0-9-_]*$"
              help={t(
                "Only letters, numbers, dashes and underscores are allowed. 'code' and 'description' are protected words and cannot be used.",
              )}
              placeholder="my-custom-field-1"
              label={t("Field name")}
              required
            />
            <Field
              name={`value-${index}`}
              label={t("Field value")}
              onChange={(event) =>
                updateField(index, {
                  ...field,
                  value: event.target.value,
                })
              }
              fullWidth
              value={field.value ?? ""}
              placeholder={t("Value of the field")}
              required
              className="flex-1"
            />
            <div className="mt-3 flex gap-2">
              <Checkbox
                id={`secret-${index}`}
                className="mt-1"
                name={`secret_${index}`}
                onChange={(event) =>
                  updateField(index, {
                    ...field,
                    secret: event.target.checked,
                  })
                }
                checked={field.secret ?? false}
                label={t("Secret")}
              />
              <button
                type="button"
                onClick={() =>
                  form.setFieldValue(
                    "fields",
                    form.formData.fields.filter(
                      (_: any, i: number) => i !== index,
                    ),
                  )
                }
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <Button
        variant="white"
        size="sm"
        type="button"
        data-testid="add-field"
        onClick={() => form.setFieldValue("fields", [...fields, {}])}
        leadingIcon={<PlusCircleIcon className="h-4 w-4" />}
      >
        {t("Add a field")}
      </Button>
    </div>
  );
}

export default {
  label: "Custom",
  color: "bg-gray-200",
  iconSrc: "/images/cog.svg",
  Form: CustomForm,
  fields: [],
  validate(fields: { [key: string]: any }) {
    const errors = {} as any;
    Object.keys(fields).forEach((key) => {
      if (["code", "description"].includes(key)) {
        // I don't know yet why but trying to make the translation work here makes the i18n:extract to fail
        errors[key] =
          `"${key}" is a protected word and cannot be used as a field name.`;
      }
    });
    return errors;
  },
};
