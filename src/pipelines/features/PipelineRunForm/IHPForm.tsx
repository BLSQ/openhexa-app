import { PlayIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Checkbox from "core/components/forms/Checkbox";
import Field from "core/components/forms/Field";
import useForm from "core/hooks/useForm";
import { useTranslation } from "next-i18next";

type Form = {
  start_date: string;
  end_date: string;
  generate_extract: boolean;
  update_dhis2: boolean;
  reuse_existing_extract: boolean;
  update_dashboard: boolean;
};

type IHPFormProps = {
  onSubmit?(config: { [key: string]: any }): Promise<void>;
  readOnly?: boolean;
  fromConfig?: { parameters: Form } | null;
};

const IHPForm = (props: IHPFormProps) => {
  const { onSubmit, fromConfig, readOnly } = props;
  const { t } = useTranslation();
  const form = useForm<Form>({
    validate(values) {
      const errors = {} as any;
      if (
        values.start_date &&
        values.end_date &&
        values.start_date >= values.end_date
      ) {
        errors.start_date = t(
          "Enter start and end date. Start date must be before end date.",
        );
      }

      return errors;
    },
    getInitialState() {
      let initialState = {
        generate_extract: false,
        update_dhis2: false,
        update_dashboard: false,
        reuse_existing_extract: false,
      };

      if (fromConfig) {
        initialState = { ...initialState, ...fromConfig.parameters };
      }
      return initialState;
    },

    onSubmit(values) {
      onSubmit ? onSubmit({ parameters: values }) : null;
    },
  });
  return (
    <form onSubmit={form.handleSubmit} className="grid grid-cols-2 gap-4">
      <Field
        name="start_date"
        disabled={readOnly}
        type="date"
        required
        value={form.formData.start_date}
        onChange={form.handleInputChange}
        id="start_date"
        label={t("From date")}
        error={form.touched.start_date && form.errors.start_date}
      />
      <Field
        name="end_date"
        type="date"
        disabled={readOnly}
        required
        value={form.formData.end_date}
        onChange={form.handleInputChange}
        id="end_date"
        label={t("To date")}
        error={form.touched.end_date && form.errors.end_date}
      />

      <Checkbox
        checked={form.formData.generate_extract}
        name="generate_extract"
        disabled={readOnly}
        onChange={form.handleInputChange}
        label={t("Generate extract")}
      />
      <Checkbox
        checked={form.formData.reuse_existing_extract}
        name="reuse_existing_extract"
        disabled={readOnly}
        onChange={form.handleInputChange}
        label={t("Re-use existing extract")}
      />
      <Checkbox
        checked={form.formData.update_dhis2}
        name="update_dhis2"
        disabled={readOnly}
        onChange={form.handleInputChange}
        label={t("Update DHIS2")}
      />
      <Checkbox
        checked={form.formData.update_dashboard}
        name="update_dashboard"
        disabled={readOnly}
        onChange={form.handleInputChange}
        label={t("Update dashboard")}
      />
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

export default IHPForm;
