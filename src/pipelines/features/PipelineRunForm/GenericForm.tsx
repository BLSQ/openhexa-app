import { PlayIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import CodeEditor from "core/components/CodeEditor";
import Field from "core/components/forms/Field";
import useForm from "core/hooks/useForm";
import { useTranslation } from "next-i18next";

type GenericFormProps = {
  onSubmit?(config: { [key: string]: any }): Promise<void>;
  fromConfig?: object | null;
  readOnly?: boolean;
};

type Form = {
  textConfig: string;
};

const GenericForm = (props: GenericFormProps) => {
  const { onSubmit, fromConfig, readOnly } = props;
  const { t } = useTranslation();
  const form = useForm<Form>({
    validate(values) {
      const errors = {} as any;
      try {
        JSON.parse(values.textConfig ?? "");
      } catch {
        errors.textConfig = t(
          "Invalid configuration. This is not a valid JSON.",
        );
      }

      return errors;
    },
    async onSubmit(values) {
      onSubmit && onSubmit(JSON.parse(values.textConfig));
    },
    getInitialState() {
      return {
        textConfig: fromConfig ? JSON.stringify(fromConfig, null, 2) : "{}",
      };
    },
  });

  return (
    <form onSubmit={form.handleSubmit} className="grid grid-cols-2 gap-4">
      <Field
        name="config"
        label={t("Configuration")}
        required
        error={form.errors.textConfig}
        readOnly={readOnly}
        className="col-span-2"
      >
        <CodeEditor
          height="auto"
          minHeight="auto"
          lang="json"
          readonly={readOnly}
          editable={!readOnly}
          onChange={(value) => form.setFieldValue("textConfig", value)}
          value={form.formData.textConfig}
        />
      </Field>

      {!readOnly && (
        <div className="col-span-2 text-right">
          <Button
            disabled={form.isSubmitting}
            type="submit"
            leadingIcon={<PlayIcon className="w-4" />}
          >
            {t("Run")}
          </Button>
        </div>
      )}
    </form>
  );
};

export default GenericForm;
