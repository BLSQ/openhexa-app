import { gql } from "@apollo/client";
import { PlayIcon } from "@heroicons/react/outline";
import Button from "core/components/Button";
import CodeEditor from "core/components/CodeEditor";
import Checkbox from "core/components/forms/Checkbox";
import Field from "core/components/forms/Field";
import useForm from "core/hooks/useForm";
import { useTranslation } from "next-i18next";

type PipelineRunFormProps = {
  onSubmit(dagId: string, config: object): Promise<void>;
  dag: any;
  fromConfig?: object;
};

type Form = {
  textConfig: string;
  config: { [key: string]: any };
};

const CUSTOM_IHP_FORM = ["ihp"];

function PipelineRunForm(props: PipelineRunFormProps) {
  const { onSubmit, dag, fromConfig } = props;
  const { t } = useTranslation();
  const form = useForm<Form>({
    validate(values) {
      const errors = {} as any;
      if (CUSTOM_IHP_FORM !== dag.formCode) {
        try {
          JSON.parse(values.textConfig ?? "");
        } catch {
          errors.config = t("Invalid configuration. This is not a valid JSON.");
        }
      } else {
        if (
          values.config?.start_date >= values.config?.end_date ||
          !(values.config?.start_date && values.config?.end_date)
        ) {
          errors.start_date = t(
            "Enter start and end date. Start date must be before end date."
          );
        }
      }

      return errors;
    },
    async onSubmit(values) {
      if (CUSTOM_IHP_FORM !== dag.formCode) {
        onSubmit(dag.id, JSON.parse(values.textConfig));
      } else {
        onSubmit(dag.id, values.config);
      }
    },
    getInitialState() {
      return {
        textConfig: JSON.stringify(
          fromConfig ?? (dag.template.sampleConfig || {}),
          null,
          2
        ),
        config: fromConfig ?? (dag.template.sampleConfig || {}),
      };
    },
  });

  const setConfigFieldValue = (key: string, value: any) => {
    form.setFieldValue("config", { ...form.formData.config, [key]: value });
  };

  return (
    <form onSubmit={form.handleSubmit} className="grid grid-cols-2 gap-4">
      {CUSTOM_IHP_FORM !== dag.formCode ? (
        <Field
          name="config"
          label={t("Configuration")}
          required
          className="col-span-2"
        >
          <CodeEditor
            height="auto"
            lang="json"
            onChange={(value) => form.setFieldValue("textConfig", value)}
            value={form.formData.textConfig}
          />
        </Field>
      ) : (
        <>
          <Field
            name="start_date"
            type="date"
            required
            value={form.formData.config?.start_date}
            onChange={(e) => setConfigFieldValue("start_date", e.target.value)}
            id="start_date"
            label={t("From date")}
            error={
              (form.touched as any).start_date &&
              (form.errors as any).start_date
            }
          />
          <Field
            name="end_date"
            type="date"
            required
            value={form.formData.config?.end_date}
            onChange={(e) => setConfigFieldValue("end_date", e.target.value)}
            id="end_date"
            label={t("To date")}
            error={
              (form.touched as any).end_date && (form.errors as any).end_date
            }
          />

          <Checkbox
            value={form.formData.config?.generate_extract}
            name="generate_extract"
            onChange={(e) =>
              setConfigFieldValue("generate_extract", e.target.checked)
            }
            label={t("Generate extract")}
          />
          <Checkbox
            value={form.formData.config?.update_dhis2}
            name="update_dhis2"
            onChange={(e) =>
              setConfigFieldValue("update_dhis2", e.target.checked)
            }
            label={t("Update DHIS2")}
          />
          <Checkbox
            value={form.formData.config?.update_dashboard}
            name="update_dashboard"
            onChange={(e) =>
              setConfigFieldValue("update_dashboard", e.target.checked)
            }
            label={t("Update dashboard")}
          />
        </>
      )}
      <div className="col-span-2 text-right">
        <Button
          disabled={!form.isValid}
          type="submit"
          leadingIcon={<PlayIcon className="w-6" />}
        >
          {t("Configure & run")}
        </Button>
      </div>
    </form>
  );
}

PipelineRunForm.fragments = {
  dag: gql`
    fragment PipelineRunForm_dag on DAG {
      template {
        sampleConfig
      }
      formCode
      id
    }
  `,
};

export default PipelineRunForm;
